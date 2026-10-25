🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A10 — Solution walkthrough (spoilers)

Examples: `curl` against `http://127.0.0.1:8091` (vulnerable) and `http://127.0.0.1:8092` (fixed). On Windows, Git Bash or WSL (or `curl.exe` in PowerShell) is more convenient. The texts printed by the application itself are left in Russian, as in the real output; an English gloss is given in parentheses.

## Defect 1 — verbose errors in the response

A non-numeric `month` causes an unhandled exception. The "debug" error handler gives the client everything:

```bash
curl -s "http://127.0.0.1:8091/report?month=abc"
# {"config": {"database": "sqlite:///:memory:", "env": "production",
#             "internal_api_key": "FLAG{a10_verbose_errors}"},
#  "error": "invalid literal for int() with base 10: 'abc'",
#  "trace": ["Traceback (most recent call last):",
#            "  File \"/usr/local/lib/python3.12/site-packages/flask/app.py\", line 917, in full_dispatch_request", ...]}
```

The response contains the language and framework version, file paths and lines of code, and also the internal configuration with a key. For an attacker this is a ready-made map of the application.

**Rule:** to the client: a short neutral message and an `error_id`. The stack trace, the configuration and the details stay in the server log, and debug modes are switched off in production.

**Fix:** a single handler returns `{"error": "внутренняя ошибка сервера", "error_id": "..."}` (internal server error), and the stack trace is written to the log under this `error_id` (`# FIX 1`). An expected input error (`month` is not a number) is handled by the application itself and answered with 400.

## Defect 2 — fail-open in the access check

Document `3` is "corrupted": `level` holds the text `TOP`, not a number. The access check catches any error and in that case allows access:

```bash
curl -s -c a.txt -X POST http://127.0.0.1:8091/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
for i in 1 2 3 4; do curl -s -b a.txt http://127.0.0.1:8091/documents/$i; echo; done
# 1: {"content": "Сегодня: борщ и плов.", ...}   (today: borscht and pilaf)
# 2: {"error": "недостаточно прав"}   (not enough rights)
# 3: {"content": "FLAG{a10_fail_open} — бюджет на следующий год", ...}   <- should be closed!  (next year's budget)
# 4: {"error": "недостаточно прав"}
```

Here `int("TOP")` raises `ValueError`, and `except Exception: return True` turns the failure into a permission. In real systems such an error appears with corrupted data, an unavailable policy service, a timeout or unexpected input.

**Rule:** when an access check fails, the default answer is "no" (fail-closed). The error is logged, so that the cause can be found and fixed.

**Fix:** `except` returns `False` and writes to the log which check failed (`# FIX 2`). In fixed, document `3` is closed to everyone until the data is corrected.

## Defect 3 — a partially executed operation

An order of three mugs: there are two in stock. The application first charges the money and only then looks at the stock:

```bash
curl -s -b a.txt http://127.0.0.1:8091/me
# {"balance": 100, ...}
curl -s -b a.txt -X POST http://127.0.0.1:8091/orders -H 'Content-Type: application/json' -d '{"item_id":1,"qty":3}'
# {"error": "на складе осталось 2, а нужно 3", "type": "RuntimeError", "trace": [...], "config": {...}}   (500)
# (2 left in stock, 3 needed)
curl -s -b a.txt http://127.0.0.1:8091/me
# {"balance": 40, ...}
curl -s http://127.0.0.1:8091/_lab/consistency
# {"flag": "FLAG{a10_partial_operation}", "money_lost": {"alice": 60}, "note": "деньги списаны, а заказов на эти суммы нет"}
# (money was charged, and there are no orders for these amounts)
```

60 was charged, there is no order. Every SQL statement was saved at once (autocommit), and there is nothing to roll back "half" of the operation.

**Rule:** an operation of several steps is executed atomically: all or nothing. That is a transaction, and in distributed systems compensating actions (saga) and idempotency.

**Fix:** the whole operation sits inside `BEGIN IMMEDIATE` … `COMMIT`, with `ROLLBACK` on any error (`# FIX 3`). The order of steps is left the same as in vulnerable, to make it visible that the point is precisely the transaction. In fixed the same order gives 409, the balance stays 100, and `/_lab/consistency` shows `{"money_lost": {}}`.

## Defect 4 — no limits

A normal request: an 800×600 image. But there is no upper bound:

```bash
curl -s -X POST http://127.0.0.1:8091/thumbnail -H 'Content-Type: application/json' -d '{"width":800,"height":600}'
# {"estimated_mb": 1.83, "ok": true}
curl -s -X POST http://127.0.0.1:8091/thumbnail -H 'Content-Type: application/json' -d '{"width":20000,"height":20000}'
# {"error": "сервис упал: не хватило памяти"}   (500)   (the service crashed: out of memory)
curl -s -b a.txt http://127.0.0.1:8091/me
# {"error": "сервис недоступен"}   (503)   (the service is unavailable)
curl -s http://127.0.0.1:8091/health
# {"flag": "FLAG{a10_no_limits}", "status": "crashed", ...}   (503)
curl -s -X POST http://127.0.0.1:8091/reset-lab
```

20000×20000 pixels is almost 1.5 GB at 4 bytes per pixel. The crash is imitated in the lab, but in real life it is the OOM killer, a hung process and a service unavailable to everyone. Separately, there is no limit on the size of the request itself and no timeouts for long-running work.

**Rule:** we check the bounds of input data **before** spending resources: the request body size, the sizes and number of elements, the nesting depth, the execution time (timeouts), the request rate (rate limit).

**Fix:** `MAX_CONTENT_LENGTH` (8 KB, Flask answers 413 itself), an allowed side of 1–2048 pixels and a memory estimate check before processing (`# FIX 4`). The same request gets 413, and the service keeps working.

## Defect 5 — the raw exception text in the response

There is no `q2` report, and `archive` is "broken" (a directory in place of the file). The application returns `str(e)`:

```bash
curl -s http://127.0.0.1:8091/reports/q1
# {"name": "q1", "text": "Отчёт за 1 квартал: выручка выросла на 4%.\n"}   (Q1 report: revenue grew by 4%.)
curl -s http://127.0.0.1:8091/reports/q2
# {"error": "[Errno 2] No such file or directory: '/tmp/a10v_v0oz0vii/q2.txt'"}
curl -s http://127.0.0.1:8091/reports/archive
# {"error": "[Errno 21] Is a directory: '/tmp/a10v_v0oz0vii/archive.txt'"}
```

The error texts reveal the operating system (the path `/tmp/...`, or `C:\Users\<name>\AppData\...` on Windows), the directory where the data lives, and the logic of the application.

**Rule:** the exception message is meant for the developer, not for the user. Expected situations ("no file") are handled with a meaningful response, unexpected ones are passed to the single handler.

**Fix:** `FileNotFoundError` is handled separately and gives a neutral "отчёт не найден" (report not found) (`# FIX 5`), everything else goes to the single handler and is returned with an `error_id`.

## Checking fixed

```bash
curl -s "http://127.0.0.1:8092/report?month=abc"
# {"error": "month должен быть числом от 1 до 12"}   (400)   (month must be a number from 1 to 12)
curl -s http://127.0.0.1:8092/reports/archive
# {"error": "внутренняя ошибка сервера", "error_id": "1d6406c3"}   (500; the stack trace only in the server console)
curl -s -c b.txt -X POST http://127.0.0.1:8092/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
curl -s -b b.txt http://127.0.0.1:8092/documents/3
# {"error": "недостаточно прав"}   (403)
curl -s -b b.txt -X POST http://127.0.0.1:8092/orders -H 'Content-Type: application/json' -d '{"item_id":1,"qty":3}'
# {"error": "недостаточно товара на складе"}   (409)   (not enough stock)
curl -s -b b.txt http://127.0.0.1:8092/me
# {"balance": 100, ...}
curl -s -X POST http://127.0.0.1:8092/thumbnail -H 'Content-Type: application/json' -d '{"width":20000,"height":20000}'
# {"error": "допустимая сторона: от 1 до 2048 пикселей"}   (413)   (allowed side: 1 to 2048 pixels)
curl -s http://127.0.0.1:8092/reports/q2
# {"error": "отчёт не найден"}   (404)
```

Legitimate scenarios work as before: `alice` reads document `1`, `bob` reads document `2`, an ordinary order of one mug goes through, an 800×600 image is processed. Look for the details of every hidden error in the server console by `error_id`.

## Summary

| № | Defect | How it is shown | What is in fixed |
|---|--------|-----------------|------------------|
| 1 | Verbose errors | A stack trace and a config with a key in the response to `?month=abc` | A single handler: `error_id` to the client, details to the log |
| 2 | Fail-open | A corrupted `level` opened a secret document | Fail-closed: a check failure means denial and a log entry |
| 3 | No rollback | 60 charged, no order | A transaction: `ROLLBACK` on error, the balance does not change |
| 4 | No limits | One 20000×20000 request "crashes" the service | A limit on the body and sizes, 413 before allocating resources |
| 5 | Raw exception text | A server file path in the response | Neutral messages, details only in the log |
