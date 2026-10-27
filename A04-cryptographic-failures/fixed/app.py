"""A04 Cryptographic Failures — ИСПРАВЛЕННАЯ версия.

Сайт банка ATLAS полностью повторяет vulnerable/app.py: те же страницы,
те же маршруты, те же проверки. Отличия только в криптографии и помечены
комментариями FIX:

  FIX 1 — ключ подписи cookie сессии берётся из окружения (или случайный);
  FIX 2 — пароли хранятся через scrypt с уникальной солью;
  FIX 3 — номера карт шифруются Fernet, наружу отдаётся только маска;
  FIX 4 — токен сброса пароля случайный, в базе его хеш, срок и
          одноразовость.

Только для обучения. Не публикуйте это приложение в интернете.
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
from flask import (Flask, flash, get_flashed_messages, g, jsonify, redirect,
                   render_template, request, session)
from werkzeug.security import check_password_hash, generate_password_hash

from bank import (BRAND, LANGS, mask, money, register_lang, signed,
                  t as texts)

app = Flask(__name__)

# FIX: ключ подписи сессии — из окружения, а если его нет, то случайный.
# Такую сессию нельзя подделать, не зная ключа.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
# В реальной системе добавьте SESSION_COOKIE_SECURE=True и работайте только по HTTPS.

# FIX: ключ шифрования данных карт тоже из окружения; в лабе без переменной
# окружения он создаётся заново при каждом старте (см. SOLUTION).
fernet = Fernet((os.environ.get("DATA_ENCRYPTION_KEY")
                 or Fernet.generate_key().decode()).encode())

register_lang(app)

DB_PATH = os.path.join(tempfile.gettempdir(),
                       f"a04_fixed_{uuid.uuid4().hex}.db")
OUTBOX = []  # имитация почтового ящика (только для лабы)
FLAG = "FLAG{a04_admin_takeover}"
RESET_TTL_SECONDS = 15 * 60

# FIX: хеш-заглушка для несуществующего пользователя: проверка пароля
# занимает столько же времени, сколько для настоящего аккаунта.
DUMMY_HASH = generate_password_hash("dummy-password-for-timing")

SEED_USERS = [
    ("alice", "Alice Weaver", "sunshine", "user"),
    ("bob", "Bob Nolan", "qwerty", "user"),
    ("admin", "Lab Administrator", "Adm1n!lab#2026", "admin"),
]


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def query(sql, params=(), commit=False):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        if commit:
            conn.commit()
        return rows


def insert(sql, params=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid


def init_db():
    query("""CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL)""", commit=True)
    query("""CREATE TABLE accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                number TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0)""", commit=True)
    query("""CREATE TABLE cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                number TEXT NOT NULL,
                brand TEXT NOT NULL,
                exp TEXT NOT NULL,
                holder TEXT NOT NULL,
                tone TEXT NOT NULL DEFAULT '')""", commit=True)
    query("""CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                direction TEXT NOT NULL,
                description TEXT NOT NULL,
                created TEXT NOT NULL)""", commit=True)
    query("""CREATE TABLE reset_tokens (
                token_hash TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                expires_at REAL NOT NULL,
                used INTEGER NOT NULL DEFAULT 0)""", commit=True)

    user_id = {}
    for username, full_name, password, role in SEED_USERS:
        # FIX: стойкий алгоритм с солью (scrypt) вместо MD5
        user_id[username] = insert(
            "INSERT INTO users (username, full_name, role, password_hash) "
            "VALUES (?, ?, ?, ?)",
            (username, full_name, role, generate_password_hash(password)))

    accounts = {
        ("alice", "Everyday"): (insert("INSERT INTO accounts (user_id, name, "
                                       "number, balance) VALUES (?, ?, ?, ?)",
                                       (user_id["alice"], "Everyday",
                                        "US7K2Q-4M1P-93XZ", 1250.40)), 1250.40),
        ("alice", "Savings"): (insert("INSERT INTO accounts (user_id, name, "
                                      "number, balance) VALUES (?, ?, ?, ?)",
                                      (user_id["alice"], "Savings",
                                       "US5R8T-2B6N-10QW", 8400.00)), 8400.00),
        ("bob", "Everyday"): (insert("INSERT INTO accounts (user_id, name, "
                                     "number, balance) VALUES (?, ?, ?, ?)",
                                     (user_id["bob"], "Everyday",
                                      "US3D9F-7H2J-55KL", 320.15)), 320.15),
        ("admin", "Everyday"): (insert("INSERT INTO accounts (user_id, name, "
                                       "number, balance) VALUES (?, ?, ?, ?)",
                                       (user_id["admin"], "Everyday",
                                        "US1A4C-6E8G-77RS", 12500.00)), 12500.00),
    }

    # FIX: номер карты шифруется перед записью, ключ приходит из окружения.
    cards = [
        ("alice", "4111111111111111", "VISA", "09/29", "ALICE WEAVER", ""),
        ("bob", "5555555555554444", "MASTERCARD", "11/28", "BOB NOLAN", "tone-2"),
        ("admin", "5412751234123457", "MASTERCARD", "03/30",
         "LAB ADMINISTRATOR", "tone-3"),
    ]
    for username, number, brand, exp, holder, tone in cards:
        insert("INSERT INTO cards (user_id, number, brand, exp, holder, tone) "
               "VALUES (?, ?, ?, ?, ?, ?)",
               (user_id[username], fernet.encrypt(number.encode()).decode(),
                brand, exp, holder, tone))

    history = [
        ("alice", "Everyday", "2026-10-24", "Coffee House", "out", 4.60),
        ("alice", "Everyday", "2026-10-23", "Salary", "in", 1200.00),
        ("alice", "Everyday", "2026-10-23", "Transfer to Savings", "out", 500.00),
        ("alice", "Savings", "2026-10-23", "Transfer from Everyday", "in", 500.00),
        ("alice", "Everyday", "2026-10-21", "Grocery Market", "out", 63.25),
        ("alice", "Everyday", "2026-10-19", "Cashback", "in", 12.40),
        ("bob", "Everyday", "2026-10-24", "Coffee House", "out", 4.60),
        ("bob", "Everyday", "2026-10-22", "Salary", "in", 980.00),
    ]
    for username, acc_name, day, desc, direction, amount in history:
        account_id, _ = accounts[(username, acc_name)]
        insert("INSERT INTO transactions (user_id, account_id, amount, "
               "direction, description, created) VALUES (?, ?, ?, ?, ?, ?)",
               (user_id[username], account_id, amount, direction, desc, day))


init_db()


# ------------------------------------------------------------------ helpers
def _wants_html():
    """Браузер шлёт Accept: text/html, curl/Postman — */*."""
    return "text/html" in request.headers.get("Accept", "")


def _payload():
    return request.get_json(silent=True) or request.form


def _page(template, **extra):
    """Все страницы сайта проходят через один helper: язык, переводы,
    вариант лабы и флеш-сообщения."""
    data = dict(lang=g.lang, t=texts(), langs=LANGS,
                variant_label=texts()["vuln"])
    for category, message in get_flashed_messages(with_categories=True):
        key = "error" if category == "error" else "message"
        data.setdefault(key, message)
    # шаблоны всегда получают оба ключа — даже если сообщений нет
    data.setdefault("message", None)
    data.setdefault("error", None)
    data.update(extra)
    return render_template(template, **data)


def _current_user():
    username = session.get("user")
    if not username:
        return None
    rows = query("SELECT * FROM users WHERE username = ?", (username,))
    return dict(rows[0]) if rows else None


def _require_user():
    """(пользователь, ответ-отказ): отказ — страница/редирект или 401."""
    user = _current_user()
    if user:
        return user, None
    if _wants_html():
        flash(texts()["err_auth"], "error")
        return None, redirect("/login")
    return None, (jsonify(error="login required"), 401)


def _accounts(user_id):
    return [{"id": r["id"], "name": r["name"], "number": r["number"],
             "balance": money(r["balance"])} for r in _account_rows(user_id)]


def _account_rows(user_id):
    return query("SELECT * FROM accounts WHERE user_id = ? ORDER BY id",
                 (user_id,))


def _transactions(user_id, limit=8):
    rows = query(
        """SELECT t.*, a.name AS account_name FROM transactions t
           JOIN accounts a ON a.id = t.account_id
           WHERE t.user_id = ? ORDER BY t.created DESC, t.id DESC LIMIT ?""",
        (user_id, limit))
    return [{"date": r["created"], "desc": r["description"],
             "account": r["account_name"],
             "amount": signed(r["amount"]) if r["direction"] == "in"
                       else signed(-r["amount"]),
             "in": r["direction"] == "in"} for r in rows]


def _card_brand(number):
    if number.startswith("4"):
        return "VISA"
    if number[:1] in ("5", "2"):
        return "MASTERCARD"
    return "CARD"


# ВАЖНО для лабы: хук регистрируется ДО register_ui (см. конец файла),
# иначе браузерный запрос к "/" перехватит редирект labui на страницу /ui.
@app.before_request
def _site_index():
    if request.path == "/" and request.method == "GET" and _wants_html():
        return _page("home.html", active="home")


@app.get("/")
def index():
    """Для curl и Postman — JSON-описание API; браузер открывает сайт."""
    return jsonify(
        message="ATLAS Bank — A04 Cryptographic Failures (vulnerable)",
        endpoints=["GET /login", "POST /login", "GET /register",
                   "POST /register", "GET /dashboard", "GET /cards",
                   "POST /cards", "GET /transfers", "POST /transfers",
                   "GET /admin", "GET /me", "POST /forgot",
                   "POST /reset/<token>", "GET /_lab/outbox",
                   "GET /_lab/dump"],
        accounts="alice / sunshine, bob / qwerty",
        langs=LANGS,
    )


# --------------------------------------------------------------- витрина
@app.get("/login")
def login_page():
    user = _current_user()
    if user and _wants_html():
        return redirect("/dashboard")
    return _page("login.html", active="")


@app.post("/login")
def login():
    data = _payload()
    rows = query("SELECT * FROM users WHERE username = ?",
                 (data.get("username", ""),))
    stored = rows[0]["password_hash"] if rows else DUMMY_HASH
    # FIX: сравнение хешей scrypt вместо голого MD5, для неизвестного
    # пользователя проверяется хеш-заглушка — время одинаковое
    ok = bool(rows) and check_password_hash(stored, data.get("password", ""))
    if not ok:
        if _wants_html():
            return _page("login.html", active="",
                         error=texts()["err_cred"]), 401
        return jsonify(error="invalid credentials"), 401
    session.clear()
    session["user"] = rows[0]["username"]
    if _wants_html():
        return redirect("/dashboard")
    return jsonify(message="logged in", user=rows[0]["username"],
                   role=rows[0]["role"])


@app.get("/register")
def register_page():
    return _page("register.html", active="")


@app.post("/register")
def register():
    data = _payload()
    tt = texts()
    username = data.get("username", "")
    full_name = (data.get("full_name", "") or "").strip()
    password = data.get("password", "")
    error = None
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username) or not full_name:
        error = tt["err_input"]
    elif len(password) < 8:
        error = tt["err_pass_len"]
    elif password != data.get("password2", password):
        error = tt["err_pass"]
    elif query("SELECT 1 FROM users WHERE username = ?", (username,)):
        error = tt["err_exists"]
    if error:
        if _wants_html():
            return _page("register.html", active="", error=error), 400
        return jsonify(error=error), 400

    user_id = insert("INSERT INTO users (username, full_name, role, "
                     "password_hash) VALUES (?, ?, 'user', ?)",
                     (username, full_name, generate_password_hash(password)))
    number = "US" + "-".join(uuid.uuid4().hex[:4].upper() for _ in range(3))
    insert("INSERT INTO accounts (user_id, name, number, balance) "
           "VALUES (?, 'Everyday', ?, 0)", (user_id, number))
    if _wants_html():
        flash(tt["ok_registered"])
        return redirect("/login")
    return jsonify(message="registered"), 201


# --------------------------------------------------------------- кабинет
@app.get("/dashboard")
def dashboard():
    user, deny = _require_user()
    if deny:
        return deny
    rows = _account_rows(user["id"])
    accounts = _accounts(user["id"])
    total = money(sum(r["balance"] for r in rows))
    return _page("dashboard.html", active="dashboard", user=user,
                 accounts=accounts, total=total,
                 txns=_transactions(user["id"]))


@app.get("/cards")
def cards_list():
    user, deny = _require_user()
    if deny:
        return deny
    rows = query("SELECT * FROM cards WHERE user_id = ? ORDER BY id",
                 (user["id"],))
    # FIX: наружу отдаётся только маска; полный номер в базе зашифрован
    # и в ответ не попадает.
    numbers = [fernet.decrypt(r["number"].encode()).decode() for r in rows]
    if not _wants_html():
        return jsonify([{"number": mask(n), "brand": r["brand"],
                         "exp": r["exp"], "holder": r["holder"]}
                        for n, r in zip(numbers, rows)])
    cards = [{"number": mask(n), "brand": r["brand"], "exp": r["exp"],
              "holder": r["holder"], "tone": r["tone"]}
             for n, r in zip(numbers, rows)]
    return _page("cards.html", active="cards", user=user, cards=cards)


@app.post("/cards")
def add_card():
    user, deny = _require_user()
    if deny:
        return deny
    data = _payload()
    tt = texts()
    number = re.sub(r"[^0-9]", "", data.get("number", ""))
    exp = (data.get("exp", "") or "").strip()
    holder = (data.get("holder", "") or "").strip()
    if not re.fullmatch(r"\d{13,19}", number):
        error = tt["err_card"]
    elif not re.fullmatch(r"\d{2}/\d{2}", exp):
        error = tt["err_exp"]
    elif not holder:
        error = tt["err_input"]
    else:
        error = None
    if error:
        if _wants_html():
            flash(error, "error")
            return redirect("/cards")
        return jsonify(error=error), 400
    insert("INSERT INTO cards (user_id, number, brand, exp, holder, tone) "
           "VALUES (?, ?, ?, ?, ?, ?)",
           (user["id"], fernet.encrypt(number.encode()).decode(),
            _card_brand(number), exp, holder.upper(), "tone-2"))
    if _wants_html():
        flash(tt["ok_card"])
        return redirect("/cards")
    return jsonify(message="card saved", brand=_card_brand(number)), 201


@app.get("/transfers")
def transfers_page():
    user, deny = _require_user()
    if deny:
        return deny
    return _page("transfers.html", active="transfers", user=user,
                 accounts=_accounts(user["id"]),
                 txns=_transactions(user["id"], limit=12))


@app.post("/transfers")
def transfer():
    user, deny = _require_user()
    if deny:
        return deny
    data = _payload()
    tt = texts()
    try:
        from_id = int(data.get("from_account", ""))
        to_id = int(data.get("to_account", ""))
        amount = round(float(data.get("amount", "")), 2)
    except (TypeError, ValueError):
        from_id = to_id = -1
        amount = 0.0

    error = None
    rows = query("SELECT * FROM accounts WHERE user_id = ?", (user["id"],))
    owned = {r["id"]: r for r in rows}
    if from_id not in owned or to_id not in owned:
        error = tt["err_own"]
    elif from_id == to_id:
        error = tt["err_same"]
    elif amount <= 0:
        error = tt["err_amount"]
    elif owned[from_id]["balance"] < amount:
        error = tt["err_funds"]

    if error:
        if _wants_html():
            flash(error, "error")
            return redirect("/transfers")
        return jsonify(error=error), 400

    note = (data.get("note", "") or "").strip()[:60]
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?",
                     (amount, from_id))
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?",
                     (amount, to_id))
        for account_id, direction, label in (
                (from_id, "out", note or f"Transfer to {owned[to_id]['name']}"),
                (to_id, "in", note or f"Transfer from {owned[from_id]['name']}")):
            conn.execute("INSERT INTO transactions (user_id, account_id, "
                         "amount, direction, description, created) "
                         "VALUES (?, ?, ?, ?, ?, date('now'))",
                         (user["id"], account_id, amount, direction, label))
        conn.commit()

    if _wants_html():
        flash(tt["ok_transfer"])
        return redirect("/transfers")
    return jsonify(message="transfer completed", amount=money(amount))


@app.get("/admin")
def admin_page():
    user, deny = _require_user()
    if deny:
        return deny
    tt = texts()
    if user["role"] != "admin":
        if _wants_html():
            return _page("error.html", active="", title=tt["err_403_t"],
                         message=tt["err_403_m"]), 403
        return jsonify(error="administrator access required"), 403

    rows = query("""SELECT u.username, u.full_name, u.role,
                           COUNT(a.id) AS accounts,
                           COALESCE(SUM(a.balance), 0) AS balance
                    FROM users u LEFT JOIN accounts a ON a.user_id = u.id
                    GROUP BY u.id ORDER BY u.id""")
    users = [{"username": r["username"], "full_name": r["full_name"],
              "role": r["role"], "accounts": r["accounts"],
              "balance": money(r["balance"])} for r in rows]
    return _page("admin.html", active="admin", user=user, users=users,
                 flag=FLAG if user["role"] == "admin" else None)


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.get("/me")
def me():
    """JSON-статус сессии: по нему в SOLUTION проверяют захват админки."""
    user = _current_user()
    if not user:
        return jsonify(error="login required"), 401
    result = {"user": user["username"], "role": user["role"]}
    if user["role"] == "admin":
        result["flag"] = FLAG
    return jsonify(result)


# FIX: токен сброса пароля — криптографически стойкая случайная строка.
# В базе хранится только его SHA-256, со сроком жизни и одноразовостью:
# зная имя пользователя, токен не вычислить.
@app.get("/forgot")
def forgot_page():
    return _page("forgot.html", active="")


@app.post("/forgot")
def forgot():
    data = _payload()
    username = data.get("username", "")
    rows = query("SELECT username FROM users WHERE username = ?", (username,))
    if rows:
        token = secrets.token_urlsafe(32)
        query("INSERT INTO reset_tokens (token_hash, username, expires_at, "
              "used) VALUES (?, ?, ?, 0)",
              (sha256(token), username, time.time() + RESET_TTL_SECONDS),
              commit=True)
        OUTBOX.append({"to": username, "link": f"/reset/{token}"})
    if _wants_html():
        flash(texts()["ok_sent"])
        return redirect("/forgot")
    return jsonify(message="если пользователь существует, ссылка отправлена")


@app.get("/reset/<token>")
def reset_page(token):
    if not _token_user(token):
        return _page("reset.html", active="", error=texts()["err_token"]), 404
    return _page("reset.html", active="")


@app.post("/reset/<token>")
def reset(token):
    data = _payload()
    tt = texts()
    new_password = data.get("password", "") or data.get("new_password", "")
    if len(new_password) < 8:
        error = tt["err_pass_len"]
    elif new_password != data.get("password2", new_password):
        error = tt["err_pass"]
    else:
        error = None
    if error:
        if _wants_html():
            return _page("reset.html", active="", error=error), 400
        return jsonify(error=error), 400

    username = _token_user(token)
    if not username:
        if _wants_html():
            return _page("reset.html", active="", error=tt["err_token"]), 404
        return jsonify(error="invalid token"), 404
    query("UPDATE reset_tokens SET used = 1 WHERE token_hash = ?",
          (sha256(token),), commit=True)
    # FIX: новый пароль тоже хранится стойким хешем с солью
    query("UPDATE users SET password_hash = ? WHERE username = ?",
          (generate_password_hash(new_password), username), commit=True)
    if _wants_html():
        flash(tt["ok_reset"])
        return redirect("/login")
    return jsonify(message="password changed")


def _token_user(token):
    """FIX: токен ищется по хешу; просроченный или уже использованный
    не подходит."""
    rows = query("SELECT * FROM reset_tokens WHERE token_hash = ?",
                 (sha256(token),))
    if not rows or rows[0]["used"] or rows[0]["expires_at"] < time.time():
        return None
    return rows[0]["username"]


# ------------------------------------------------- служебное для лабы
@app.get("/_lab/outbox")
def lab_outbox():
    """Имитация почтового ящика: показывает «письма» со ссылками сброса."""
    return jsonify(OUTBOX)


@app.get("/_lab/dump")
def lab_dump():
    """Имитация утечки базы: показывает, как данные лежат в хранилище."""
    users = [dict(r) for r in query(
        "SELECT username, full_name, role, password_hash FROM users")]
    cards = [dict(username=r["username"], number=r["number"], exp=r["exp"])
             for r in query("SELECT u.username, c.number, c.exp FROM cards c "
                            "JOIN users u ON u.id = c.user_id ORDER BY c.id")]
    tokens = [dict(r) for r in query(
        "SELECT token_hash, username, expires_at, used FROM reset_tokens")]
    return jsonify(users=users, cards=cards, reset_tokens=tokens)


@app.errorhandler(404)
def not_found(exc):
    tt = texts()
    if _wants_html():
        return _page("error.html", active="", title=tt["err_404_t"],
                     message=tt["err_404_m"]), 404
    return jsonify(error="not found"), 404


@app.errorhandler(500)
def server_error(exc):
    tt = texts()
    if _wants_html():
        return _page("error.html", active="", title=tt["err_500_t"],
                     message=tt["err_500_m"]), 500
    return jsonify(error="internal error"), 500


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402

register_ui(
    app, 'A04 Cryptographic Failures — fixed',
    notes='Сайт ATLAS Bank открывается на «/» (переключатель EN/RU/UZ — в '
          'шапке). Кабинет: /dashboard, карты: /cards, переводы: /transfers. '
          'Здесь — консоль лабы: эндпоинты и ответы сервера.',
    presets={
        'POST /login': [('alice', {'username': 'alice', 'password': 'sunshine'})],
        'POST /register': [('новый клиент',
                            {'full_name': 'Carol Smith', 'username': 'carol',
                             'password': 'Str0ng-pass-1',
                             'password2': 'Str0ng-pass-1'})],
        'POST /cards': [('тестовая карта',
                         {'number': '4242424242424242', 'exp': '09/29',
                          'holder': 'Carol Smith'})],
        'POST /transfers': [('50 на накопительный',
                             {'from_account': '1', 'to_account': '2',
                              'amount': '50.00', 'note': 'lab'})],
        'POST /forgot': [('alice', {'username': 'alice'})],
        'GET /me': [('статус сессии', '/me')],
        'GET /_lab/dump': [('утечка базы', '/_lab/dump')],
        'GET /_lab/outbox': [('почтовый ящик', '/_lab/outbox')],
    },
    uz={'notes': 'ATLAS Bank sayti «/» manzilida (EN/RU/UZ almashtirgichi '
                 'boshqaruv panelida). Kabinet: /dashboard, kartalar: /cards, '
                 'o‘tkazmalar: /transfers. Bu yerda laboratoriya konsoli.',
        'presets': {
            'POST /login': [('alice', {'username': 'alice',
                                       'password': 'sunshine'})],
            'POST /register': [('yangi mijoz',
                                {'full_name': 'Carol Smith', 'username': 'carol',
                                 'password': 'Str0ng-pass-1',
                                 'password2': 'Str0ng-pass-1'})],
            'POST /cards': [('test kartasi',
                             {'number': '4242424242424242', 'exp': '09/29',
                              'holder': 'Carol Smith'})],
            'POST /transfers': [('jamg‘armaga 50',
                                 {'from_account': '1', 'to_account': '2',
                                  'amount': '50.00', 'note': 'lab'})],
            'POST /forgot': [('alice', {'username': 'alice'})]}},
    en={'notes': 'The ATLAS Bank site opens at "/" (EN/RU/UZ switcher in the '
                 'header). Banking area: /dashboard, cards: /cards, transfers: '
                 '/transfers. This is the lab console: endpoints and responses.',
        'presets': {
            'POST /login': [('alice', {'username': 'alice',
                                       'password': 'sunshine'})],
            'POST /register': [('new customer',
                                {'full_name': 'Carol Smith', 'username': 'carol',
                                 'password': 'Str0ng-pass-1',
                                 'password2': 'Str0ng-pass-1'})],
            'POST /cards': [('test card',
                             {'number': '4242424242424242', 'exp': '09/29',
                              'holder': 'Carol Smith'})],
            'POST /transfers': [('50 to savings',
                                 {'from_account': '1', 'to_account': '2',
                                  'amount': '50.00', 'note': 'lab'})],
            'POST /forgot': [('alice', {'username': 'alice'})]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
