🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A05 — Injection

**Status:** ✅ ready

## About the lab
A mini web shop with login, product search, a search results page and a guestbook. User input gets into SQL queries and into HTML without processing, so it can be turned into code: **SQL injection** and **XSS** (reflected and stored).

## What you will learn
- To understand how user data changes the meaning of an SQL query
- To bypass a login and extract other people's data with SQL injection (on a learning application)
- To see the difference between reflected and stored XSS
- To defend: parameterized queries, output escaping, CSP

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8041 |
| fixed | http://127.0.0.1:8042 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

## Task
Test account: `alice` / `alice123`. The `/search` and `/guestbook` pages are easier to open in a browser.

1. Log in as `admin` **without knowing the password** (`POST /login`).
2. Through the product search (`GET /products?q=...`) show a product that is hidden from ordinary customers.
3. Through the same search extract the administrator's secret (a `FLAG{...}` flag) from the `users` table.
4. Make the `/search?q=...` page run your script (reflected XSS), then do the same through the guestbook (stored XSS). `alert(1)` is enough for the check.
5. Repeat everything against the **fixed** version and explain why it does not work.
6. Compare `vulnerable/app.py` and `fixed/app.py`: the fixes are marked `FIX`.

## Hints
1. What happens if you put a single quote `'` into the username? Do you see an SQL error?
2. In SQL `--` starts a comment. What could you comment out in the login query?
3. The search query has the condition `hidden = 0`. How can you neutralize it?
4. `UNION SELECT` adds rows from another table, but the number of columns must match the original query.
5. For XSS, look at how the message gets into the HTML page.

Full solution with spoilers: [SOLUTION.md](./SOLUTION.md)

## How to defend
- **SQL:** parameterized queries (`?` and passing the values separately), not string concatenation
- **XSS:** escape data when outputting into HTML, use template engines with auto-escaping
- **Defense in depth:** the `Content-Security-Policy` header, limits on input length and format, minimal privileges for the database account
- Do not show database error messages to the user
