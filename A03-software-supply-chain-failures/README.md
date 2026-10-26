🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A03 — Software Supply Chain Failures

**Status:** ✅ ready

## About the lab

**Kestrel CI** is the site of a fictional SaaS for building and shipping releases: a landing page, pricing, documentation, a builds page and a package registry. The interface works in **English, Russian and Uzbek** (an EN / RU / UZ switcher in the header). The lab has two parts:

1. **Integrity inside the application.** The server believes whatever the build sends it: the artifact digest is never recomputed, the signature is never checked, the build profile is deserialized as code, CI events are trusted without a signature, and package names resolve through two indexes at once. Four defects with flags live here.
2. **Dependencies.** `vulnerable/requirements.txt` deliberately pins old versions with known vulnerabilities, including transitive ones. `fixed/` shows the right approach: `requirements.in`, a lock file with hashes and an install with `--require-hashes`.

## What you will learn

- To compute a digest from the content on the server side and compare it with a pinned value
- To sign artifacts (HMAC) and verify the signature before deploying
- Why data must never be parsed with unsafe deserializers (`pickle`) and what that leads to
- To verify webhook signatures and reject unsigned events
- To pin versions **and hashes** of dependencies (a lock file) and to keep names out of the public index
- To check dependencies for known vulnerabilities (`pip-audit`) and to produce an SBOM

## The site

| Page | Address | Note |
|------|---------|------|
| Home | `/` | A browser gets the site; `curl` gets a short JSON description of the API |
| Pricing | `/pricing` | Three plans and what every plan includes |
| Docs | `/docs` | Quick start, the `kestrel.yml` format, the signing formula, the endpoint table |
| Builds | `/builds` | Runs with artifact digests, forms for a release, a build profile and a webhook |
| Registry | `/registry` | The internal index and the public mirror, plus an install form |
| Lab console | `/ui` | Endpoint list, ready-made requests, server responses |
| Package versions | `/deps` | JSON with the versions of the installed dependencies |

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable (integrity defects + old dependencies) | http://127.0.0.1:8021 |
| fixed (checks in place + updated dependencies with hashes) | http://127.0.0.1:8022 |

Both versions serve the same site — only `app.py` differs. Open http://127.0.0.1:8021/ and use the site as an ordinary visitor. Without Docker:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

The lab project key that signs releases and webhooks is `kestrel-lab-project-key` (it is also shown on the `/docs` page). It sits in the code on purpose: without it there would be nothing to verify.

> ⚠️ The application is vulnerable on purpose. Run it locally only and never publish it to the internet.

## Tasks

### Part 1. Integrity inside the application

Find **four** integrity flaws in the vulnerable version (each one hides a flag):

1. Publish a release whose digest does not match the artifact body, with no signature at all. Did the server accept it? Did it recompute the digest itself?
2. Send a base64 blob of a serialized object as a build profile instead of JSON. What happened **before** the server read the first field of the profile?
3. Send a CI event to `/webhooks/ci` without the `X-Kestrel-Signature` header. What happened to the build, and what does that mean for anyone who knows the address?
4. Install the package `kestrel-utils` first without a version and then pinned to `1.4.2`. Which index served the package in each case, and was its digest compared with the one pinned in the lock file?

Repeat all four on the fixed version (port 8022) and state exactly what changed there. The flaws are marked in `vulnerable/app.py` with `# ДЕФЕКТ N` comments (Russian for "DEFECT N").

### Part 2. Dependencies

1. Install the tool: `pip install pip-audit`
2. Check the vulnerable version: `pip-audit -r vulnerable/requirements.txt`
3. Find out which packages are vulnerable and up to which versions they must be updated. Which of them did you **not** list in the project directly?
4. Check the fixed version with the same command: `pip-audit -r fixed/requirements.txt`
5. Open `fixed/requirements.in` and `fixed/requirements.txt`. How do they differ and why are hashes needed?
6. Experiment: copy `fixed/requirements.txt`, replace any hash with zeros and try `pip install --require-hashes -r <file>`. What happens?

## Hints

1. Every request has a form on `/builds` and `/registry`, so part of the work can be done in a browser. For curl, JSON is easier: `curl -X POST http://127.0.0.1:8021/api/releases -H 'Content-Type: application/json' -d '{...}'`.
2. A release signature is the HMAC-SHA256 of the digest string with the project key. There is a Python example on the `/docs` page.
3. A build profile arrives as base64 of whatever `pickle` can parse. What happens next depends on what the object carries.
4. The "Public mirror" table on `/registry` shows which packages come from the external index. Look at the digests: they differ from the internal ones.
5. `pip-audit` prints the package name, the version, the advisory id and the version where the problem is fixed.
6. `requests` pulls in `urllib3`, `idna` and `certifi`, while `Flask` pulls in `Werkzeug` and `Jinja2`.

Full solution with spoilers: [SOLUTION.md](./SOLUTION.md)

## How to defend

- Compute the digest from the content on the server side and compare it with a pinned value; sign releases and verify the signature before rolling out
- Never parse incoming data with unsafe deserializers (`pickle`, `marshal`, `yaml.load`): use JSON, schemas and validation
- Require a signature from webhooks, compare it in constant time and reject events without one
- Resolve package names from the internal index only, pin versions **and hashes** in the lock file, and do not treat the public index as an equal source
- Check dependencies regularly (`pip-audit`, Dependabot and similar), keep them updated and maintain an SBOM
