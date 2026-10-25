"""A04 Cryptographic Failures — ИСПРАВЛЕННАЯ версия.

Отличия от vulnerable/app.py помечены комментариями FIX.
"""
import hashlib
import os
import re
import secrets
import sqlite3
import tempfile
import time
import uuid
from contextlib import closing

from cryptography.fernet import Fernet
from flask import Flask, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# FIX: ключ сессии берётся из окружения, а если его нет, генерируется случайный
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
# В реальной системе добавьте SESSION_COOKIE_SECURE=True и работайте только по HTTPS.

# FIX: ключ шифрования данных тоже из окружения (в лабе, если нет, создаётся новый при старте)
fernet = Fernet((os.environ.get("DATA_ENCRYPTION_KEY") or Fernet.generate_key().decode()).encode())

DB_PATH = os.path.join(tempfile.gettempdir(), f"a04_fixed_{uuid.uuid4().hex}.db")
OUTBOX = []  # имитация почтового ящика пользователя (только для лабы)
RESET_TTL_SECONDS = 15 * 60

DUMMY_HASH = generate_password_hash("dummy-password-for-timing")


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def query(sql, params=(), commit=False):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        if commit:
            conn.commit()
        return rows


def init_db():
    query("CREATE TABLE users (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT)", commit=True)
    query("CREATE TABLE cards (username TEXT, number_enc TEXT)", commit=True)
    query("CREATE TABLE reset_tokens (token_hash TEXT PRIMARY KEY, username TEXT, expires_at REAL, used INTEGER)",
          commit=True)
    seed = [("alice", "sunshine", "user"), ("bob", "qwerty", "user"), ("admin", "Adm1n!lab#2026", "admin")]
    for username, password, role in seed:
        # FIX: стойкий алгоритм с солью (scrypt) вместо MD5
        query("INSERT INTO users VALUES (?, ?, ?)", (username, generate_password_hash(password), role), commit=True)
    # FIX: номера карт шифруются перед записью
    for username, number in (("alice", "4111111111111111"), ("bob", "5555555555554444")):
        query("INSERT INTO cards VALUES (?, ?)", (username, fernet.encrypt(number.encode()).decode()), commit=True)


init_db()


def mask(number):
    return "**** **** **** " + number[-4:]


@app.get("/")
def index():
    return jsonify(
        message="A04 Cryptographic Failures lab (fixed)",
        endpoints=[
            "POST /register", "POST /login", "GET /me",
            "POST /cards", "GET /cards",
            "POST /reset-request", "POST /reset/<token>",
            "GET /_lab/outbox  (имитация почты, только для лабы)",
            "GET /_lab/dump    (имитация утечки базы, только для лабы)",
        ],
        accounts="alice / sunshine, bob / qwerty",
    )


@app.post("/register")
def register():
    data = request.get_json(silent=True) or request.form
    username, password = data.get("username", ""), data.get("password", "")
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username) or len(password) < 8:
        return jsonify(error="invalid input (пароль не короче 8 символов)"), 400
    if query("SELECT 1 FROM users WHERE username = ?", (username,)):
        return jsonify(error="user exists"), 409
    query("INSERT INTO users VALUES (?, ?, 'user')", (username, generate_password_hash(password)), commit=True)
    return jsonify(message="registered"), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    rows = query("SELECT * FROM users WHERE username = ?", (data.get("username", ""),))
    stored = rows[0]["password_hash"] if rows else DUMMY_HASH  # одинаковое время для неизвестного имени
    if not check_password_hash(stored, data.get("password", "")) or not rows:
        return jsonify(error="invalid credentials"), 401
    session["user"] = rows[0]["username"]
    return jsonify(message="logged in")


@app.get("/me")
def me():
    user = session.get("user")
    if not user:
        return jsonify(error="login required"), 401
    rows = query("SELECT role FROM users WHERE username = ?", (user,))
    if not rows:
        return jsonify(error="login required"), 401
    result = {"user": user, "role": rows[0]["role"]}
    if rows[0]["role"] == "admin":
        result["flag"] = "FLAG{a04_admin_takeover}"
    return jsonify(result)


@app.post("/cards")
def add_card():
    user = session.get("user")
    if not user:
        return jsonify(error="login required"), 401
    data = request.get_json(silent=True) or request.form
    number = data.get("number", "")
    if not re.fullmatch(r"\d{13,19}", number):
        return jsonify(error="invalid card number"), 400
    query("INSERT INTO cards VALUES (?, ?)", (user, fernet.encrypt(number.encode()).decode()), commit=True)
    return jsonify(message="card saved"), 201


@app.get("/cards")
def my_cards():
    user = session.get("user")
    if not user:
        return jsonify(error="login required"), 401
    rows = query("SELECT number_enc FROM cards WHERE username = ?", (user,))
    # FIX: в ответе только маска, полный номер наружу не отдаётся
    return jsonify([mask(fernet.decrypt(r["number_enc"].encode()).decode()) for r in rows])


@app.post("/reset-request")
def reset_request():
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "")
    if query("SELECT 1 FROM users WHERE username = ?", (username,)):
        # FIX: случайный токен, в базе только его хеш, срок жизни и одноразовость
        token = secrets.token_urlsafe(32)
        query("INSERT INTO reset_tokens VALUES (?, ?, ?, 0)",
              (sha256(token), username, time.time() + RESET_TTL_SECONDS), commit=True)
        OUTBOX.append({"to": username, "link": f"/reset/{token}"})
    return jsonify(message="если пользователь существует, ссылка отправлена")


@app.post("/reset/<token>")
def reset(token):
    data = request.get_json(silent=True) or request.form
    new_password = data.get("new_password", "")
    if len(new_password) < 8:
        return jsonify(error="new_password must be at least 8 characters"), 400
    rows = query("SELECT * FROM reset_tokens WHERE token_hash = ?", (sha256(token),))
    if not rows or rows[0]["used"] or rows[0]["expires_at"] < time.time():
        return jsonify(error="invalid or expired token"), 400
    query("UPDATE reset_tokens SET used = 1 WHERE token_hash = ?", (sha256(token),), commit=True)
    query("UPDATE users SET password_hash = ? WHERE username = ?",
          (generate_password_hash(new_password), rows[0]["username"]), commit=True)
    return jsonify(message="password changed")


@app.get("/_lab/outbox")
def lab_outbox():
    """Имитация почтового ящика: показывает «письма» со ссылками сброса."""
    return jsonify(OUTBOX)


@app.get("/_lab/dump")
def lab_dump():
    """Имитация утечки базы данных: показывает, как данные лежат в хранилище."""
    return jsonify(
        users=[dict(r) for r in query("SELECT * FROM users")],
        cards=[dict(r) for r in query("SELECT * FROM cards")],
        reset_tokens=[dict(r) for r in query("SELECT * FROM reset_tokens")],
    )


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A04 Cryptographic Failures — fixed', notes='Аккаунты: alice / sunshine, bob / qwerty',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'sunshine'})], 'POST /register': [('новый', {'username': 'carol', 'password': 'Str0ng-pass-1'})], 'POST /cards': [('тестовая карта', {'number': '4242424242424242'})], 'POST /reset-request': [('alice', {'username': 'alice'})]},
            uz={'notes': 'Akkauntlar: alice / sunshine, bob / qwerty', 'presets': {'POST /register': [('yangi', {'username': 'carol', 'password': 'Str0ng-pass-1'})], 'POST /cards': [('test kartasi', {'number': '4242424242424242'})]}},
            en={'notes': 'Accounts: alice / sunshine, bob / qwerty',
             'presets': {'POST /register': [['new user', {'username': 'carol', 'password': 'Str0ng-pass-1'}]],
                         'POST /cards': [['test card', {'number': '4242424242424242'}]]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
