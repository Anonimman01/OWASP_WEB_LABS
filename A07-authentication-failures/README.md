🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A07 — Authentication Failures

**Status:** ✅ ready

## About the lab
A mini service with registration, login, "remember me" and password change.
The code contains no SQL injection or XSS — all seven defects of this lab are
in how sessions, tokens and checks are built in authentication: a weak
password policy, user enumeration, no brute-force protection, session
fixation, a "cosmetic" logout, a predictable "remember me" token, and a
password change without re-entering the current password.

## What you will learn
- To tell authentication (who you are) from authorization (what you are allowed to do)
- To see why a session must be reissued at login (session fixation)
- That logout must be a server-side operation, not just deleting the cookie in the browser
- To assess the entropy and unpredictability of "remember me" tokens
- To require re-confirmation of identity before sensitive actions

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8061 |
| fixed | http://127.0.0.1:8062 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
PORT=8061 python vulnerable/app.py   # http://127.0.0.1:8061
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

## Task

Test accounts: `alice` / `alice-Good-Pass1`, `bob` / `123456` (the password is
weak on purpose — it got through registration because the password policy
allowed it), `admin` / `Adm1n-Str0ng-Pass!2025` (the password is strong on
purpose — this account cannot be broken by brute force). It is convenient to
work with `curl`, saving cookies (`-c cookies.txt -b cookies.txt`).
`POST /reset-lab` resets the lab data.

1. **The "remember me" token.** Get access to `GET /admin` (and the flag)
   without knowing the `admin` password, using only the `remember_token`
   cookie.
2. **Session fixation.** Get the same access another way: through a `sid`
   that you obtained before anyone logged in as `admin`.
3. **Logout.** Log in, remember the value of the `sid` cookie, log out — and
   show that the same value can still be used.
4. **Enumeration + brute force.** From the response of `POST /login`,
   determine which logins exist at all, then brute-force `bob`'s password
   with a short dictionary, without any delays or lockouts.
5. **Account takeover.** With any active session of someone else (for example
   from items 1–3), change the victim's password through
   `POST /change-password` without knowing their current password.

## Endpoints

```
POST /register           {"username","password"}
POST /login               {"username","password","remember":true|false}
POST /logout
GET  /auto-login          login by the remember_token cookie
GET  /me
GET  /admin
POST /change-password     {"new_password"}   (in fixed also "current_password")
POST /reset-lab
```

## Hints

<details>
<summary>Hint 1 — remember_token</summary>

On `POST /login` with `"remember": true` the server sets the
`remember_token` cookie. What is it computed from — a random secret or
something you can compute yourself knowing only the login?
</details>

<details>
<summary>Hint 2 — session fixation</summary>

Open `GET /`. The server already gives you a `sid` cookie — before you have
even logged in. What happens to this same `sid` value if you now do
`POST /login` as another user?
</details>

<details>
<summary>Hint 3 — logout</summary>

`POST /logout` answers `{"ok": true}` and explicitly deletes the cookies in
the response. But deleting a cookie in the browser is not the same as
destroying the session record on the server. Save the `sid` value separately
before logging out and try to use it afterwards.
</details>

<details>
<summary>Hint 4 — enumeration and brute force</summary>

Compare the code and the text of the `POST /login` response for a
nonexistent login and for an existing login with a wrong password. And then:
how many times in a row can you call `/login` before the server says
"enough"?
</details>

<details>
<summary>Hint 5 — password change</summary>

`POST /change-password` requires only an active session. Look at which
fields this request accepts at all — is there anything about the old
password?
</details>

## What to compare in fixed/

Open `fixed/app.py` and find the `# FIX N` comments — each corresponds to the
defect with the same number in `vulnerable/app.py`.

## Structure
- `vulnerable/` — the vulnerable version
- `fixed/` — the fixed version
- `SOLUTION.md` — the walkthrough (with spoilers)
- `docker-compose.yml` — runs both versions

## Further reading
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — section V3: Session Management, section V2: Authentication
- [OWASP Web Security Testing Guide — Testing for Authentication](https://owasp.org/www-project-web-security-testing-guide/)
