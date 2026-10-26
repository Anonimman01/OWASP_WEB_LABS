🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# OWASP Top 10:2025: hands-on labs

Ten local hands-on labs, one for each category of the **[OWASP Top 10:2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)**.
The format is **break it → fix it**: every lab starts two versions of the same application side by side, a vulnerable one and a fixed one. You find the flaws in the first, then compare it with the second to see exactly how each hole was closed.

The documentation of every lab is available in English, Russian and Uzbek (Latin script); this README is available in the same three languages (see [Languages](#languages)). License: MIT.

> ⚠️ **Important.** The applications in this repository are **intentionally vulnerable**.
> - Run them only locally (`127.0.0.1`) or in an isolated environment (Docker, a virtual machine).
> - **Never expose them to the internet.** The ports in `docker-compose.yml` are bound to `127.0.0.1` for exactly this reason.
> - Apply what you learn only to your own systems or to systems where you have explicit permission to test.
> - All data in the labs is fictional: users, passwords, card numbers and secrets.

## Contents

- [Lab list](#lab-list)
- [Quick start](#quick-start)
- [How to work through a lab](#how-to-work-through-a-lab)
- [Structure of each lab](#structure-of-each-lab)
- [Common conventions](#common-conventions)
- [Languages](#languages)
- [Solutions and spoilers](#solutions-and-spoilers)
- [Troubleshooting](#troubleshooting)
- [Useful links](#useful-links)

## Lab list

Ports are listed as **vulnerable / fixed**. All addresses look like `http://127.0.0.1:<port>`.
Lab documentation (README and SOLUTION) is in English, Russian and Uzbek; the folder links below open the English version, and each file has links to the other languages at the top.

| №   | Lab | Category | What is inside | Ports |
|-----|-----|----------|----------------|-------|
| A01 | [broken-access-control](./A01-broken-access-control) | Broken Access Control | A corporate HR portal with roles: the server does not check who owns a resource or what role the user has | 8001 / 8002 |
| A02 | [security-misconfiguration](./A02-security-misconfiguration) | Security Misconfiguration | A cafe website (Flask): default password, extra exposed files, verbose errors, no security headers | 8011 / 8012 |
| A03 | [software-supply-chain-failures](./A03-software-supply-chain-failures) | Software Supply Chain Failures | A harmless app with outdated pinned dependencies; `fixed/` shows the `requirements.in` approach | 8021 / 8022 |
| A04 | [cryptographic-failures](./A04-cryptographic-failures) | Cryptographic Failures | Accounts and bank cards: weak cryptography, taking over the administrator account | 8031 / 8032 |
| A05 | [injection](./A05-injection) | Injection (SQLi, XSS, etc.) | A shop with login, search and a guestbook; input reaches SQL and HTML unprocessed | 8041 / 8042 |
| A06 | [insecure-design](./A06-insecure-design) | Insecure Design | A shop JSON API with clean code but broken business logic | 8051 / 8052 |
| A07 | [authentication-failures](./A07-authentication-failures) | Authentication Failures | Registration, login, "remember me", password change | 8061 / 8062 |
| A08 | [software-or-data-integrity-failures](./A08-software-or-data-integrity-failures) | Software or Data Integrity Failures | Unsigned cookie, license, mirror update and webhook | 8071 / 8072 |
| A09 | [logging-and-alerting-failures](./A09-logging-and-alerting-failures) | Security Logging and Alerting Failures | The attack is invisible in the logs: missing records, log injection, secrets in the log, no alerts | 8081 / 8082 |
| A10 | [mishandling-of-exceptional-conditions](./A10-mishandling-of-exceptional-conditions) | Mishandling of Exceptional Conditions | Verbose errors, fail-open, operations without rollback, no limits | 8091 / 8092 |

Status: ✅ all ten labs are ready.

## Quick start

### What you need

- Git
- Docker with the Compose plugin **or** Python 3.11+ (without Docker)
- For `curl` commands: on Windows use Git Bash, WSL or `curl.exe`. In PowerShell `curl` is an alias for a different command, so the examples from the labs will not work there as they are.

### Run with Docker

Bash / Git Bash / WSL:

```bash
git clone https://github.com/Anonimman01/my-labs.git
cd my-labs/A01-broken-access-control
docker compose up --build
```

PowerShell:

```powershell
git clone https://github.com/Anonimman01/my-labs.git
cd my-labs\A01-broken-access-control
docker compose up --build
```

Both versions (vulnerable and fixed) start at the same time on the ports from the table above. To stop: `Ctrl+C`, then `docker compose down`.

### Run without Docker

You need Python 3.11+. A virtual environment is recommended. The port is set with the `PORT` variable (default `5000`).

Bash / Git Bash / WSL:

```bash
cd my-labs/A09-logging-and-alerting-failures
python -m venv .venv && source .venv/bin/activate
pip install -r vulnerable/requirements.txt
PORT=8081 python vulnerable/app.py     # http://127.0.0.1:8081
```

PowerShell:

```powershell
cd my-labs\A09-logging-and-alerting-failures
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r vulnerable\requirements.txt
$env:PORT = 8081
python vulnerable\app.py               # http://127.0.0.1:8081
```

To run the fixed version, replace `vulnerable` with `fixed` (and the port with `8082`). The two versions may have different dependencies, so install the `requirements.txt` of the version you are running. In A03 the Flask versions differ on purpose: `vulnerable/` uses an outdated one.

## How to work through a lab

1. Open the lab's `README.md` and read what it is about and which test accounts it has.
2. Start the lab and open the `vulnerable` address. In a browser, `/` redirects to the `/ui` page with forms for all endpoints; A01 and A02 open their own application (a portal and a cafe site) instead, and the `/ui` console is linked from there. The same requests can be sent with `curl` or Postman.
3. Complete the items in the "Task" section. If you get stuck, expand the hints in `<details>`.
4. In `vulnerable/app.py` the flaws are marked with `# ДЕФЕКТ N` comments (Russian for "DEFECT N"). Find them and state the rule that was violated.
5. Open `fixed/app.py`: the fixes are marked `# FIX N`, and the number matches the number of the flaw. Repeat the same requests against `fixed` and confirm that the attack no longer works while normal scenarios still do.
6. Only after that read `SOLUTION.md`.

## Structure of each lab

```
AXX-category-name/
  README.md              description, task, endpoints, hints (English)
  README.ru.md           Russian translation
  README.uz.md           Uzbek translation
  SOLUTION.md            walkthrough (with spoilers, English)
  SOLUTION.ru.md         Russian translation
  SOLUTION.uz.md         Uzbek translation
  Dockerfile             python:3.11-slim, ARG VARIANT, ENV HOST=0.0.0.0 PORT=5000
  docker-compose.yml     two services (vulnerable and fixed), ports on 127.0.0.1
  vulnerable/
    app.py               vulnerable version
    labui.py             the /ui learning interface
    requirements.txt
  fixed/
    app.py               fixed version
    labui.py
    requirements.txt
```

Some labs have extra files: for example `wordlist.txt` in A04, `backup.sql` in A02's `vulnerable/`, `requirements.in` in A03's `fixed/`. A02 also ships its site files: `templates/`, `static/` and `cafe.py` in each version.

## Common conventions

- **Stack.** Flask, usually a JSON API. The address and port come from the `HOST` and `PORT` environment variables (default `127.0.0.1:5000`).
- **The `/ui` page.** A learning wrapper, not part of the vulnerability. It is built from the list of Flask routes, so it is the same for both versions. If you see JSON in the browser instead, open `/ui` manually.
- **Flags.** Responses of `vulnerable` contain strings like `FLAG{aNN_...}`. They confirm that the flaw was found and exploited.
- **Resetting state.** Labs A06–A10 have `POST /reset-lab`, which restores the initial data. In the other labs, restart the application to reset the state.
- **Helper endpoints.** Routes that simulate the actions of an attacker or an external system (for example the update mirror in A08) are labelled in the code as lab helpers and are not part of the vulnerability.
- **Cookies.** `vulnerable` and `fixed` use different cookie names, because different ports on `127.0.0.1` share one cookie jar in the browser.
- **Passwords.** For simplicity they are stored in plain text. Proper password storage is covered by lab A04.
- **No weaponized exploits.** The labs demonstrate each flaw on a safe example, without ready-made exploitation such as RCE through deserialization.

## Languages

- **This README** is available in English (`README.md`), Russian (`README.ru.md`) and Uzbek (`README.uz.md`). Each file has a language switcher on its first line.
- **Lab documentation** (A01–A10) is available in English (`README.md`, `SOLUTION.md`), Russian (`README.ru.md`, `SOLUTION.ru.md`) and Uzbek, Latin script (`README.uz.md`, `SOLUTION.uz.md`). Each file has a language switcher on its first line.
- **The `/ui` page** of every lab is available in English (the default), Russian and Uzbek, with an **EN / RU / UZ** switcher in the top right corner. The choice is remembered in the browser, and it can also be set in the address bar by appending `?lang=ru` or `?lang=uz` (if the address ends with `/ui`) or `/ui?lang=ru` / `/ui?lang=uz` (if it does not), for example `http://127.0.0.1:8041/ui?lang=uz`. A browser with an Uzbek locale opens the Uzbek version right away.
- Only the interface shell is translated (headings, buttons, hints, examples). The applications' own responses (note texts, product names, error messages) are left as they are so that they match `SOLUTION`. Code comments (`# ДЕФЕКТ N` / `# FIX N`) stay in Russian.

## Solutions and spoilers

For every flaw, the `SOLUTION.md` of each lab gives the commands, the violated rule and a description of the fix, followed by a summary. Read it after your own attempt.

## Troubleshooting

- **Port already in use.** Stop the other lab or change the left-hand port in `docker-compose.yml` (for example `127.0.0.1:9001:5000`). Without Docker, set a different `PORT`.
- **Cookies "stick" between labs.** Open the page in a private window or clear the cookies for `127.0.0.1`.
- **`curl` behaves strangely in PowerShell.** Use `curl.exe`, Git Bash or WSL.
- **Docker does not start.** Check that Docker Desktop is running and that the `docker compose` command is available (not only `docker-compose`).

## Useful links

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) and the [Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) for deeper study

## License

[MIT](./LICENSE)
