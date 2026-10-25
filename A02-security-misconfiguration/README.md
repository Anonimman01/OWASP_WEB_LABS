🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A02 — Security Misconfiguration

**Status:** ✅ ready

## About the lab
A small web shop (API) with typical configuration mistakes: a default password, unnecessary exposed files, verbose errors and missing security headers. There is no exploit code here: the vulnerabilities are exactly the **wrong settings**.

## What you will learn
- To find insecure settings in an application
- Why verbose errors and forgotten files (`.env`, backups) are dangerous
- To configure security HTTP headers and expose only what is needed

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8011 |
| fixed | http://127.0.0.1:8012 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

## Task
Find **four** configuration mistakes in the vulnerable version (each hides a flag or a telltale sign):

1. Log in as the administrator without knowing the password.
2. Get the application's secret data without having access to the server.
3. Make the application give out extra technical information.
4. Check the HTTP response headers: which security headers are missing and what extra does the server reveal?

Then repeat the checks against the fixed version. The admin password in fixed is generated at startup: `docker compose logs fixed` (or set your own through the `ADMIN_PASSWORD` variable).

## Hints
1. Which login and password are often left as the "default"?
2. What does the `GET /files/<name>` route do, and which files sit next to `app.py`?
3. What does `GET /items?id=abc` return?
4. Use `curl -i` to see the headers.

Full solution with spoilers: [SOLUTION.md](./SOLUTION.md)

## How to defend
- Change default passwords, keep secrets in the environment and not in files next to the code
- Serve only a static directory, not the application root
- Show the user a neutral error and write the details to the server log
- Add security headers and remove version banners
- Check the configuration regularly with automated scanners
