🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A08 — Software or Data Integrity Failures

**Status:** ✅ ready

## About the lab
The application accepts code and data whose authenticity nobody has verified: user state in a cookie, a "signed" license, an update from a mirror, a payment system notification and a script from a third-party CDN. If an attacker can change such data "on the way" or in storage, the application will do their bidding.

## What you will learn
- To tell a checksum (hash) from a real signature (HMAC / asymmetric signature)
- Not to keep trusted state on the client side without a signature
- To verify the integrity of updates and dependencies (lock files, pinned hashes, signatures)
- To verify the authenticity of webhooks: signature, freshness, replay
- To include third-party scripts with SRI

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8071 |
| fixed | http://127.0.0.1:8072 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
PORT=8071 python vulnerable/app.py   # http://127.0.0.1:8071
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

## Task
Test accounts: `alice` / `alice123` (an ordinary user) and `admin` (you do not need the password). It is convenient to work with `curl` (on Windows: Git Bash/WSL or `curl.exe`) and short Python scripts. `POST /reset-lab` resets the lab data. The `/mirror/publish` and `/cdn/compromise` endpoints are lab helpers: they imitate an attacker who has gained access to the update mirror and to the CDN.

1. Log in as `alice` and get access to `GET /admin` **without knowing the admin password**.
2. Buy the `basic` plan (`POST /buy`) and get access to `GET /pro` **without paying for pro**.
3. Through the auto-update (`POST /system/run-update`) replace `payout_account` in the settings with the attacker's account (the flag appears in `GET /settings`).
4. Make order `1001` paid (`GET /orders/1001` will show the key) **without paying**.
5. Open `GET /donate` in a browser, then `POST /cdn/compromise` and reload the page: which payment details does the victim see now? What changed in fixed?

## Endpoints

```
POST /login                  {"username","password"}
GET  /me
GET  /admin
POST /buy                    {"plan":"basic"}
GET  /pro
POST /system/run-update      cron imitation: auto-update from the mirror
POST /mirror/publish         {"package","version","content":{}}   (helper: "hacking" the mirror)
GET  /settings
GET  /orders/<id>
POST /webhook/payment        {"order_id","status","amount"}
GET  /donate                 an HTML page with a third-party script
POST /cdn/compromise         (helper: "hacking" the CDN)
POST /reset-lab
```

## Hints

<details>
<summary>Hint 1 — the cookie after login</summary>

Log in and look at the `a08v_profile` cookie. Does it look like base64? What happens if you decode it, change one field and encode it back?
</details>

<details>
<summary>Hint 2 — the license cookie</summary>

The `a08v_license` cookie has a "signature" after the dot. What is it computed with? Does it need a secret that only the server knows?
</details>

<details>
<summary>Hint 3 — the update mirror</summary>

What does `/system/run-update` check before applying a package from the mirror? And which settings fields is a package allowed to change at all?
</details>

<details>
<summary>Hint 4 — the webhook</summary>

Who other than the payment system can send a POST to `/webhook/payment`? How does the server tell a real notification from a fake?
</details>

<details>
<summary>Hint 5 — SRI</summary>

Look at the HTML of the `/donate` page in vulnerable and in fixed (the page source). How do the `<script>` tags differ?
</details>

## What to compare in fixed/
Open `fixed/app.py` and find the `# FIX N` comments: the number matches the number of the defect in `vulnerable/app.py`.

## Structure
- `vulnerable/` — the vulnerable version
- `fixed/` — the fixed version
- `SOLUTION.md` — the walkthrough (with spoilers)
- `docker-compose.yml` — runs both versions

## Further reading
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP Cheat Sheet: Deserialization](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- [SLSA](https://slsa.dev/) and [Sigstore](https://www.sigstore.dev/) — signing and provenance of artifacts
- [MDN: Subresource Integrity](https://developer.mozilla.org/docs/Web/Security/Subresource_Integrity)
