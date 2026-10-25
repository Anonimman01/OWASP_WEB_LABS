🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A04 — Cryptographic Failures

**Status:** ✅ ready

## About the lab
A service with accounts and linked bank cards (all data is fictional, the card numbers are test ones). Security is built on cryptography, but done with mistakes: weak password storage, predictable tokens, a weak session key, card data stored unencrypted.

## What you will learn
- To tell secure password storage (scrypt, bcrypt, Argon2 with a salt) from insecure (unsalted MD5)
- Why predictable tokens and weak secret keys are dangerous
- To encrypt sensitive data and not expose it unnecessarily
- To keep secrets out of the source code

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8031 |
| fixed | http://127.0.0.1:8032 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt   # for fixed: fixed/requirements.txt
python vulnerable/app.py                     # http://127.0.0.1:5000
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.
> The lab has no HTTPS, to keep the setup simple. In a real system all traffic must go over TLS and cookies must have the `Secure` flag.

## Task
Test accounts: `alice` / `sunshine`, `bob` / `qwerty`. Each has a linked card.

The helper endpoints `GET /_lab/dump` (imitates a database leak) and `GET /_lab/outbox` (imitates a mailbox) exist for learning only.

1. Imagine the database has leaked: open `/_lab/dump`. In what form are the passwords and card numbers stored?
2. Use the `wordlist.txt` dictionary to recover the passwords of `alice` and `bob` from their hashes. Does it work for `admin`?
3. Get administrator rights (the admin's `/me` contains a flag) in **two ways**:
   - through a password reset (`POST /reset-request`, `POST /reset/<token>`);
   - through the session cookie.
4. Repeat all the steps against the **fixed** version and explain why they do not work.
5. Compare `vulnerable/app.py` and `fixed/app.py`: the fixes are marked `FIX`.

## Hints
1. How many characters does the password hash have and which algorithm is it? Is there a "salt" in it?
2. Request a password reset for yourself and look at the link in `/_lab/outbox`. How is the token related to your name?
3. The session cookie is signed with a secret key. What if the key is too simple?
4. What does `GET /cards` return?

Full solution with spoilers: [SOLUTION.md](./SOLUTION.md)

## How to defend
- Passwords: scrypt, bcrypt or Argon2 with a unique salt, never MD5 or SHA-1
- Tokens: only a cryptographically strong generator (`secrets`), store a hash, limit the lifetime, make them single-use
- Secret keys: long random values from the environment or a secrets manager
- Sensitive data: encrypt at rest, show it masked, do not return more than needed
- All traffic over HTTPS only
