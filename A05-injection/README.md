🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A05 — Injection

**Status:** ✅ ready

## About the lab
The website of the fictional airline **Skyline**: flight search, results, a flight page with booking, "My trips", login/registration and an admin area with an airport-node check tool. The interface is multilingual (EN / RU / UZ, switcher in the header). User input reaches SQL queries and a shell command, so it can be turned into code: **SQL injection** and **command injection**.

## What you will learn
- To understand how user data changes the meaning of an SQL query
- To bypass a login, reveal hidden data and extract other users' records with SQL injection (on a learning application)
- To see why string concatenation near `os.popen` is dangerous
- To defend: parameterized queries, input allowlists, no shell

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
pip install -r vulnerable/requirements.txt   # for fixed: fixed/requirements.txt
python vulnerable/app.py                     # http://127.0.0.1:5000
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.
> The admin node check uses `ping` (Linux/macOS/Docker) — on Windows the normal check shows an error, but the command injection exercise still works there with `&` instead of `;`.

## Task
Test account: `alice` / `alice123`. The site pages are easier to open in a browser: the lab console is at `/ui`.

1. Log in as `admin` **without knowing the password** (`POST /login`). The admin's `/me` contains a flag.
2. Through the flight search (`GET /flights?from=...&to=...`) show the **charter flight** that is hidden from ordinary passengers, open it and find its flag.
3. Through the same search, extract the administrator's secret (a `FLAG{...}` flag) from the `users` table.
4. Get administrator rights (use step 1) and run your own command through the airport-node check (`POST /admin/check`) to read the flag from the server environment.
5. Repeat everything against the **fixed** version and explain why it does not work.
6. Compare `vulnerable/app.py` and `fixed/app.py`: the fixes are marked `FIX`.

## Hints
1. What happens if you put a single quote `'` into the username? Do you see an SQL error?
2. In SQL `--` starts a comment. What could you comment out in the login query?
3. The search query has the condition `hidden = 0`. How can you neutralize it?
4. `UNION SELECT` adds rows from another table, but the number of columns must match the original query (count the columns in `SELECT`).
5. The node check builds a command from the host field. Which shell separator (`;` on Linux/macOS, `&` on Windows) lets you run an extra command, and where is the flag stored in the process?

Full solution with spoilers: [SOLUTION.md](./SOLUTION.md)

## How to defend
- **SQL:** parameterized queries (`?` and passing the values separately), not string concatenation
- **Commands:** never build a shell command from user input — use argument lists without a shell and validate values against an allowlist (e.g. `^[A-Za-z0-9.-]+$`)
- **Depth:** do not show database error messages to the user, limit input length and format, keep the database account's privileges minimal
- Treat every input (HTTP parameters, headers, filenames) as untrusted data, never as code
