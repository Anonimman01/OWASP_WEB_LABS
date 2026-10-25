"""A05 Injection — УЯЗВИМАЯ версия.

Только для обучения. Не публикуйте это приложение в интернете.
Все данные вымышленные.
"""
import os
import sqlite3
import tempfile
import uuid
from contextlib import closing

from flask import Flask, jsonify, make_response, request

app = Flask(__name__)

DB_PATH = os.path.join(tempfile.gettempdir(), f"a05_vulnerable_{uuid.uuid4().hex}.db")
GUESTBOOK = []


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, secret TEXT)")
        conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, hidden INTEGER)")
        # Пароли в открытом виде только ради простоты лабы (про хеширование см. лабу A04).
        conn.executemany(
            "INSERT INTO users (username, password, role, secret) VALUES (?, ?, ?, ?)",
            [
                ("alice", "alice123", "user", "нет секретов"),
                ("bob", "bob123", "user", "нет секретов"),
                ("admin", "Adm1n-lab-pass", "admin", "FLAG{a05_sqli_union_dump}"),
            ],
        )
        conn.executemany(
            "INSERT INTO products (name, price, hidden) VALUES (?, ?, ?)",
            [
                ("Лампа настольная", 1500, 0),
                ("Лампа напольная", 4200, 0),
                ("Кружка", 300, 0),
                ("Блокнот", 200, 0),
                ("Скрытый образец FLAG{a05_hidden_product}", 0, 1),
            ],
        )
        conn.commit()


init_db()


def run_sql(sql):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        return conn.execute(sql).fetchall()


def html_page(body):
    resp = make_response(f"<!doctype html><html><head><meta charset='utf-8'></head><body>{body}</body></html>")
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


@app.get("/")
def index():
    return jsonify(
        message="A05 Injection lab (vulnerable)",
        endpoints=[
            "POST /login (JSON: username, password)",
            "GET /products?q=<строка>",
            "GET /search?q=<строка>   (HTML)",
            "GET /guestbook, POST /guestbook (JSON: name, message)   (HTML)",
        ],
        accounts="alice / alice123",
    )


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    username, password = data.get("username", ""), data.get("password", "")
    # УЯЗВИМОСТЬ: SQL-запрос собирается склейкой строк
    sql = f"SELECT username, role, secret FROM users WHERE username = '{username}' AND password = '{password}'"
    try:
        rows = run_sql(sql)
    except sqlite3.Error as exc:
        return jsonify(error=str(exc)), 500
    if not rows:
        return jsonify(error="invalid credentials"), 401
    user, role, _ = rows[0]
    result = {"message": "logged in", "user": user, "role": role}
    if role == "admin":
        result["flag"] = "FLAG{a05_sqli_login_bypass}"
    return jsonify(result)


@app.get("/products")
def products():
    q = request.args.get("q", "")
    # УЯЗВИМОСТЬ: ввод пользователя попадает прямо в SQL
    sql = f"SELECT id, name, price FROM products WHERE name LIKE '%{q}%' AND hidden = 0"
    try:
        rows = run_sql(sql)
    except sqlite3.Error as exc:
        return jsonify(error=str(exc)), 500
    return jsonify([{"id": r[0], "name": r[1], "price": r[2]} for r in rows])


@app.get("/search")
def search():
    q = request.args.get("q", "")
    # УЯЗВИМОСТЬ: отражённый XSS — ввод вставляется в HTML без экранирования
    return html_page(f"<h1>Результаты поиска: {q}</h1><p>Ничего не найдено.</p>")


@app.route("/guestbook", methods=["GET", "POST"])
def guestbook():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        GUESTBOOK.append({"name": data.get("name", "аноним"), "message": data.get("message", "")})
        return jsonify(message="saved"), 201
    # УЯЗВИМОСТЬ: хранимый XSS — сообщения выводятся как есть
    items = "".join(f"<li><b>{e['name']}</b>: {e['message']}</li>" for e in GUESTBOOK)
    return html_page(f"<h1>Гостевая книга</h1><ul>{items}</ul>")


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A05 Injection — vulnerable', notes='Аккаунт: alice / alice123',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'alice123'})], 'GET /products': [('q=a', '?q=a')], 'GET /search': [('q=привет', '?q=привет')], 'POST /guestbook': [('запись', {'name': 'Аня', 'message': 'Привет!'})]},
            uz={'notes': 'Akkaunt: alice / alice123', 'presets': {'GET /search': [('q=salom', '?q=salom')], 'POST /guestbook': [('yozuv', {'name': 'Ali', 'message': 'Salom!'})]}},
            en={'notes': 'Account: alice / alice123',
             'presets': {'GET /search': [['q=hello', '?q=hello']],
                         'POST /guestbook': [['entry', {'name': 'Anna', 'message': 'Hello!'}]]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
