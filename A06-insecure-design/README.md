🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A06 — Insecure Design

**Status:** ✅ ready

## About the lab
A mini web shop (JSON API) with neat code but broken business logic: the price comes from the client, quantity and coupons are unlimited, the order steps can be skipped, and the password reset code can be brute-forced. There is no "one dangerous line" here: this can only be fixed by changing the design.

## What you will learn
- To see business logic vulnerabilities that a scanner will not find
- Not to trust the client with money and process state
- To model a process as a state machine and threats as abuse cases
- To protect one-time codes: attempt limit, lifetime, cryptographically strong randomness

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8051 |
| fixed | http://127.0.0.1:8052 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
PORT=8051 python vulnerable/app.py   # http://127.0.0.1:8051
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

## Task
Test accounts: `alice` / `alice123` (balance $100) and `bob` / `S3cr3t-b0b-pass` (balance $10,000). It is convenient to work with `curl`, Postman or Burp (JSON). `POST /reset-lab` resets the lab data.

1. Order the "Gift set" (`product_id: 3`, $5000) while paying less than $1 for it, and get the flag at `/orders/<id>/ship`.
2. Increase alice's balance without selling anything.
3. Get an order shipped **without paying for it**.
4. Take over the `bob` account through the password reset (the code "arrives" in the log: `docker compose logs vulnerable`) and explain why the server is not protected against brute force.
5. For every defect you find, state the *architectural* rule that was violated, then compare with `fixed/` (the `# FIX N` comments).

## Endpoints

```
POST /login                  {"username","password"}
GET  /me
GET  /products
POST /orders                 {"items":[{"product_id","quantity"}],"coupons":[...]}
GET  /orders/<id>
POST /orders/<id>/pay
POST /orders/<id>/ship
POST /password-reset/request {"username"}
POST /password-reset/confirm {"username","otp","new_password"}
POST /reset-lab
```

## Hints

<details>
<summary>Hint 1 — price</summary>

The client sends JSON with the items of the order. Look carefully at which fields
`POST /orders` accepts for each item: does that match what the server normally
decides (the catalog) and what the client decides (the quantity)?
</details>

<details>
<summary>Hint 2 — quantity</summary>

What happens to the order total if `quantity` is negative? And if it is very
large?
</details>

<details>
<summary>Hint 3 — coupons</summary>

The `coupons` field is a list. What if you pass the same code in it several
times?
</details>

<details>
<summary>Hint 4 — order of steps</summary>

The `/pay` and `/ship` endpoints are separate, independent calls. Do they have
to be called in that order?
</details>

<details>
<summary>Hint 5 — paying again</summary>

Can you call `/orders/<id>/pay` twice for the same order? What if the order has
a negative total (see hint 2)?
</details>

<details>
<summary>Hint 6 — password reset</summary>

`POST /password-reset/request` "sends" a code — look at the server log
(`docker compose logs vulnerable`) to see how many digits it has. How many
requests to `/password-reset/confirm` does it take to try every option, and
does the server limit their number?
</details>

## Structure
- `vulnerable/` — the vulnerable version
- `fixed/` — the fixed version
- `SOLUTION.md` — the walkthrough (with spoilers)
- `docker-compose.yml` — runs both versions

## Further reading
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — section V1: architecture, design and threat modeling
