"""
A10:2025 Mishandling of Exceptional Conditions — ИСПРАВЛЕННАЯ версия.

Исправления помечены комментариями "# FIX N"; номера совпадают с
"# ДЕФЕКТ N" в vulnerable/app.py. Только для локального запуска!
"""
import logging
import os
import re
import secrets
import sqlite3
import tempfile
import threading
from functools import wraps

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.json.ensure_ascii = False  # кириллица в JSON читается без \uXXXX
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# FIX 4: потолок размера любого запроса — Flask сам ответит 413,
# не читая тело дальше
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024

PREFIX = "a10f_"

USERS = {
    "alice": {"password": "alice123", "level": 1},
    "bob": {"password": "bob123", "level": 2},
}
DOCUMENTS = {
    1: {"title": "Меню столовой", "level": "1", "content": "Сегодня: борщ и плов."},
    2: {"title": "Внутренний регламент", "level": "2", "content": "Пропуск обязателен."},
    3: {"title": "Бюджет компании", "level": "TOP",
        "content": "бюджет на следующий год"},
    4: {"title": "План увольнений", "level": "5", "content": "Только для руководства."},
}
INITIAL_BALANCE = 100
MEMORY_LIMIT_MB = 64
MAX_SIDE = 2048  # FIX 4: допустимая сторона изображения, пикселей

SESSIONS = {}
REPORTS_DIR = tempfile.mkdtemp(prefix="a10f_")
with open(os.path.join(REPORTS_DIR, "q1.txt"), "w", encoding="utf-8") as fh:
    fh.write("Отчёт за 1 квартал: выручка выросла на 4%.\n")
os.mkdir(os.path.join(REPORTS_DIR, "archive.txt"))  # «битый» отчёт: на месте файла каталог

db = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
db.row_factory = sqlite3.Row
db_lock = threading.Lock()


class Reject(Exception):
    """Ожидаемый отказ (бизнес-правило): откат транзакции и понятный ответ."""
    def __init__(self, message, status):
        super().__init__(message)
        self.message, self.status = message, status


def reset_state():
    SESSIONS.clear()
    for table in ("accounts", "items", "orders"):
        db.execute(f"DROP TABLE IF EXISTS {table}")
    db.execute("CREATE TABLE accounts (user TEXT PRIMARY KEY, balance INTEGER)")
    db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, qty INTEGER)")
    db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, "
               "user TEXT, item_id INTEGER, qty INTEGER, total INTEGER)")
    for user in USERS:
        db.execute("INSERT INTO accounts VALUES (?, ?)", (user, INITIAL_BALANCE))
    db.execute("INSERT INTO items VALUES (1, 'Кружка', 20, 2)")
    db.execute("INSERT INTO items VALUES (2, 'Ноутбук', 90, 1)")


reset_state()


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def current_user():
    return SESSIONS.get(request.cookies.get(PREFIX + "sid"))


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify(error="сначала войдите: POST /login"), 401
        return f(user, *args, **kwargs)
    return wrapper


@app.errorhandler(Exception)
def on_error(e):
    # FIX 1: единый обработчик. Клиент получает нейтральное сообщение и
    # error_id, а подробности (трассировка) остаются в логе сервера.
    if isinstance(e, HTTPException):
        return jsonify(error=e.name), e.code
    error_id = secrets.token_hex(4)
    app.logger.error("error_id=%s path=%s", error_id, request.path, exc_info=e)
    return jsonify(error="внутренняя ошибка сервера", error_id=error_id), 500


@app.get("/")
def index():
    return jsonify(
        message="A10 Mishandling of Exceptional Conditions lab (fixed)",
        endpoints=["POST /login", "GET /me", "GET /documents/<id>", "GET /report?month=<1-12>",
                   "GET /items", "POST /orders", "POST /thumbnail", "GET /reports/<имя>",
                   "GET /health", "GET /_lab/consistency", "POST /reset-lab"],
        accounts="alice / alice123, bob / bob123",
    )


@app.post("/reset-lab")
def reset_lab():
    reset_state()
    return jsonify(ok=True)


@app.post("/login")
def login():
    d = body()
    user = USERS.get(d.get("username"))
    if not user or user["password"] != d.get("password"):
        return jsonify(error="неверный логин или пароль"), 401
    sid = secrets.token_hex(8)
    SESSIONS[sid] = d["username"]
    resp = jsonify(ok=True, user=d["username"])
    resp.set_cookie(PREFIX + "sid", sid, httponly=True, samesite="Lax")
    return resp


@app.get("/me")
@login_required
def me(user):
    row = db.execute("SELECT balance FROM accounts WHERE user = ?", (user,)).fetchone()
    return jsonify(user=user, level=USERS[user]["level"], balance=row["balance"])


def is_allowed(user, doc):
    try:
        return int(doc["level"]) <= USERS[user]["level"]
    except Exception:
        # FIX 2: fail-closed. Если проверить нельзя, доступа нет. Сбой при этом
        # не молчит: запись попадает в лог, чтобы испорченные данные починили.
        app.logger.error("access check failed: user=%s level=%r", user, doc.get("level"))
        return False


@app.get("/documents/<int:doc_id>")
@login_required
def get_document(user, doc_id):
    doc = DOCUMENTS.get(doc_id)
    if not doc:
        return jsonify(error="документ не найден"), 404
    if not is_allowed(user, doc):
        return jsonify(error="недостаточно прав"), 403
    return jsonify(id=doc_id, title=doc["title"], content=doc["content"])


@app.get("/report")
def report():
    # FIX 1: ожидаемую ошибку ввода обрабатываем сами, а не ловим глобально
    try:
        month = int(request.args.get("month", "1"))
    except ValueError:
        return jsonify(error="month должен быть числом от 1 до 12"), 400
    if not 1 <= month <= 12:
        return jsonify(error="month должен быть числом от 1 до 12"), 400
    return jsonify(month=month, summary=f"Итоги за месяц {month}: всё в норме")


@app.get("/items")
def items():
    return jsonify([dict(r) for r in db.execute("SELECT * FROM items")])


@app.post("/orders")
@login_required
def create_order(user):
    d = body()
    item_id, qty = d.get("item_id"), d.get("qty")
    if not isinstance(item_id, int) or not isinstance(qty, int) or qty <= 0:
        return jsonify(error="нужны item_id и qty (целые, qty > 0)"), 400
    with db_lock:
        # FIX 3: вся операция в одной транзакции. Шаги те же, что и во
        # vulnerable (сначала списание, потом склад), но при любой ошибке
        # откатывается всё.
        db.execute("BEGIN IMMEDIATE")
        try:
            item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
            if not item:
                raise Reject("товар не найден", 404)
            total = item["price"] * qty
            balance = db.execute("SELECT balance FROM accounts WHERE user = ?", (user,)).fetchone()["balance"]
            if balance < total:
                raise Reject("недостаточно средств", 402)
            db.execute("UPDATE accounts SET balance = balance - ? WHERE user = ?", (total, user))
            if item["qty"] < qty:
                raise Reject("недостаточно товара на складе", 409)
            db.execute("UPDATE items SET qty = qty - ? WHERE id = ?", (qty, item_id))
            cur = db.execute("INSERT INTO orders (user, item_id, qty, total) VALUES (?, ?, ?, ?)",
                             (user, item_id, qty, total))
            db.execute("COMMIT")
        except Reject as r:
            db.execute("ROLLBACK")
            return jsonify(error=r.message), r.status
        except Exception:
            db.execute("ROLLBACK")
            raise  # неожиданное: откат сделан, дальше глобальный обработчик
        return jsonify(ok=True, order_id=cur.lastrowid, total=total)


@app.get("/_lab/consistency")
def lab_consistency():
    """ЛАБ-ПОМОЩНИК: проверка целостности — сходятся ли списания и заказы."""
    lost = {}
    for r in db.execute("SELECT user, balance FROM accounts"):
        invoiced = db.execute("SELECT COALESCE(SUM(total), 0) FROM orders WHERE user = ?",
                              (r["user"],)).fetchone()[0]
        diff = (INITIAL_BALANCE - r["balance"]) - invoiced
        if diff:
            lost[r["user"]] = diff
    resp = {"money_lost": lost}
    if lost:
        resp["flag"] = "FLAG{a10_partial_operation}"
        resp["note"] = "деньги списаны, а заказов на эти суммы нет"
    return jsonify(resp)


@app.post("/thumbnail")
def thumbnail():
    d = body()
    w, h = d.get("width"), d.get("height")
    if not isinstance(w, int) or not isinstance(h, int):
        return jsonify(error="нужны width и height (целые)"), 400
    # FIX 4: границы входных данных проверяются ДО выделения ресурсов
    if not (1 <= w <= MAX_SIDE and 1 <= h <= MAX_SIDE):
        return jsonify(error=f"допустимая сторона: от 1 до {MAX_SIDE} пикселей"), 413
    estimated_mb = round(w * h * 4 / 1024 / 1024, 2)
    if estimated_mb > MEMORY_LIMIT_MB:
        return jsonify(error="слишком большое изображение"), 413
    return jsonify(ok=True, estimated_mb=estimated_mb)


@app.get("/health")
def health():
    return jsonify(status="ok", max_body_bytes=app.config["MAX_CONTENT_LENGTH"],
                   max_side=MAX_SIDE)


@app.get("/reports/<name>")
def get_report(name):
    if not re.fullmatch(r"[a-z0-9_]+", name):
        return jsonify(error="недопустимое имя отчёта"), 400
    try:
        with open(os.path.join(REPORTS_DIR, name + ".txt"), encoding="utf-8") as fh:
            return jsonify(name=name, text=fh.read())
    except FileNotFoundError:
        # FIX 5: ожидаемую ситуацию обрабатываем по существу, текст
        # исключения наружу не отдаём (путь остаётся только в логе)
        app.logger.warning("report not found: %s", name)
        return jsonify(error="отчёт не найден"), 404


from labui import register_ui  # noqa: E402  (учебный интерфейс /ui)
register_ui(app, "A10 Mishandling of Exceptional Conditions — fixed",
            notes="Аккаунты: alice / alice123 (уровень 1), bob / bob123 (уровень 2). Начальный баланс: 100.",
            presets={
                "POST /login": [("alice", {"username": "alice", "password": "alice123"}),
                                ("bob", {"username": "bob", "password": "bob123"})],
                "GET /documents/<int:doc_id>": [("документ 1", "/documents/1"), ("документ 2", "/documents/2")],
                "GET /report": [("month=3", "?month=3")],
                "POST /orders": [("1 кружка", {"item_id": 1, "qty": 1})],
                "POST /thumbnail": [("800×600", {"width": 800, "height": 600})],
                "GET /reports/<name>": [("q1", "/reports/q1")],
            },
            uz={"notes": "Akkauntlar: alice / alice123 (1-daraja), bob / bob123 (2-daraja). Boshlangʻich balans: 100.",
                "presets": {
                    "GET /documents/<int:doc_id>": [("hujjat 1", "/documents/1"), ("hujjat 2", "/documents/2")],
                    "POST /orders": [("1 ta krujka", {"item_id": 1, "qty": 1})],
                }})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
