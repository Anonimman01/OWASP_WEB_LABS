"""A05 Injection — ИСПРАВЛЕННАЯ версия.

Сайт авиакомпании Skyline: те же страницы и данные, что в vulnerable,
но инъекции закрыты. Отличия от vulnerable/app.py помечены FIX:

  FIX 1 — вход: параметризованный запрос, пароль сверяется в коде;
  FIX 2 — поиск: значения передаются отдельно от текста запроса,
          ошибки SQL не показываются наружу;
  FIX 3 — проверка узла: оболочка не используется, имя проверяется
          белым списком и резолвится средствами Python.

Только для обучения. Не публикуйте это приложение в интернете.
"""
import hmac
import os
import re
import socket
import sqlite3
import tempfile
import uuid
from contextlib import closing

from flask import (Flask, flash, get_flashed_messages, g, jsonify, redirect,
                   render_template, request, session)

from sky import (BRAND, LANGS, city, date_fmt, dur, price, register_lang,
                 t as texts)

app = Flask(__name__)
app.secret_key = os.urandom(32)

register_lang(app)

DB_PATH = os.path.join(tempfile.gettempdir(),
                       f"a05_fixed_{uuid.uuid4().hex}.db")

FLAG_LOGIN = "FLAG{a05_sqli_login_bypass}"
FLAG_HIDDEN = "FLAG{a05_hidden_flight}"
FLAG_UNION = "FLAG{a05_sqli_union_dump}"
# FIX 3: флаг больше не лежит в окружении — выполнить произвольную команду
# в этой версии просто нечем.

SEED_USERS = [
    ("alice", "Alice Fern", "alice123", "user", "нет секретов"),
    ("bob", "Bob Nolan", "bob123", "user", "нет секретов"),
    ("admin", "Lab Administrator", "Adm1n-lab-pass", "admin", FLAG_UNION),
]

SEED_FLIGHTS = [
    ("SK 104", "TAS", "IST", "2026-11-14", "07:40", "09:55", 255, 214, 38, 0, 0, ""),
    ("SK 217", "IST", "DXB", "2026-11-14", "12:15", "17:30", 315, 302, 12, 0, 0, ""),
    ("SK 330", "TAS", "LHR", "2026-11-15", "05:50", "08:20", 450, 418, 21, 1, 0, "via IST"),
    ("SK 455", "DXB", "BER", "2026-11-15", "10:10", "14:05", 355, 276, 44, 0, 0, ""),
    ("SK 512", "ALA", "FCO", "2026-11-16", "14:35", "17:50", 375, 329, 9, 1, 0, "via IST"),
    ("SK 900", "TAS", "IST", "2026-11-17", "02:15", "04:30", 255, 1999, 2, 0, 1,
     f"Private charter, not for sale. {FLAG_HIDDEN}"),
]


def init_db():
    query("CREATE TABLE users ("
          "id INTEGER PRIMARY KEY AUTOINCREMENT, "
          "username TEXT UNIQUE NOT NULL, "
          "full_name TEXT NOT NULL, "
          "password TEXT NOT NULL, "
          "role TEXT NOT NULL, "
          "secret TEXT NOT NULL)", commit=True)
    query("CREATE TABLE flights ("
          "id INTEGER PRIMARY KEY AUTOINCREMENT, "
          "flight_no TEXT NOT NULL, "
          "origin TEXT NOT NULL, "
          "destination TEXT NOT NULL, "
          "dep_date TEXT NOT NULL, "
          "dep_time TEXT NOT NULL, "
          "arr_time TEXT NOT NULL, "
          "duration_min INTEGER NOT NULL, "
          "price INTEGER NOT NULL, "
          "seats INTEGER NOT NULL, "
          "stops INTEGER NOT NULL DEFAULT 0, "
          "hidden INTEGER NOT NULL DEFAULT 0, "
          "note TEXT NOT NULL DEFAULT '')", commit=True)
    query("CREATE TABLE bookings ("
          "id INTEGER PRIMARY KEY AUTOINCREMENT, "
          "user_id INTEGER NOT NULL, "
          "flight_id INTEGER NOT NULL, "
          "passengers INTEGER NOT NULL, "
          "created TEXT NOT NULL DEFAULT (datetime('now')))", commit=True)

    for username, full_name, password, role, secret in SEED_USERS:
        query("INSERT INTO users (username, full_name, password, role, secret) "
              "VALUES (?, ?, ?, ?, ?)",
              (username, full_name, password, role, secret), commit=True)

    for row in SEED_FLIGHTS:
        query("INSERT INTO flights (flight_no, origin, destination, dep_date, "
              "dep_time, arr_time, duration_min, price, seats, stops, hidden, "
              "note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              row, commit=True)


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


init_db()


# FIX 2 (защита в глубину): запрещаем выполнение скриптов и убираем
# возможность «угадать» тип ответа. Самое важное — экранирование данных
# делает шаблонизатор Jinja при выводе.
@app.after_request
def security_headers(resp):
    # Только учебной странице /ui (не часть уязвимости) разрешены свои
    # inline-скрипты и запросы на свой адрес.
    if request.path == "/ui":
        resp.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
            "connect-src 'self'; base-uri 'none'")
    else:
        resp.headers["Content-Security-Policy"] = (
            "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'")
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


# ------------------------------------------------------------------ helpers
def _wants_html():
    """Браузер шлёт Accept: text/html, curl/Postman — */*."""
    return "text/html" in request.headers.get("Accept", "")


def _payload():
    return request.get_json(silent=True) or request.form or request.args


def _page(template, **extra):
    """Все страницы сайта проходят через один helper: язык, переводы,
    вариант лабы и флеш-сообщения."""
    data = dict(lang=g.lang, t=texts(), langs=LANGS, brand=BRAND,
                variant_label=texts()["fixed"])
    for category, message in get_flashed_messages(with_categories=True):
        key = "flash_err" if category == "error" else "flash_ok"
        data.setdefault(key, message)
    data.setdefault("flash_ok", None)
    data.setdefault("flash_err", None)
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


def _require_admin():
    user, deny = _require_user()
    if deny:
        return user, deny
    if user["role"] == "admin":
        return user, None
    if _wants_html():
        return user, (_page("error.html", active="", title=texts()["err_403_t"],
                            message=texts()["err_403_m"]), 403)
    return user, (jsonify(error="administrator access required"), 403)


def _flight_dict(row, detail=False):
    data = {"id": row["id"], "flight_no": row["flight_no"],
            "origin": row["origin"], "destination": row["destination"],
            "origin_city": city(row["origin"]),
            "destination_city": city(row["destination"]),
            "dep_date": row["dep_date"], "dep_date_label": date_fmt(row["dep_date"]),
            "dep_time": row["dep_time"], "price": price(row["price"]),
            "seats": row["seats"] if "seats" in row.keys() else None}
    if detail:
        data.update(arr_time=row["arr_time"],
                    duration=dur(row["duration_min"]),
                    seats=row["seats"],
                    stops_label=texts()["direct"] if row["stops"] == 0
                               else texts()["one_stop"],
                    note=row["note"], hidden=bool(row["hidden"]),
                    tag_charter=texts()["tag_charter"])
    return data


def _search_flights(origin, dest, date, max_price):
    # FIX 2: параметры передаются отдельно от текста запроса — данные
    # не могут изменить его структуру. Имена таблиц и столбцов из ввода
    # не берутся, значения ограничены по длине и формату.
    clauses = ["origin LIKE ?", "destination LIKE ?"]
    params = [f"%{origin[:64]}%", f"%{dest[:64]}%"]
    try:
        limit = max(0, min(int(max_price), 1_000_000))
    except (TypeError, ValueError):
        limit = 999999
    clauses.append("price <= ?")
    params.append(limit)
    if date:
        clauses.append("dep_date = ?")
        params.append(date[:32])
    clauses.append("hidden = 0")
    sql = ("SELECT id, flight_no, origin, destination, dep_date, dep_time, price "
           "FROM flights WHERE " + " AND ".join(clauses) +
           " ORDER BY dep_date, dep_time")
    return query(sql, params)


# ВАЖНО для лабы: хук регистрируется ДО register_ui (см. конец файла),
# иначе браузерный запрос к "/" перехватит редирект labui на страницу /ui.
@app.before_request
def _site_index():
    if request.path == "/" and request.method == "GET" and _wants_html():
        popular = query("SELECT * FROM flights WHERE hidden = 0 "
                        "ORDER BY dep_date, price LIMIT 3")
        return _page("home.html", active="home",
                     popular=[_flight_dict(r) for r in popular])


@app.get("/")
def index():
    """Для curl и Postman — JSON-описание API; браузер открывает сайт."""
    return jsonify(
        message="Skyline Air — A05 Injection (fixed)",
        endpoints=["GET /flights", "GET /flight/<id>",
                   "POST /flight/<id>/book", "GET /login", "POST /login",
                   "GET /register", "POST /register", "GET /trips",
                   "GET /admin", "POST /admin/check", "GET /me"],
        accounts="alice / alice123",
        langs=LANGS,
    )


# --------------------------------------------------------------- поиск
@app.get("/flights")
def flights():
    origin = request.args.get("from", "")
    dest = request.args.get("to", "")
    date = request.args.get("date", "")
    max_price = request.args.get("max_price", "").strip()
    try:
        rows = _search_flights(origin, dest, date, max_price)
    except sqlite3.Error:
        # FIX 2: текст ошибки SQL наружу не уходит — только общее сообщение.
        if _wants_html():
            return _page("results.html", active="routes", flights=[],
                         q_origin=origin, q_dest=dest, q_date=date,
                         q_max=request.args.get("max_price", ""),
                         sql_error=texts()["err_query"]), 500
        return jsonify(error=texts()["err_query"]), 500
    found = [_flight_dict(r) for r in rows]
    if not _wants_html():
        return jsonify(found)
    return _page("results.html", active="routes", flights=found,
                 q_origin=origin, q_dest=dest, q_date=date,
                 q_max=request.args.get("max_price", ""), sql_error=None)


@app.get("/flight/<int:flight_id>")
def flight_detail(flight_id):
    rows = query("SELECT * FROM flights WHERE id = ?", (flight_id,))
    if not rows:
        if _wants_html():
            tt = texts()
            return _page("error.html", active="", title=tt["err_404_t"],
                         message=tt["err_404_m"]), 404
        return jsonify(error="not found"), 404
    data = _flight_dict(rows[0], detail=True)
    if not _wants_html():
        return jsonify(data)
    return _page("flight.html", active="routes", flight=data)


@app.post("/flight/<int:flight_id>/book")
def book_flight(flight_id):
    user, deny = _require_user()
    if deny:
        return deny
    tt = texts()
    try:
        passengers = int(_payload().get("passengers", 1))
    except (TypeError, ValueError):
        passengers = 0
    rows = query("SELECT * FROM flights WHERE id = ?", (flight_id,))
    flight = rows[0] if rows else None
    if flight is None:
        if _wants_html():
            return _page("error.html", active="", title=tt["err_404_t"],
                         message=tt["err_404_m"]), 404
        return jsonify(error="not found"), 404
    if not 1 <= passengers <= 4 or flight["seats"] < passengers:
        if _wants_html():
            flash(tt["no_seats"], "error")
            return redirect(f"/flight/{flight_id}")
        return jsonify(error=tt["no_seats"]), 400
    insert("INSERT INTO bookings (user_id, flight_id, passengers) "
           "VALUES (?, ?, ?)", (user["id"], flight["id"], passengers))
    query("UPDATE flights SET seats = seats - ? WHERE id = ?",
          (passengers, flight_id), commit=True)
    if _wants_html():
        flash(tt["booked_ok"])
        return redirect("/trips")
    return jsonify(message="booked", flight=flight["flight_no"],
                   passengers=passengers), 201


@app.get("/trips")
def trips():
    user, deny = _require_user()
    if deny:
        return deny
    rows = query(
        """SELECT b.passengers, b.created, f.* FROM bookings b
           JOIN flights f ON f.id = b.flight_id
           WHERE b.user_id = ? ORDER BY b.id DESC""", (user["id"],))
    found = []
    for row in rows:
        item = _flight_dict(row, detail=True)
        item["passengers"] = row["passengers"]
        found.append(item)
    if not _wants_html():
        return jsonify(found)
    return _page("trips.html", active="trips", trips=found)


# --------------------------------------------------------------- вход
@app.get("/login")
def login_page():
    user = _current_user()
    if user and _wants_html():
        return redirect("/trips" if user["role"] != "admin" else "/admin")
    return _page("login.html", active="")


@app.post("/login")
def login():
    data = _payload()
    username, password = str(data.get("username", "")), str(data.get("password", ""))
    # FIX 1: данные передаются отдельно от запроса, пароль сверяется в коде
    # через hmac.compare_digest — SQL не может изменить условие выборки.
    rows = query("SELECT username, role, secret, password FROM users "
                 "WHERE username = ?", (username,))
    if not rows or not hmac.compare_digest(rows[0]["password"], password):
        if _wants_html():
            return _page("login.html", active="",
                         error=texts()["err_cred"]), 401
        return jsonify(error="invalid credentials"), 401
    session.clear()
    session["user"] = rows[0]["username"]
    if not _wants_html():
        result = {"message": "logged in", "user": rows[0]["username"],
                  "role": rows[0]["role"]}
        if rows[0]["role"] == "admin":
            result["flag"] = FLAG_LOGIN
        return jsonify(result)
    return redirect("/admin" if rows[0]["role"] == "admin" else "/trips")


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

    query("INSERT INTO users (username, full_name, password, role, secret) "
          "VALUES (?, ?, ?, 'user', 'нет секретов')",
          (username, full_name, password), commit=True)
    if _wants_html():
        flash(tt["ok_registered"])
        return redirect("/login")
    return jsonify(message="registered"), 201


@app.get("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.get("/me")
def me():
    """JSON-статус сессии: по нему в SOLUTION проверяют вход админом."""
    user = _current_user()
    if not user:
        return jsonify(error="login required"), 401
    result = {"user": user["username"], "role": user["role"]}
    if user["role"] == "admin":
        result["flag"] = FLAG_LOGIN
    return jsonify(result)


# --------------------------------------------------------------- админка
@app.get("/admin")
def admin_page():
    user, deny = _require_admin()
    if deny:
        return deny
    users = [dict(r) for r in query(
        "SELECT username, full_name, role FROM users ORDER BY id")]
    all_flights = [_flight_dict(r, detail=True)
                   for r in query("SELECT * FROM flights ORDER BY dep_date")]
    if not _wants_html():
        return jsonify(users=users, flights=all_flights,
                       flag=FLAG_LOGIN)
    return _page("admin.html", active="admin", users=users,
                 flights=all_flights, check_out=None, check_host="",
                 flag=FLAG_LOGIN)


@app.post("/admin/check")
def admin_check():
    user, deny = _require_admin()
    if deny:
        return deny
    host = (_payload().get("host", "") or "").strip()
    # FIX 3: оболочка не используется. Имя проходит белый список
    # [A-Za-z0-9.-] и резолвится средствами Python — подстановка
    # разделителей команд (';', '&', '|', '$()') невозможна.
    if not re.fullmatch(r"[A-Za-z0-9.-]{1,253}", host):
        out = f"invalid host: {host!r} (allowed: letters, digits, dot, dash)"
    else:
        try:
            out = f"{host} -> {socket.gethostbyname(host)}"
        except OSError as exc:
            out = f"{host}: {exc}"
    if not _wants_html():
        return jsonify(host=host, output=out)
    users = [dict(r) for r in query(
        "SELECT username, full_name, role FROM users ORDER BY id")]
    all_flights = [_flight_dict(r, detail=True)
                   for r in query("SELECT * FROM flights ORDER BY dep_date")]
    return _page("admin.html", active="admin", users=users,
                 flights=all_flights, check_out=out, check_host=host,
                 flag=FLAG_LOGIN)


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
    app, 'A05 Injection — fixed',
    notes='Сайт Skyline открывается на «/» (переключатель EN/RU/UZ — в '
          'шапке). Поиск: /flights, карточка рейса: /flight/1, мои поездки: '
          '/trips, админка: /admin. Здесь — консоль лабы: эндпоинты и ответы '
          'сервера.',
    presets={
        'GET /flights': [('рейсы TAS → IST', '?from=TAS&to=IST'),
                         ('все рейсы', '?from=')],
        'GET /flight/1': [('SK 104', '/flight/1')],
        'POST /flight/1/book': [('бронь на 1', {'passengers': 1})],
        'POST /login': [('alice', {'username': 'alice',
                                   'password': 'alice123'}),
                        ("попытка: admin'--", {'username': "admin'--",
                                               'password': 'x'})],
        'POST /register': [('новый пассажир',
                            {'full_name': 'Carol Smith', 'username': 'carol',
                             'password': 'Str0ng-pass-1',
                             'password2': 'Str0ng-pass-1'})],
        'POST /admin/check': [('localhost', {'host': 'localhost'})],
        'GET /me': [('статус сессии', '/me')],
    },
    uz={'notes': 'Skyline sayti «/» manzilida (EN/RU/UZ almashtirgichi '
                 'boshqaruv panelida). Qidiruv: /flights, reys: /flight/1, '
                 'sayohatlarim: /trips, admin: /admin. Bu yerda '
                 'laboratoriya konsoli.',
        'presets': {
            'GET /flights': [('TAS → IST', '?from=TAS&to=IST'),
                             ('barcha reyslar', '?from=')],
            'POST /login': [('alice', {'username': 'alice',
                                       'password': 'alice123'})],
            'POST /admin/check': [('localhost', {'host': 'localhost'})]}},
    en={'notes': 'The Skyline site opens at "/" (EN/RU/UZ switcher in the '
                 'header). Search: /flights, a flight: /flight/1, my trips: '
                 '/trips, admin: /admin. This is the lab console: endpoints '
                 'and server responses.',
        'presets': {
            'GET /flights': [('TAS → IST', '?from=TAS&to=IST'),
                             ('all flights', '?from=')],
            'POST /login': [('alice', {'username': 'alice',
                                       'password': 'alice123'}),
                            ("attempt: admin'--", {'username': "admin'--",
                                                   'password': 'x'})],
            'POST /admin/check': [('localhost', {'host': 'localhost'})]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
