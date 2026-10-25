"""
A09:2025 Security Logging and Alerting Failures — УЯЗВИМАЯ версия.

Шесть дефектов логирования и оповещений:
1. Неудачные входы и отказы в доступе (403) не попадают в лог
2. Log injection: пользовательский ввод пишется в лог как есть (CRLF)
3. Пароли и идентификаторы сессий пишутся в лог
4. Нет оповещений: перебор пароля никого не тревожит
5. Лог доступен без авторизации
6. Нет журнала аудита значимых действий и нет защиты логов от подмены

Только для локального запуска!
"""
import os
import re
import secrets
from datetime import datetime
from functools import wraps

from flask import Flask, Response, jsonify, make_response, request

app = Flask(__name__)
app.json.ensure_ascii = False  # кириллица в JSON читается без \uXXXX

# Префикс нужен, чтобы cookie vulnerable и fixed (один хост 127.0.0.1,
# разные порты) не перезаписывали друг друга в браузере
PREFIX = "a09v_"
ADMIN_PASSWORD = "Adm1n-L0g-Pass!"

USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "bob": {"password": "bob123", "role": "user"},
    "admin": {"password": ADMIN_PASSWORD, "role": "admin"},
}
BALANCES, SESSIONS = {}, {}
LOG = []  # строки лога, как в обычном текстовом файле
# «Истина» для проверки лабы: что на самом деле происходило в системе.
# Приложение само этим не пользуется, это нужно только эндпоинтам оценки.
TRUTH = {"failed": 0, "real_logins": set()}


def now():
    return datetime.now().isoformat(timespec="seconds")


def log(level, message):
    LOG.append(f"{now()} {level} {message}")


def reset_state():
    BALANCES.clear()
    BALANCES.update({"alice": 1000, "bob": 1000, "admin": 5000})
    SESSIONS.clear()
    LOG.clear()
    TRUTH["failed"] = 0
    TRUTH["real_logins"] = {"admin"}
    log("INFO", "app started")
    # Администратор «уже работал» до вас — его вход есть в логе
    sid = secrets.token_hex(8)
    SESSIONS[sid] = "admin"
    log("INFO", f"login ok user=admin password={ADMIN_PASSWORD} sid={sid}")  # ДЕФЕКТ 3


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


@app.get("/")
def index():
    html = """<h1>A09 Logging and Alerting Failures — vulnerable</h1>
<p>API: curl / Burp / Postman. Cookie a09v_sid выставляется автоматически.</p>
<pre>
POST /login            {"username","password"}
GET  /me
POST /transfer         {"to","amount"}
POST /feedback         {"name","message"}
GET  /admin/export
GET  /logs
GET  /logs/summary
GET  /alerts
POST /_lab/tamper       {"index","text"}   помощник: правка файла лога
POST /reset-lab
</pre>"""
    return Response(html, mimetype="text/html")


@app.post("/reset-lab")
def reset_lab():
    reset_state()
    return jsonify(ok=True)


@app.post("/login")
def login():
    d = body()
    username, password = d.get("username"), d.get("password")
    user = USERS.get(username)
    if not user or user["password"] != password:
        TRUTH["failed"] += 1
        # ДЕФЕКТ 1: неудачный вход нигде не фиксируется — перебор пароля
        # не оставляет в логе ни одной строки
        return jsonify(error="неверный логин или пароль"), 401
    sid = secrets.token_hex(8)
    SESSIONS[sid] = username
    TRUTH["real_logins"].add(username)
    # ДЕФЕКТ 3: в лог попадают пароль и идентификатор сессии
    log("INFO", f"login ok user={username} password={password} sid={sid}")
    resp = jsonify(ok=True, user=username)
    resp.set_cookie(PREFIX + "sid", sid)
    return resp


@app.get("/me")
@login_required
def me(user):
    return jsonify(user=user, role=USERS[user]["role"], balance=BALANCES[user])


@app.post("/transfer")
@login_required
def transfer(user):
    d = body()
    to, amount = d.get("to"), d.get("amount")
    if to not in USERS or not isinstance(amount, int) or amount <= 0:
        return jsonify(error="нужны to (пользователь) и amount (целое > 0)"), 400
    if BALANCES[user] < amount:
        return jsonify(error="недостаточно средств"), 400
    BALANCES[user] -= amount
    BALANCES[to] += amount
    # ДЕФЕКТ 6: денежный перевод ничем не фиксируется — кто, кому и сколько
    # перевёл, потом не восстановить
    return jsonify(ok=True, balance=BALANCES[user])


@app.post("/feedback")
def feedback():
    d = body()
    # ДЕФЕКТ 2: пользовательский ввод пишется в лог без какой-либо обработки.
    # Символ перевода строки в message создаёт в файле «новую запись».
    log("INFO", f"feedback from={d.get('name', 'аноним')}: {d.get('message', '')}")
    return jsonify(ok=True, message="спасибо за отзыв")


@app.get("/admin/export")
@login_required
def admin_export(user):
    if USERS[user]["role"] != "admin":
        # ДЕФЕКТ 1 (продолжение): отказ в доступе тоже не логируется
        return jsonify(error="только для администратора"), 403
    return jsonify(flag="FLAG{a09_secrets_in_logs}", balances=BALANCES)


@app.get("/logs")
def logs():
    # ДЕФЕКТ 5: лог отдаётся любому без авторизации. А в нём — пароль
    # администратора и действующая сессия (см. ДЕФЕКТ 3)
    return Response("\n".join(LOG) + "\n", mimetype="text/plain; charset=utf-8")


LOGIN_RE = re.compile(r"login ok user=(\S+)")


@app.get("/logs/summary")
def logs_summary():
    """«Анализатор»: собирает из лога список пользователей, которые входили."""
    seen = []
    for line in "\n".join(LOG).splitlines():
        m = LOGIN_RE.search(line)
        if m and m.group(1) not in seen:
            seen.append(m.group(1))
    resp = {"successful_logins": seen}
    if any(u not in TRUTH["real_logins"] for u in seen):
        resp["flag"] = "FLAG{a09_log_forged}"
        resp["note"] = "в логе есть вход пользователя, которого на самом деле не было"
    return jsonify(resp)


@app.get("/alerts")
def alerts():
    # ДЕФЕКТ 4: оповещений нет вообще — порогов, счётчиков и уведомлений в
    # приложении не предусмотрено. Список всегда пуст, что бы ни происходило.
    resp = {"alerts": []}
    if TRUTH["failed"] >= 10:
        resp["flag"] = "FLAG{a09_attack_unnoticed}"
        resp["note"] = (f"за это время было {TRUTH['failed']} неудачных входов, "
                        "а оповещений нет — атаку никто не заметил")
    return jsonify(resp)


@app.post("/_lab/tamper")
def lab_tamper():
    """ЛАБ-ПОМОЩНИК: имитирует злоумышленника с доступом к файлу лога.
    {"index": N, "text": "новая строка"}; "text": null — удалить строку."""
    d = body()
    i = d.get("index")
    if not isinstance(i, int) or not 0 <= i < len(LOG):
        return jsonify(error=f"index от 0 до {len(LOG) - 1}"), 400
    # ДЕФЕКТ 6 (продолжение): ни хеш-цепочки, ни подписи, ни внешней копии —
    # правку или удаление строки обнаружить нечем
    if d.get("text") is None:
        LOG.pop(i)
    else:
        LOG[i] = str(d["text"])
    return jsonify(ok=True, lines=len(LOG))


from labui import register_ui  # noqa: E402  (учебный интерфейс /ui)
register_ui(app, "A09 Logging and Alerting Failures — vulnerable",
            notes="Аккаунты: alice / alice123, bob / bob123. Пароль admin найдите сами.",
            presets={
                "POST /login": [("alice", {"username": "alice", "password": "alice123"}),
                                ("bob", {"username": "bob", "password": "bob123"})],
                "POST /transfer": [("alice → bob 50", {"to": "bob", "amount": 50})],
                "POST /feedback": [("отзыв", {"name": "Аня", "message": "Всё отлично"})],
                "POST /_lab/tamper": [("удалить строку 1", {"index": 1, "text": None})],
            },
            uz={"notes": "Akkauntlar: alice / alice123, bob / bob123. Admin parolini oʻzingiz toping.",
                "presets": {
                    "POST /feedback": [("fikr", {"name": "Ali", "message": "Hammasi yaxshi"})],
                    "POST /_lab/tamper": [("1-qatorni oʻchirish", {"index": 1, "text": None})],
                }})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
