🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A10 — Mishandling of Exceptional Conditions

**Status:** ✅ ready

## About the lab
Every application breaks sometimes: unexpected data arrives, dependencies fail, resources run out. The question is **how** it breaks. Here are five wrong responses to a failure: show the client everything about yourself, allow "just in case", abandon the operation halfway, not limit a request by size, and dump the exception text.

## What you will learn
- The fail-closed (fail-secure) principle: when an access check fails, access is denied
- To make operations atomic: a transaction and rollback instead of "half" of an action
- To return a neutral error with an `error_id` to the client and keep the details in the log
- To check the sizes and bounds of input data before allocating resources
- To tell expected errors (handled on the merits) from unexpected ones (a single handler)

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8091 |
| fixed | http://127.0.0.1:8092 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
PORT=8091 python vulnerable/app.py   # http://127.0.0.1:8091
```

In a browser `/` opens the `/ui` page with forms for all endpoints. You can do the same with `curl` (on Windows: Git Bash/WSL or `curl.exe`).

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

## Task
Test accounts: `alice` / `alice123` (access level 1) and `bob` / `bob123` (level 2). Both start with a balance of 100. `POST /reset-lab` resets the lab data and "brings up" a crashed service. `GET /_lab/consistency` is a lab helper: it reconciles charges and orders.

1. Cause an error in `GET /report` so that the server shows more than it should: what exactly do you see in the response? (the flag is in the response)
2. Log in as `alice` and read document `3`, although she has no rights to it (the flag is in the content). Documents `2` and `4` are closed to her, but `3` somehow opened. Why?
3. Order three mugs (`POST /orders`, `item_id: 1`, `qty: 3`). What happens to your balance? Check `GET /_lab/consistency` (the flag).
4. Take the service down with **one** request to `POST /thumbnail`, then confirm it through `GET /health` (the flag).
5. Open the reports `GET /reports/q1`, `/reports/q2` and `/reports/archive`. What do you learn about the server from the error texts?
6. Repeat everything on `fixed` (port 8092) and compare the responses and behavior. Look at the server console: it keeps details that are not in the responses.

## Endpoints

```
POST /login                  {"username","password"}
GET  /me
GET  /documents/<id>
GET  /report?month=<1-12>
GET  /items
POST /orders                 {"item_id","qty"}
POST /thumbnail              {"width","height"}
GET  /reports/<name>
GET  /health
GET  /_lab/consistency       (helper: reconciling charges and orders)
POST /reset-lab
```

## Hints

<details>
<summary>Hint 1 — what is in the error response</summary>

Pass something that is not a number in `month`. Read the whole response: besides the error itself there are two more fields. What is in them and who could find that useful?
</details>

<details>
<summary>Hint 2 — a document with a "quirk"</summary>

Every document has a `level` field. Compare documents `2`, `3` and `4`: how does document `3` differ from the others, and what does the access check do if it cannot compare the values?
</details>

<details>
<summary>Hint 3 — the order of steps</summary>

In what sequence does `POST /orders` charge the money, check the stock and create the order? What is left in the database if it fails between the first and the second step?
</details>

<details>
<summary>Hint 4 — request size</summary>

The service has "64 MB available", and an image needs 4 bytes per pixel. Which `width` and `height` values does the application check before allocating memory?
</details>

<details>
<summary>Hint 5 — three reports, three errors</summary>

Compare the error texts for `q2` (the file does not exist) and `archive` (there is a directory in place of the file). What do they have in common and how is that useful to someone studying the server?
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
- [OWASP Cheat Sheet: Error Handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
- [OWASP: Improper Error Handling](https://owasp.org/www-community/Improper_Error_Handling)
- [CWE-636: Not Failing Securely ("Failing Open")](https://cwe.mitre.org/data/definitions/636.html)
