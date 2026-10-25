🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A03 — Software Supply Chain Failures

**Status:** ✅ ready

## About the lab
The application itself is harmless: it only shows the versions of the installed packages. The problem is in its **dependencies**: `vulnerable/requirements.txt` deliberately pins old versions with known vulnerabilities, including transitive dependencies (what comes along with `requests` and `Flask`).

## What you will learn
- To check dependencies for known vulnerabilities (`pip-audit`)
- What transitive dependencies are and why they need checking too
- To pin package versions and **hashes** (a lock file) and install them with `--require-hashes`
- To get an SBOM (a bill of materials) of a project

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable (old dependencies) | http://127.0.0.1:8021 |
| fixed (updated + hashes) | http://127.0.0.1:8022 |

The `GET /deps` endpoint shows the versions of the installed packages.

> ⚠️ An application with deliberately outdated dependencies. Run it locally only and do not expose it to the internet.

## Task
1. Install the tool: `pip install pip-audit`
2. Check the vulnerable version: `pip-audit -r vulnerable/requirements.txt`
3. Find out which packages are vulnerable and to which versions they must be updated. Which of them did you **not** list in the project directly?
4. Check the fixed version with the same command: `pip-audit -r fixed/requirements.txt`
5. Open `fixed/requirements.in` and `fixed/requirements.txt`. How do they differ and why are the hashes needed?
6. Experiment: copy `fixed/requirements.txt`, replace any hash with zeros and try `pip install --require-hashes -r <file>`. What happens?

## Hints
1. `pip-audit` prints the package name, the version, the advisory number and the version in which the problem is fixed.
2. `requests` pulls in `urllib3`, `idna` and `certifi`, and `Flask` pulls in `Werkzeug` and `Jinja2`.
3. Versions in projects like this go stale quickly: new advisories appear all the time, so the check has to be repeated.

Full solution with spoilers: [SOLUTION.md](./SOLUTION.md)

## How to defend
- Check dependencies regularly (`pip-audit`, Dependabot, similar tools) and update them
- Keep a lock file with hashes and install with `--require-hashes`
- Maintain an SBOM to know what the product consists of
- Take packages only from trusted sources and watch the names (typos in a package name and public packages replacing internal ones)
