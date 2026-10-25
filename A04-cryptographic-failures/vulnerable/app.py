"""A04 Cryptographic Failures — УЯЗВИМАЯ версия.

Только для обучения. Не публикуйте это приложение в интернете.
Все данные (пароли, номера карт) вымышленные.
"""
import hashlib
import os
import re
import sqlite3
import tempfile
import uuid
from contextlib import closing

from flask import Flask, jsonify, request, session

app = Flask(__name__)

# ОШИБКА №1: слабый секретный ключ, зашитый в код. Им подписывается cookie сессии.
app.secret_key = "secret"

DB_PATH = os.path.join(tempfile.gettempdir(), f"a04_vulnerable_{uuid.uuid4().hex}.db")
OUTBOX = []  # имитация почтового ящика пользователя (только для лабы)


def md5(text):
    return hashlib.md5(text.encode()).hexdigest()


def query(sql, params=(), commit=False):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        if commit:
            conn.commit()
        return rows


def init_db():
    query("CREATE TABLE users (username TEXT PRIMARY KEY, password_hash TEXT, role TEXT)", commit=True)
    query("CREATE TABLE cards (username TEXT, number TEXT)", commit=True)
    seed = [("alice", "sunshine", "user"), ("bob", "qwerty", "user"), ("admin", "Adm1n!lab#2026", "admin")]
    for username, password, role in seed:
        # ОШИБКА №2: пароль хранится как MD5 без соли
        query("INSERT INTO users VALUES (?, ?, ?)", (username, md5(password), role), commit=True)
    # ОШИБКА №3: номера карт хранятся открытым текстом (это тестовые номера)
    query("INSERT INTO cards VALUES (?, ?)", ("alice", "4111111111111111"), commit=True)
    query("INSERT INTO cards VALUES (?, ?)", ("bob", "5555555555554444"), commit=True)


init_db()


@app.get("/")
def index():
    return jsonify(
        message="A04 Cryptographic Failures lab (vulnerable)",
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
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username) or not password:
        return jsonify(error="invalid input"), 400
    if query("SELECT 1 FROM users WHERE username = ?", (username,)):
        return jsonify(error="user exists"), 409
    query("INSERT INTO users VALUES (?, ?, 'user')", (username, md5(password)), commit=True)
    return jsonify(message="registered"), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    rows = query("SELECT * FROM users WHERE username = ?", (data.get("username", ""),))
    if not rows or rows[0]["password_hash"] != md5(data.get("password", "")):
        return jsonify(error="invalid credentials"), 401
    session["user"] = rows[0]["username"]
    return jsonify(message="logged in")


@app.get("/me")
def me():
    user = session.get("user")
    if not user:
        return jsonify(error="login required"), 401
    rows = query("SELECT role FROM users WHERE username = ?", (user,))
    role = rows[0]["role"] if rows else "unknown"
    result = {"user": user, "role": role}
    if role == "admin":
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
    query("INSERT INTO cards VALUES (?, ?)", (user, number), commit=True)
    return jsonify(message="card saved"), 201


@app.get("/cards")
def my_cards():
    user = session.get("user")
    if not user:
        return jsonify(error="login required"), 401
    # ОШИБКА №3 (продолжение): в ответе полный номер карты
    return jsonify([r["number"] for r in query("SELECT number FROM cards WHERE username = ?", (user,))])


@app.post("/reset-request")
def reset_request():
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "")
    if query("SELECT 1 FROM users WHERE username = ?", (username,)):
        # ОШИБКА №4: токен сброса пароля предсказуем — это MD5 от имени пользователя
        token = md5(username)
        OUTBOX.append({"to": username, "link": f"/reset/{token}"})
    return jsonify(message="если пользователь существует, ссылка отправлена")


@app.post("/reset/<token>")
def reset(token):
    data = request.get_json(silent=True) or request.form
    new_password = data.get("new_password", "")
    if not new_password:
        return jsonify(error="new_password required"), 400
    for row in query("SELECT username FROM users"):
        if md5(row["username"]) == token:
            query("UPDATE users SET password_hash = ? WHERE username = ?",
                  (md5(new_password), row["username"]), commit=True)
            return jsonify(message="password changed")
    return jsonify(error="invalid token"), 404


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
    )


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A04 Cryptographic Failures — vulnerable', notes='Аккаунты: alice / sunshine, bob / qwerty',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'sunshine'})], 'POST /register': [('новый', {'username': 'carol', 'password': 'Str0ng-pass-1'})], 'POST /cards': [('тестовая карта', {'number': '4242424242424242'})], 'POST /reset-request': [('alice', {'username': 'alice'})]})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
