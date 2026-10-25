"""
A07:2025 Authentication Failures — ИСПРАВЛЕННАЯ версия.

Каждое исправление помечено комментарием FIX N — номер соответствует
дефекту с тем же номером во vulnerable/app.py.
"""
import hashlib
import hmac
import os
import secrets
import time
from functools import wraps

from flask import Flask, Response, jsonify, request

app = Flask(__name__)

USERS = {}        # username -> {"password","role"}
SESSIONS = {}      # sid -> {"user": str}
REMEMBER = {}       # sha256(token) -> {"user": str, "expires": float}
LOGIN_ATTEMPTS = {}  # username -> {"count": int, "locked_until": float}

MAX_ATTEMPTS = 5
LOCK_SECONDS = 60
COMMON_PASSWORDS = {"123456", "password", "qwerty", "111111", "12345678", "admin"}


def reset_state():
    USERS.clear()
    SESSIONS.clear()
    REMEMBER.clear()
    LOGIN_ATTEMPTS.clear()
    USERS["alice"] = {"password": "alice-Good-Pass1", "role": "user"}
    USERS["bob"] = {"password": "bob-Also-Good-Pass2", "role": "user"}
    USERS["admin"] = {"password": "Adm1n-Str0ng-Pass!2025", "role": "admin"}


reset_state()


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def new_sid():
    return secrets.token_hex(16)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        sid = request.cookies.get("sid")
        sess = SESSIONS.get(sid)
        if not sess:
            return jsonify(error="сначала войдите: POST /login"), 401
        user = USERS.get(sess["user"])
        return f(sess["user"], user, *args, **kwargs)
    return wrapper


def password_policy_error(password):
    if not isinstance(password, str) or len(password) < 8:
        return "пароль должен быть не короче 8 символов"
    if password.lower() in COMMON_PASSWORDS:
        return "пароль слишком распространён, выберите другой"
    return None


@app.get("/")
def index():
    # FIX 4 (часть 1): анонимная сессия на главной странице больше не
    # выдаётся — предавторизационного sid, который можно было бы
    # «зафиксировать», просто не существует
    html = """<h1>A07 Authentication Failures — fixed</h1>
<p>Те же эндпоинты, что в vulnerable.</p>"""
    return Response(html, mimetype="text/html")


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
    # FIX 1: политика пароля — минимальная длина и запрет распространённых
    err = password_policy_error(password)
    if err:
        return jsonify(error=err), 400
    USERS[username] = {"password": password, "role": "user"}
    return jsonify(ok=True)


@app.post("/login")
def login():
    d = body()
    username, password = d.get("username"), d.get("password")
    now = time.time()

    attempt = LOGIN_ATTEMPTS.setdefault(username or "", {"count": 0, "locked_until": 0})
    # FIX 3: блокировка после серии неудачных попыток
    if attempt["locked_until"] > now:
        return jsonify(error="слишком много попыток, попробуйте позже"), 429

    user = USERS.get(username)
    # FIX 2: один и тот же обобщённый ответ — существует логин или нет
    generic_fail = (jsonify(error="неверный логин или пароль"), 401)
    if not user or not hmac.compare_digest(user["password"], str(password or "")):
        attempt["count"] += 1
        if attempt["count"] >= MAX_ATTEMPTS:
            attempt["locked_until"] = now + LOCK_SECONDS
            attempt["count"] = 0
        return generic_fail

    attempt["count"] = 0
    attempt["locked_until"] = 0

    # FIX 4 (часть 2): при успешном входе ВСЕГДА выдаём новый sid, старый
    # (если он был прислан клиентом) не используется и не продлевается
    old_sid = request.cookies.get("sid")
    if old_sid in SESSIONS:
        del SESSIONS[old_sid]
    sid = new_sid()
    SESSIONS[sid] = {"user": username}

    resp = jsonify(ok=True, user=username, role=user["role"])
    resp.set_cookie("sid", sid, httponly=True, samesite="Lax")

    if d.get("remember"):
        # FIX 6: случайный токен, хранится на сервере только в виде хэша,
        # с сроком жизни; по токену нельзя вычислить логин
        raw_token = secrets.token_urlsafe(32)
        REMEMBER[hashlib.sha256(raw_token.encode()).hexdigest()] = {
            "user": username, "expires": now + 30 * 24 * 3600,
        }
        resp.set_cookie("remember_token", raw_token,
                        max_age=30 * 24 * 3600, httponly=True, samesite="Lax")
    return resp


@app.get("/auto-login")
def auto_login():
    raw_token = request.cookies.get("remember_token")
    if not raw_token:
        return jsonify(error="нет remember_token"), 401
    digest = hashlib.sha256(raw_token.encode()).hexdigest()
    entry = REMEMBER.get(digest)
    if not entry or entry["expires"] < time.time():
        REMEMBER.pop(digest, None)
        return jsonify(error="remember_token не распознан или истёк"), 401

    # ротация токена при каждом использовании ("one-time" remember-токен)
    del REMEMBER[digest]
    new_raw = secrets.token_urlsafe(32)
    REMEMBER[hashlib.sha256(new_raw.encode()).hexdigest()] = {
        "user": entry["user"], "expires": time.time() + 30 * 24 * 3600,
    }

    sid = new_sid()
    SESSIONS[sid] = {"user": entry["user"]}
    resp = jsonify(ok=True, user=entry["user"], note="вход по remember_token")
    resp.set_cookie("sid", sid, httponly=True, samesite="Lax")
    resp.set_cookie("remember_token", new_raw, max_age=30 * 24 * 3600,
                    httponly=True, samesite="Lax")
    return resp


@app.post("/logout")
def logout():
    sid = request.cookies.get("sid")
    # FIX 5: сессия реально удаляется на сервере — украденный ранее sid
    # после logout больше не работает ни у кого
    SESSIONS.pop(sid, None)
    raw_token = request.cookies.get("remember_token")
    if raw_token:
        REMEMBER.pop(hashlib.sha256(raw_token.encode()).hexdigest(), None)
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
    return jsonify(ok=True, message="добро пожаловать в админку")


@app.post("/change-password")
@login_required
def change_password(username, user):
    d = body()
    current_password = d.get("current_password")
    new_password = d.get("new_password")
    # FIX 7: смена пароля требует знания текущего пароля —
    # угнанной сессии одной уже недостаточно, чтобы отобрать аккаунт
    if not hmac.compare_digest(user["password"], str(current_password or "")):
        return jsonify(error="текущий пароль указан неверно"), 403
    err = password_policy_error(new_password)
    if err:
        return jsonify(error=err), 400
    user["password"] = new_password
    return jsonify(ok=True, message="пароль изменён")


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
