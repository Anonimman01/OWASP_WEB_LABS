"""
A08:2025 Software or Data Integrity Failures — ИСПРАВЛЕННАЯ версия.

Каждое исправление помечено комментарием FIX N — номер совпадает с
дефектом во vulnerable/app.py.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from functools import wraps

from flask import Flask, Response, jsonify, request

app = Flask(__name__)

PREFIX = "a08f_"

USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "admin": {"password": "Adm1n-lab-pass", "role": "admin"},
}
DEFAULT_PAYOUT = "LAB-IBAN-0001-LEGIT"
SETTINGS, MIRROR, ORDERS, CDN = {}, {}, {}, {}
SEEN_WEBHOOKS = set()

# FIX 1/2: секретный ключ сервера для подписи cookie (в проде — из окружения/секрет-хранилища)
SECRET = os.environ.get("SECRET_KEY", "").encode() or secrets.token_bytes(32)
# FIX 4: общий секрет с платёжным провайдером
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "lab-demo-webhook-secret").encode()
WEBHOOK_MAX_AGE = 300

LEGIT_WIDGET = 'document.getElementById("acct").textContent = "LAB-IBAN-0001-LEGIT";\n'
EVIL_WIDGET = 'document.getElementById("acct").textContent = "ATTACKER-IBAN-6666";\n'

# FIX 5: SRI-хеш эталонного скрипта
WIDGET_SRI = "sha384-" + base64.b64encode(hashlib.sha384(LEGIT_WIDGET.encode()).digest()).decode()


def canonical_sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


# FIX 3: «lock-файл» — хеши пакетов, которым мы доверяем, и разрешённые поля
PINNED = {"theme-pack": canonical_sha256({"theme": "dark"})}
ALLOWED_KEYS = {"theme"}


def reset_state():
    SETTINGS.clear()
    SETTINGS.update({"theme": "light", "payout_account": DEFAULT_PAYOUT})
    MIRROR.clear()
    MIRROR["theme-pack"] = {"version": "1.1", "content": {"theme": "dark"}}
    ORDERS.clear()
    ORDERS[1001] = {"id": 1001, "owner": "alice", "item": "Pro license",
                    "amount": 5000, "status": "pending"}
    SEEN_WEBHOOKS.clear()
    CDN["widget"] = LEGIT_WIDGET


reset_state()


def b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


# FIX 1 + FIX 2: настоящая подпись — HMAC-SHA256 с секретным ключом сервера
def sign(payload: dict) -> str:
    data = b64e(json.dumps(payload, separators=(",", ":")).encode())
    sig = b64e(hmac.new(SECRET, data.encode(), hashlib.sha256).digest())
    return f"{data}.{sig}"


def unsign(token):
    try:
        data, sig = token.split(".")
        expected = b64e(hmac.new(SECRET, data.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(b64d(data))
    except Exception:
        return None


def read_profile():
    raw = request.cookies.get(PREFIX + "profile")
    return unsign(raw) if raw else None


def read_license():
    raw = request.cookies.get(PREFIX + "license")
    return unsign(raw) if raw else None


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        profile = read_profile()
        if not profile or profile.get("user") not in USERS:
            return jsonify(error="сначала войдите: POST /login"), 401
        return f(profile, *args, **kwargs)
    return wrapper


def set_signed_cookie(resp, name, payload):
    resp.set_cookie(PREFIX + name, sign(payload), httponly=True, samesite="Lax")


@app.get("/")
def index():
    return Response("<h1>A08 Integrity Failures — fixed</h1><p>Те же эндпоинты, что в vulnerable.</p>",
                    mimetype="text/html")


@app.post("/reset-lab")
def reset_lab():
    reset_state()
    resp = jsonify(ok=True)
    resp.delete_cookie(PREFIX + "profile")
    resp.delete_cookie(PREFIX + "license")
    return resp


@app.post("/login")
def login():
    d = body()
    user = USERS.get(d.get("username"))
    if not user or user["password"] != d.get("password"):
        return jsonify(error="неверный логин или пароль"), 401
    resp = jsonify(ok=True, user=d["username"], role=user["role"])
    # FIX 1: в cookie только подписанный идентификатор; роль — не доверяем токену
    set_signed_cookie(resp, "profile", {"user": d["username"]})
    return resp


@app.get("/me")
@login_required
def me(profile):
    return jsonify(user=profile["user"], role=USERS[profile["user"]]["role"])


@app.get("/admin")
@login_required
def admin(profile):
    # FIX 1: роль берётся из серверного хранилища, а не из токена
    if USERS[profile["user"]]["role"] != "admin":
        return jsonify(error="только для администратора"), 403
    return jsonify(ok=True, message="добро пожаловать в админку")


@app.post("/buy")
@login_required
def buy(profile):
    if body().get("plan") != "basic":
        return jsonify(error="тариф pro недоступен без оплаты"), 402
    resp = jsonify(ok=True, plan="basic")
    set_signed_cookie(resp, "license", {"user": profile["user"], "plan": "basic"})
    return resp


@app.get("/pro")
@login_required
def pro(profile):
    lic = read_license()
    # FIX 2: лицензия подписана HMAC и привязана к конкретному пользователю
    if not lic or lic.get("user") != profile["user"] or lic.get("plan") != "pro":
        return jsonify(error="нужна pro-лицензия"), 403
    return jsonify(ok=True, message="pro-раздел")


@app.post("/mirror/publish")
def mirror_publish():
    """ЛАБ-ПОМОЩНИК: имитирует атакующего, получившего запись на зеркало обновлений."""
    d = body()
    if not d.get("package") or not isinstance(d.get("content"), dict):
        return jsonify(error="нужны package и content (объект)"), 400
    MIRROR[d["package"]] = {"version": str(d.get("version", "9.9")), "content": d["content"]}
    return jsonify(ok=True)


@app.post("/system/run-update")
def run_update():
    """Имитация cron-задачи автообновления."""
    applied, rejected = [], []
    for name, pkg in MIRROR.items():
        expected = PINNED.get(name)
        # FIX 3: пакет должен быть в lock-файле, а его хеш — совпасть с закреплённым
        if not expected:
            rejected.append({"package": name, "reason": "пакета нет в lock-файле"})
            continue
        if not hmac.compare_digest(expected, canonical_sha256(pkg["content"])):
            rejected.append({"package": name, "reason": "хеш не совпадает с lock-файлом"})
            continue
        # FIX 3: даже доверенный пакет может менять только разрешённые поля
        if set(pkg["content"]) - ALLOWED_KEYS:
            rejected.append({"package": name, "reason": "недопустимые поля"})
            continue
        SETTINGS.update(pkg["content"])
        applied.append({"package": name, "version": pkg["version"]})
    return jsonify(ok=True, applied=applied, rejected=rejected)


@app.get("/settings")
def settings():
    return jsonify(settings=SETTINGS)


@app.get("/orders/<int:oid>")
@login_required
def get_order(profile, oid):
    order = ORDERS.get(oid)
    if not order or order["owner"] != profile["user"]:
        return jsonify(error="заказ не найден"), 404
    resp = dict(order)
    if order["status"] == "paid":
        resp["download_key"] = "KEY-LAB-DELIVERED"
    return jsonify(resp)


@app.post("/webhook/payment")
def webhook_payment():
    raw = request.get_data()
    ts = request.headers.get("X-Timestamp", "")
    sig = request.headers.get("X-Signature", "")
    fail = (jsonify(error="неверная подпись или метка времени"), 401)

    # FIX 4: подпись HMAC-SHA256 над "timestamp.тело" + проверка свежести (защита от replay)
    try:
        age = abs(time.time() - int(ts))
    except ValueError:
        return fail
    if age > WEBHOOK_MAX_AGE:
        return fail
    expected = "sha256=" + hmac.new(WEBHOOK_SECRET, ts.encode() + b"." + raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return fail
    if sig in SEEN_WEBHOOKS:
        return jsonify(error="повторная доставка отклонена"), 409
    SEEN_WEBHOOKS.add(sig)

    d = body()
    order = ORDERS.get(d.get("order_id"))
    if not order:
        return jsonify(error="заказ не найден"), 404
    # FIX 4: сверяем сумму и статус заказа, а не верим одному полю status
    if order["status"] != "pending" or d.get("amount") != order["amount"]:
        return jsonify(error="сумма или состояние заказа не совпадают"), 409
    if d.get("status") == "paid":
        order["status"] = "paid"
    return jsonify(ok=True)


@app.get("/donate")
def donate():
    # FIX 5: integrity — браузер откажется выполнять скрипт, если его хеш не совпадёт
    html = f"""<!doctype html><meta charset="utf-8">
<h1>Пожертвования</h1>
<p>Реквизиты для перевода: <b id="acct">загрузка…</b></p>
<script src="/cdn/widget.js" integrity="{WIDGET_SRI}" crossorigin="anonymous"></script>"""
    resp = Response(html, mimetype="text/html")
    return resp


@app.get("/cdn/widget.js")
def cdn_widget():
    return Response(CDN["widget"], mimetype="application/javascript")


@app.post("/cdn/compromise")
def cdn_compromise():
    """ЛАБ-ПОМОЩНИК: имитирует взлом стороннего CDN."""
    CDN["widget"] = EVIL_WIDGET
    return jsonify(ok=True, note="widget.js подменён")


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A08 Integrity Failures — fixed', notes='Аккаунты: alice / alice123, admin / Adm1n-lab-pass',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'alice123'})], 'POST /buy': [('тариф basic', {'plan': 'basic'})]},
            uz={'notes': 'Akkauntlar: alice / alice123, admin / Adm1n-lab-pass',
                'presets': {'POST /buy': [('basic tarifi', {'plan': 'basic'})]}},
            en={'notes': 'Accounts: alice / alice123, admin / Adm1n-lab-pass',
             'presets': {'POST /buy': [['basic plan', {'plan': 'basic'}]]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
