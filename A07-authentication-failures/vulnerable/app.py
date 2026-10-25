"""
A07:2025 Authentication Failures — УЯЗВИМАЯ версия.

Семь независимых дефектов аутентификации в одном маленьком приложении:
1. Слабая парольная политика при регистрации
2. Перечисление пользователей через разные сообщения об ошибке входа
3. Нет защиты от перебора пароля (brute force)
4. Session fixation — ID сессии не меняется после входа
5. Logout не инвалидирует сессию на сервере
6. Токен «запомнить меня» — предсказуемая функция от имени пользователя
7. Смена пароля не требует текущего пароля

Только для локального запуска!
"""
import hashlib
import os
from functools import wraps

from flask import Flask, Response, jsonify, request

app = Flask(__name__)

USERS = {}      # username -> {"password","role"}
SESSIONS = {}   # sid -> {"user": str | None}


def reset_state():
    USERS.clear()
    SESSIONS.clear()
    USERS["alice"] = {"password": "alice-Good-Pass1", "role": "user"}
    # ДЕФЕКТ 1 (последствие): слабый пароль прошёл регистрацию, потому что
    # политика паролей ничего не проверяла
    USERS["bob"] = {"password": "123456", "role": "user"}
    USERS["admin"] = {"password": "Adm1n-Str0ng-Pass!2025", "role": "admin"}


reset_state()


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def get_or_create_sid():
    """Возвращает sid текущего запроса, создавая анонимную сессию при визите."""
    sid = request.cookies.get("sid")
    if sid and sid in SESSIONS:
        return sid, False
    import secrets
    new_sid = secrets.token_hex(8)
    SESSIONS[new_sid] = {"user": None}
    return new_sid, True


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        sid = request.cookies.get("sid")
        sess = SESSIONS.get(sid)
        if not sess or not sess.get("user"):
            return jsonify(error="сначала войдите: POST /login"), 401
        user = USERS.get(sess["user"])
        return f(sess["user"], user, *args, **kwargs)
    return wrapper


@app.get("/")
def index():
    sid, created = get_or_create_sid()
    html = """<h1>A07 Authentication Failures — vulnerable</h1>
<p>API: curl / Burp / Postman. Куки sid и remember_token выставляются автоматически.</p>
<pre>
POST /register           {"username","password"}
POST /login               {"username","password","remember":true|false}
POST /logout
GET  /auto-login          вход по cookie remember_token
GET  /me
GET  /admin
POST /change-password     {"new_password"}
POST /reset-lab
</pre>"""
    resp = Response(html, mimetype="text/html")
    if created:
        resp.set_cookie("sid", sid)
    return resp


@app.post("/reset-lab")
def reset_lab():
    reset_state()
    resp = jsonify(ok=True)
    resp.delete_cookie("sid")
    resp.delete_cookie("remember_token")
    return resp


@app.post("/register")
def register():
    d = body()
    username, password = d.get("username"), d.get("password")
    if not username or username in USERS:
        return jsonify(error="имя занято или не указано"), 400
    # ДЕФЕКТ 1: пароль не проверяется вообще — подходит "", "1", "123456"
    USERS[username] = {"password": str(password or ""), "role": "user"}
    return jsonify(ok=True)


@app.post("/login")
def login():
    d = body()
    username, password = d.get("username"), d.get("password")
    user = USERS.get(username)

    # ДЕФЕКТ 2: разные сообщения раскрывают, существует ли пользователь
    if not user:
        return jsonify(error="пользователь не найден"), 404
    # ДЕФЕКТ 3: нет лимита попыток — пароль можно перебирать сколько угодно
    if user["password"] != password:
        return jsonify(error="неверный пароль"), 401

    # ДЕФЕКТ 4: session fixation — используем sid, который уже был (в т.ч.
    # выставлен ДО входа, возможно, кем-то другим), вместо выдачи нового
    sid, _ = get_or_create_sid()
    SESSIONS[sid]["user"] = username

    resp = jsonify(ok=True, user=username, role=user["role"])
    resp.set_cookie("sid", sid)

    if d.get("remember"):
        # ДЕФЕКТ 6: токен — это md5 от имени пользователя, без секрета.
        # Его может посчитать кто угодно, просто зная логин.
        token = hashlib.md5(username.encode()).hexdigest()
        resp.set_cookie("remember_token", token, max_age=30 * 24 * 3600)
    return resp


@app.get("/auto-login")
def auto_login():
    token = request.cookies.get("remember_token")
    if not token:
        return jsonify(error="нет remember_token"), 401
    # ДЕФЕКТ 6 (эксплуатация): перебираем известные логины и сверяем md5
    for username in USERS:
        if hashlib.md5(username.encode()).hexdigest() == token:
            sid, _ = get_or_create_sid()
            SESSIONS[sid]["user"] = username
            resp = jsonify(ok=True, user=username, note="вход по remember_token")
            resp.set_cookie("sid", sid)
            return resp
    return jsonify(error="remember_token не распознан"), 401


@app.post("/logout")
def logout():
    sid = request.cookies.get("sid")
    # ДЕФЕКТ 5: сессия на сервере НЕ удаляется и не сбрасывается — только
    # куки убираются в браузере вызывающего. Если токен уже украден/скопирован,
    # он остаётся рабочим и после "выхода"
    resp = jsonify(ok=True, message="вы вышли")
    resp.delete_cookie("sid")
    resp.delete_cookie("remember_token")
    return resp


@app.get("/me")
@login_required
def me(username, user):
    return jsonify(user=username, role=user["role"])


@app.get("/admin")
@login_required
def admin(username, user):
    if user["role"] != "admin":
        return jsonify(error="только для администратора"), 403
    return jsonify(ok=True, message="добро пожаловать в админку",
                    flag="FLAG{A07_remember_me_token_is_just_md5_of_username}")


@app.post("/change-password")
@login_required
def change_password(username, user):
    d = body()
    new_password = d.get("new_password")
    # ДЕФЕКТ 7: текущий пароль не запрашивается и не проверяется —
    # угнанной сессии достаточно, чтобы полностью захватить аккаунт
    if not new_password:
        return jsonify(error="new_password обязателен"), 400
    user["password"] = str(new_password)
    return jsonify(ok=True, message="пароль изменён")


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A07 Authentication Failures — vulnerable', notes='Аккаунты: alice / alice-Good-Pass1, bob, admin',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'alice-Good-Pass1', 'remember': False})], 'POST /register': [('новый', {'username': 'carol', 'password': 'Str0ng-Pass-2025!'})], 'POST /change-password': [('новый пароль', {'new_password': 'New-Pass-2025!'})]},
            uz={'notes': 'Akkauntlar: alice / alice-Good-Pass1, bob, admin',
                'presets': {'POST /register': [('yangi', {'username': 'carol', 'password': 'Str0ng-Pass-2025!'})], 'POST /change-password': [('yangi parol', {'new_password': 'New-Pass-2025!'})]}},
            en={'notes': 'Accounts: alice / alice-Good-Pass1, bob, admin',
             'presets': {'POST /register': [['new user', {'username': 'carol', 'password': 'Str0ng-Pass-2025!'}]],
                         'POST /change-password': [['new password', {'new_password': 'New-Pass-2025!'}]]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
