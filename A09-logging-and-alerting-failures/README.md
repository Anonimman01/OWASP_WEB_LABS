🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A09 — Security Logging and Alerting Failures

**Status:** ✅ ready

## About the lab
An attack is noticed too late if security events are not written to the log, if there are no alerts on them, or if the log itself is unreliable: it can be forged, read by an outsider, and it contains passwords and sessions. The lab has six such defects in one small application.

## What you will learn
- What should be logged: logins (successful and failed), access denials, significant actions
- How to prevent log injection and not write secrets to the log
- How to build alerts: counters, thresholds, a time window
- How to protect the log itself: access, audit, a hash chain to detect tampering

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8081 |
| fixed | http://127.0.0.1:8082 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
PORT=8081 python vulnerable/app.py   # http://127.0.0.1:8081
```

In a browser `/` opens the `/ui` page with forms for all endpoints. You can do the same with `curl` (on Windows: Git Bash/WSL or `curl.exe`).

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

## Task
Test accounts: `alice` / `alice123` and `bob` / `bob123` (ordinary users), `admin` (you do not need the password). `POST /reset-lab` resets the lab data. The `/_lab/tamper` endpoint is a lab helper: it imitates an attacker who has access to the log storage.

1. Brute-force `bob`'s password: make at least 10 failed logins, then log in correctly. Find the traces of the brute force in `GET /logs`. Then open `GET /alerts` (the flag appears if nobody noticed the attack).
2. Log in as `alice` and request `GET /admin/export` (it will be 403). Is the denial left in the log?
3. Forge a log entry about a login of a user who never existed, through `POST /feedback`. Check the result in `GET /logs/summary` (the flag).
4. Get administrator access **without guessing the password** and without hacking the application: what you already know how to read is enough (the flag is in `GET /admin/export`).
5. Make a transfer with `POST /transfer` and look for an entry about it in the log.
6. With `POST /_lab/tamper` delete the line with your login from the log. Is there a way in the application to notice this?
7. Repeat everything on `fixed` (port 8082). There you play both the attacker and the defender: the logs and alerts are readable only by the administrator, so log in as `admin` (take the password from `fixed/app.py`) and look at `GET /alerts`, `GET /logs` and `GET /logs/verify`.

## Endpoints

```
POST /login                  {"username","password"}
GET  /me
POST /transfer               {"to","amount"}
POST /feedback               {"name","message"}
GET  /admin/export
GET  /logs
GET  /logs/summary           (fixed: admin only)
GET  /logs/verify            (fixed only: hash chain check)
GET  /alerts
POST /_lab/tamper            {"index","text"}   helper: editing the log storage
POST /reset-lab
```

## Hints

<details>
<summary>Hint 1 — what is visible in the log</summary>

Make several logins, including wrong ones, then open `GET /logs`. How many lines appeared? Which events are in them and which are missing?
</details>

<details>
<summary>Hint 2 — a line break</summary>

The log is plain text, one entry per line. What happens if a line break character (`\n` in JSON) ends up in `message`?
</details>

<details>
<summary>Hint 3 — what else is in the log</summary>

Read the lines about the administrator's login carefully. Does everything in them need to be stored?
</details>

<details>
<summary>Hint 4 — who looks at the alerts</summary>

Where in the application is the threshold after which someone learns about the brute force? Compare `GET /alerts` in vulnerable and in fixed.
</details>

<details>
<summary>Hint 5 — can the log be trusted</summary>

If an attacker deleted a line, how can you tell? Look at what each entry stores in fixed and what `GET /logs/verify` does.
</details>

## What to compare in fixed/
Open `fixed/app.py` and find the `# FIX N` comments: the number matches the number of the defect in `vulnerable/app.py`.

## Structure
- `vulnerable/` — the vulnerable version
- `fixed/` — the fixed version
- `SOLUTION.md` — the walkthrough (with spoilers)
- `docker-compose.yml` — runs both versions

## Further reading
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP Cheat Sheet: Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [OWASP: Log Injection](https://owasp.org/www-community/attacks/Log_Injection)
- [OWASP Cheat Sheet: Application Logging Vocabulary](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Vocabulary_Cheat_Sheet.html)
