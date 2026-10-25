"""
A09:2025 Security Logging and Alerting Failures — ИСПРАВЛЕННАЯ версия.

Исправления помечены комментариями "# FIX N"; номера совпадают с
"# ДЕФЕКТ N" в vulnerable/app.py. Только для локального запуска!
"""
import hashlib
import json
import os
import re
import secrets
import time
from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # кириллица в JSON читается без \uXXXX

PREFIX = "a09f_"
ADMIN_PASSWORD = "Adm1n-L0g-Pass!"

USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "bob": {"password": "bob123", "role": "user"},
    "admin": {"password": ADMIN_PASSWORD, "role": "admin"},
}
BALANCES, SESSIONS, ALERTS = {}, {}, []
LOG = []  # записи журнала (словари), связанные хеш-цепочкой
RECENT = {}  # (тип события, ключ) -> времена недавних событий
TRUTH = {"failed": 0, "real_logins": set()}  # для эндпоинтов оценки лабы

# FIX 4: пороги оповещений — сколько событий за какое окно считается тревогой
WINDOW_SEC = 60
THRESHOLDS = {"login_failed": 5, "access_denied": 3}
ZERO = "0" * 64


def clean(value, limit=200):
    # FIX 2: управляющие символы (в том числе CR/LF) заменяются пробелом,
    # длина ограничена — подделать «новую строку» нельзя
    return re.sub(r"[\x00-\x1f\x7f]", " ", str(value))[:limit]


def digest(entry):
    payload = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def audit(event, outcome, user=None, **detail):
    """FIX 1/6: единая структурная запись: кто, что, когда, откуда, итог."""
    entry = {
        "seq": len(LOG) + 1,
        "ts": datetime.now().isoformat(timespec="seconds"),
        "event": event,
        "outcome": outcome,
        "user": clean(user) if user is not None else None,
        "ip": request.remote_addr,
        "detail": {k: clean(v) for k, v in detail.items()},
        # FIX 6: каждая запись хранит хеш предыдущей — правка или удаление
        # в середине журнала ломает цепочку
        "prev": LOG[-1]["hash"] if LOG else ZERO,
    }
    entry["hash"] = digest(entry)
    LOG.append(entry)
    return entry


def raise_if_burst(kind, key, alert_type):
    # FIX 4: считаем события за окно и поднимаем тревогу при превышении порога
    t = time.time()
    hits = [x for x in RECENT.get((kind, key), []) if t - x < WINDOW_SEC] + [t]
    RECENT[(kind, key)] = hits
    if len(hits) >= THRESHOLDS[kind] and not any(
            a["type"] == alert_type and a["key"] == key and not a["acknowledged"]
            for a in ALERTS):
        ALERTS.append({"type": alert_type, "key": key, "count": len(hits),
                       "window_sec": WINDOW_SEC, "acknowledged": False,
                       "ts": datetime.now().isoformat(timespec="seconds")})
        audit("alert_raised", "info", alert=alert_type, key=key)


def reset_state():
    BALANCES.clear()
    BALANCES.update({"alice": 1000, "bob": 1000, "admin": 5000})
    SESSIONS.clear()
    LOG.clear()
    ALERTS.clear()
    RECENT.clear()
    TRUTH["failed"] = 0
    TRUTH["real_logins"] = {"admin"}
    SESSIONS[secrets.token_hex(8)] = "admin"


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


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(user, *args, **kwargs):
        if USERS[user]["role"] != "admin":
            # FIX 1: отказ в доступе фиксируется и учитывается для оповещений
            audit("access_denied", "failure", user, path=request.path)
            raise_if_burst("access_denied", user, "ACCESS_DENIED_BURST")
            return jsonify(error="только для администратора"), 403
        return f(user, *args, **kwargs)
    return wrapper


@app.get("/")
def index():
    return jsonify(
        message="A09 Logging and Alerting Failures lab (fixed)",
        endpoints=["POST /login", "GET /me", "POST /transfer", "POST /feedback",
                   "GET /admin/export", "GET /logs", "GET /logs/verify",
                   "GET /logs/summary", "GET /alerts", "POST /reset-lab"],
    )


@app.post("/reset-lab")
def reset_lab():
    reset_state()
    return jsonify(ok=True)


@app.post("/login")
def login():
    d = body()
    username, password = d.get("username"), d.get("password")
    user = USERS.get(username) if isinstance(username, str) else None
    if not user or user["password"] != password:
        TRUTH["failed"] += 1
        # FIX 1: неудачный вход логируется (имя очищено — FIX 2); пароль не
        # пишем вообще (FIX 3)
        audit("login", "failure", username)
        raise_if_burst("login_failed", request.remote_addr, "BRUTE_FORCE")
        return jsonify(error="неверный логин или пароль"), 401
    sid = secrets.token_hex(8)
    SESSIONS[sid] = username
    TRUTH["real_logins"].add(username)
    # FIX 3: ни пароля, ни сессии в логе — только короткий «отпечаток»
    audit("login", "success", username,
          session=hashlib.sha256(sid.encode()).hexdigest()[:8])
    resp = jsonify(ok=True, user=username)
    resp.set_cookie(PREFIX + "sid", sid, httponly=True, samesite="Lax")
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
        audit("transfer", "failure", user, to=to, amount=amount, reason="insufficient_funds")
        return jsonify(error="недостаточно средств"), 400
    BALANCES[user] -= amount
    BALANCES[to] += amount
    # FIX 6: аудит значимого действия — кто, кому, сколько
    audit("transfer", "success", user, to=to, amount=amount)
    return jsonify(ok=True, balance=BALANCES[user])


@app.post("/feedback")
def feedback():
    d = body()
    # FIX 2: структурная запись + очистка — перевод строки не создаёт новой записи
    audit("feedback", "info", d.get("name", "аноним"), message=d.get("message", ""))
    return jsonify(ok=True, message="спасибо за отзыв")


@app.get("/admin/export")
@admin_required
def admin_export(user):
    audit("admin_export", "success", user)
    return jsonify(balances=BALANCES)


@app.get("/logs")
@admin_required  # FIX 5: журнал читает только администратор
def logs(user):
    return jsonify(LOG)


@app.get("/logs/verify")
@admin_required
def logs_verify(user):
    """FIX 6: проверка целостности — пересчёт хеш-цепочки с начала."""
    prev = ZERO
    for i, entry in enumerate(LOG):
        body_ = {k: v for k, v in entry.items() if k != "hash"}
        if entry["seq"] != i + 1 or entry["prev"] != prev or digest(body_) != entry["hash"]:
            return jsonify(ok=False, first_bad_seq=i + 1,
                           note="журнал изменён: цепочка хешей нарушена")
        prev = entry["hash"]
    return jsonify(ok=True, entries=len(LOG))


@app.get("/logs/summary")
@admin_required
def logs_summary(user):
    seen = []
    for e in LOG:  # данные берутся из полей записи, а не разбором текста
        if e["event"] == "login" and e["outcome"] == "success" and e["user"] not in seen:
            seen.append(e["user"])
    return jsonify(successful_logins=seen)


@app.get("/alerts")
@admin_required  # FIX 4/5: оповещения видит администратор
def alerts(user):
    return jsonify(alerts=ALERTS)


@app.post("/_lab/tamper")
def lab_tamper():
    """ЛАБ-ПОМОЩНИК: имитирует злоумышленника с доступом к хранилищу лога.
    {"index": N, "text": "новый итог"}; "text": null — удалить запись."""
    d = body()
    i = d.get("index")
    if not isinstance(i, int) or not 0 <= i < len(LOG):
        return jsonify(error=f"index от 0 до {len(LOG) - 1}"), 400
    if d.get("text") is None:
        LOG.pop(i)
    else:
        LOG[i]["outcome"] = str(d["text"])  # хеш не пересчитываем — как у атакующего
    return jsonify(ok=True, entries=len(LOG))


from labui import register_ui  # noqa: E402  (учебный интерфейс /ui)
register_ui(app, "A09 Logging and Alerting Failures — fixed",
            notes="Аккаунты: alice / alice123, bob / bob123. Пароль admin найдите сами.",
            presets={
                "POST /login": [("alice", {"username": "alice", "password": "alice123"}),
                                ("bob", {"username": "bob", "password": "bob123"})],
                "POST /transfer": [("alice → bob 50", {"to": "bob", "amount": 50})],
                "POST /feedback": [("отзыв", {"name": "Аня", "message": "Всё отлично"})],
                "POST /_lab/tamper": [("удалить запись 1", {"index": 0, "text": None})],
            },
            uz={"notes": "Akkauntlar: alice / alice123, bob / bob123. Admin parolini oʻzingiz toping.",
                "presets": {
                    "POST /feedback": [("fikr", {"name": "Ali", "message": "Hammasi yaxshi"})],
                    "POST /_lab/tamper": [("1-qatorni oʻchirish", {"index": 1, "text": None})],
                }})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
