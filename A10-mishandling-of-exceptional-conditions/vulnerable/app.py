"""
A10:2025 Mishandling of Exceptional Conditions — УЯЗВИМАЯ версия.

Пять дефектов обработки ошибок и сбоев:
1. Подробные ошибки: в ответе трассировка стека и внутренняя конфигурация
2. Fail-open: исключение в проверке доступа приводит к РАЗРЕШЕНИЮ
3. Частично выполненная операция: деньги списаны, заказ не создан, отката нет
4. Нет лимитов на размер и «стоимость» запроса: один запрос валит сервис
5. В ответ пользователю уходит сырой текст исключения (пути на сервере)

Только для локального запуска!
"""
import os
import re
import secrets
import sqlite3
import tempfile
import threading
import traceback
from functools import wraps

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.json.ensure_ascii = False  # кириллица в JSON читается без \uXXXX

# Префикс нужен, чтобы cookie vulnerable и fixed (один хост 127.0.0.1,
# разные порты) не перезаписывали друг друга в браузере
PREFIX = "a10v_"

CONFIG = {  # «внутренняя» конфигурация приложения
    "env": "production",
    "database": "sqlite:///:memory:",
    "internal_api_key": "FLAG{a10_verbose_errors}",
}
USERS = {
    "alice": {"password": "alice123", "level": 1},
    "bob": {"password": "bob123", "level": 2},
}
# Документы. У документа 3 уровень доступа в данных испорчен после неудачного
# импорта: вместо числа в поле лежит текст.
DOCUMENTS = {
    1: {"title": "Меню столовой", "level": "1", "content": "Сегодня: борщ и плов."},
    2: {"title": "Внутренний регламент", "level": "2", "content": "Пропуск обязателен."},
    3: {"title": "Бюджет компании", "level": "TOP",
        "content": "FLAG{a10_fail_open} — бюджет на следующий год"},
    4: {"title": "План увольнений", "level": "5", "content": "Только для руководства."},
}
INITIAL_BALANCE = 100
MEMORY_LIMIT_MB = 64  # «оперативная память» сервиса в лабе (имитация)

SESSIONS, STATE = {}, {"crashed": False}
REPORTS_DIR = tempfile.mkdtemp(prefix="a10v_")
with open(os.path.join(REPORTS_DIR, "q1.txt"), "w", encoding="utf-8") as fh:
    fh.write("Отчёт за 1 квартал: выручка выросла на 4%.\n")  # q2.txt нет намеренно
os.mkdir(os.path.join(REPORTS_DIR, "archive.txt"))  # «битый» отчёт: на месте файла каталог

db = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
db.row_factory = sqlite3.Row
db_lock = threading.Lock()


def reset_state():
    SESSIONS.clear()
    STATE["crashed"] = False
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


@app.before_request
def service_down():
    # Имитация упавшего сервиса (см. ДЕФЕКТ 4): пока он «лежит», отвечают
    # только /health, /reset-lab и страница интерфейса
    if STATE["crashed"] and request.path not in ("/health", "/reset-lab", "/ui", "/"):
        return jsonify(error="сервис недоступен"), 503


@app.errorhandler(Exception)
def on_error(e):
    if isinstance(e, HTTPException):
        return e
    # ДЕФЕКТ 1: «режим отладки» в продакшене — клиенту уходит текст ошибки,
    # трассировка стека (с путями к файлам и строками кода) и конфигурация
    return jsonify(error=str(e), type=type(e).__name__,
                   trace=traceback.format_exc().splitlines(),
                   config=CONFIG), 500


@app.get("/")
def index():
    return jsonify(
        message="A10 Mishandling of Exceptional Conditions lab (vulnerable)",
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
    resp.set_cookie(PREFIX + "sid", sid)
    return resp


@app.get("/me")
@login_required
def me(user):
    row = db.execute("SELECT balance FROM accounts WHERE user = ?", (user,)).fetchone()
    return jsonify(user=user, level=USERS[user]["level"], balance=row["balance"])


# ---------- доступ к документам (ДЕФЕКТ 2) ----------
def is_allowed(user, doc):
    try:
        return int(doc["level"]) <= USERS[user]["level"]
    except Exception:
        # ДЕФЕКТ 2: любая ошибка при проверке означает «можно». Испорченные
        # данные, сбой зависимости или неожиданный ввод открывают доступ.
        return True


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
    # Необработанное исключение при нечисловом month — см. ДЕФЕКТ 1
    month = int(request.args.get("month", "1"))
    return jsonify(month=month, summary=f"Итоги за месяц {month}: всё в норме")


# ---------- заказы (ДЕФЕКТ 3) ----------
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
        item = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not item:
            return jsonify(error="товар не найден"), 404
        total = item["price"] * qty
        balance = db.execute("SELECT balance FROM accounts WHERE user = ?", (user,)).fetchone()["balance"]
        if balance < total:
            return jsonify(error="недостаточно средств"), 402
        # ДЕФЕКТ 3: каждый шаг сохраняется сразу (автокоммит). Сначала деньги
        # списываются, потом проверяется склад. Если упасть между шагами,
        # транзакции для отката нет.
        db.execute("UPDATE accounts SET balance = balance - ? WHERE user = ?", (total, user))
        if item["qty"] < qty:
            raise RuntimeError(f"на складе осталось {item['qty']}, а нужно {qty}")
        db.execute("UPDATE items SET qty = qty - ? WHERE id = ?", (qty, item_id))
        cur = db.execute("INSERT INTO orders (user, item_id, qty, total) VALUES (?, ?, ?, ?)",
                         (user, item_id, qty, total))
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


# ---------- лимиты (ДЕФЕКТ 4) ----------
@app.post("/thumbnail")
def thumbnail():
    d = body()
    w, h = d.get("width"), d.get("height")
    if not isinstance(w, int) or not isinstance(h, int):
        return jsonify(error="нужны width и height (целые)"), 400
    # ДЕФЕКТ 4: ни верхней границы размеров, ни ограничения размера запроса,
    # ни таймаута. Оценка памяти: 4 байта на пиксель.
    estimated_mb = round(w * h * 4 / 1024 / 1024, 2)
    if estimated_mb > MEMORY_LIMIT_MB:
        STATE["crashed"] = True  # в жизни это OOM-killer или зависание процесса
        return jsonify(error="сервис упал: не хватило памяти"), 500
    return jsonify(ok=True, estimated_mb=estimated_mb)


@app.get("/health")
def health():
    if STATE["crashed"]:
        return jsonify(status="crashed", flag="FLAG{a10_no_limits}",
                       note="один запрос вывел сервис из строя; «поднять» его можно через POST /reset-lab"), 503
    return jsonify(status="ok")


# ---------- отчёты (ДЕФЕКТ 5) ----------
@app.get("/reports/<name>")
def get_report(name):
    if not re.fullmatch(r"[a-z0-9_]+", name):
        return jsonify(error="недопустимое имя отчёта"), 400
    try:
        with open(os.path.join(REPORTS_DIR, name + ".txt"), encoding="utf-8") as fh:
            return jsonify(name=name, text=fh.read())
    except Exception as e:
        # ДЕФЕКТ 5: пользователю показывается текст исключения как есть:
        # в нём полный путь к файлу на сервере
        return jsonify(error=str(e)), 404


from labui import register_ui  # noqa: E402  (учебный интерфейс /ui)
register_ui(app, "A10 Mishandling of Exceptional Conditions — vulnerable",
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
                }},
            en={'notes': 'Accounts: alice / alice123 (level 1), bob / bob123 (level 2). Initial balance: 100.',
             'presets': {'GET /documents/<int:doc_id>': [['document 1', '/documents/1'], ['document 2', '/documents/2']],
                         'POST /orders': [['1 mug', {'item_id': 1, 'qty': 1}]]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
