"""
A08:2025 Software or Data Integrity Failures — УЯЗВИМАЯ версия.

Пять дефектов: приложение доверяет данным и коду, подлинность которых
не проверена.
1. Состояние пользователя в cookie без подписи
2. «Подпись» cookie — обычный хеш без секретного ключа
3. Автообновление ставит пакеты с зеркала без проверки целостности
4. Webhook платёжной системы принимается без проверки подписи
5. Сторонний скрипт подключён без SRI (Subresource Integrity)

Только для локального запуска!
"""
import base64
import hashlib
import json
import os
from functools import wraps

from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# Префикс нужен, чтобы cookie vulnerable и fixed (один хост 127.0.0.1,
# разные порты) не перезаписывали друг друга в браузере
PREFIX = "a08v_"

USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "admin": {"password": "Adm1n-lab-pass", "role": "admin"},
}
DEFAULT_PAYOUT = "LAB-IBAN-0001-LEGIT"
SETTINGS, MIRROR, ORDERS, CDN = {}, {}, {}, {}

LEGIT_WIDGET = 'document.getElementById("acct").textContent = "LAB-IBAN-0001-LEGIT";\n'
EVIL_WIDGET = 'document.getElementById("acct").textContent = "ATTACKER-IBAN-6666";\n'


def reset_state():
    SETTINGS.clear()
    SETTINGS.update({"theme": "light", "payout_account": DEFAULT_PAYOUT})
    MIRROR.clear()
    MIRROR["theme-pack"] = {"version": "1.1", "content": {"theme": "dark"}}
    ORDERS.clear()
    ORDERS[1001] = {"id": 1001, "owner": "alice", "item": "Pro license",
                    "amount": 5000, "status": "pending"}
    CDN["widget"] = LEGIT_WIDGET


reset_state()


def b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


# ---------- cookie profile (ДЕФЕКТ 1) ----------
def make_profile(username, role):
    # ДЕФЕКТ 1: состояние и роль лежат в cookie как обычный base64(JSON), без подписи
    return b64e(json.dumps({"user": username, "role": role}).encode())


def read_profile():
    raw = request.cookies.get(PREFIX + "profile")
    if not raw:
        return None
    try:
        return json.loads(b64d(raw))
    except Exception:
        return None


# ---------- cookie license (ДЕФЕКТ 2) ----------
def make_license(payload):
    data = json.dumps(payload, separators=(",", ":")).encode()
    # ДЕФЕКТ 2: «подпись» — SHA-256 от данных БЕЗ секретного ключа.
    # Это контрольная сумма, а не подпись: любой может пересчитать её сам.
    return b64e(data) + "." + hashlib.sha256(data).hexdigest()


def read_license():
    raw = request.cookies.get(PREFIX + "license")
    if not raw or "." not in raw:
        return None
    data_b64, _, digest = raw.partition(".")
    try:
        data = b64d(data_b64)
        if hashlib.sha256(data).hexdigest() != digest:
            return None
        return json.loads(data)
    except Exception:
        return None


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        profile = read_profile()
        if not profile or "user" not in profile:
            return jsonify(error="сначала войдите: POST /login"), 401
        return f(profile, *args, **kwargs)
    return wrapper


@app.get("/")
def index():
    html = """<h1>A08 Integrity Failures — vulnerable</h1>
<pre>
POST /login                  {"username","password"}      alice / alice123
GET  /me
GET  /admin
POST /buy                    {"plan":"basic"}
GET  /pro
POST /system/run-update      имитация cron: автообновление с зеркала
POST /mirror/publish         {"package","version","content":{}}  (имитация взлома зеркала)
GET  /settings
GET  /orders/&lt;id&gt;
POST /webhook/payment        {"order_id","status","amount"}
GET  /donate                 HTML-страница со сторонним скриптом
POST /cdn/compromise         (имитация взлома CDN)
POST /reset-lab
</pre>"""
    return Response(html, mimetype="text/html")


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
    resp.set_cookie(PREFIX + "profile", make_profile(d["username"], user["role"]))
    return resp


@app.get("/me")
@login_required
def me(profile):
    return jsonify(profile)


@app.get("/admin")
@login_required
def admin(profile):
    # ДЕФЕКТ 1 (эксплуатация): роль берётся из cookie, которую контролирует клиент
    if profile.get("role") != "admin":
        return jsonify(error="только для администратора"), 403
    return jsonify(ok=True, flag="FLAG{a08_unsigned_profile_cookie}")


@app.post("/buy")
@login_required
def buy(profile):
    if body().get("plan") != "basic":
        return jsonify(error="тариф pro недоступен без оплаты"), 402
    resp = jsonify(ok=True, plan="basic")
    resp.set_cookie(PREFIX + "license",
                    make_license({"user": profile["user"], "plan": "basic"}))
    return resp


@app.get("/pro")
@login_required
def pro(profile):
    lic = read_license()
    if not lic or lic.get("plan") != "pro":
        return jsonify(error="нужна pro-лицензия"), 403
    return jsonify(ok=True, flag="FLAG{a08_unkeyed_hash_is_not_a_signature}")


# ---------- автообновление (ДЕФЕКТ 3) ----------
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
    applied = []
    for name, pkg in MIRROR.items():
        # ДЕФЕКТ 3: пакет принимается как есть — ни хеша, ни подписи, ни
        # списка разрешённых полей
        SETTINGS.update(pkg["content"])
        applied.append({"package": name, "version": pkg["version"]})
    return jsonify(ok=True, applied=applied)


@app.get("/settings")
def settings():
    resp = {"settings": SETTINGS}
    if SETTINGS.get("payout_account") != DEFAULT_PAYOUT:
        resp["flag"] = "FLAG{a08_update_without_integrity_check}"
    return jsonify(resp)


# ---------- webhook (ДЕФЕКТ 4) ----------
@app.get("/orders/<int:oid>")
@login_required
def get_order(profile, oid):
    order = ORDERS.get(oid)
    if not order or order["owner"] != profile["user"]:
        return jsonify(error="заказ не найден"), 404
    resp = dict(order)
    if order["status"] == "paid":
        resp["download_key"] = "FLAG{a08_unsigned_webhook}"
    return jsonify(resp)


@app.post("/webhook/payment")
def webhook_payment():
    d = body()
    order = ORDERS.get(d.get("order_id"))
    if not order:
        return jsonify(error="заказ не найден"), 404
    # ДЕФЕКТ 4: ни подписи, ни проверки источника, ни суммы — любой, кто
    # знает адрес, может «подтвердить оплату»
    if d.get("status") == "paid":
        order["status"] = "paid"
    return jsonify(ok=True)


# ---------- сторонний скрипт (ДЕФЕКТ 5) ----------
@app.get("/donate")
def donate():
    # ДЕФЕКТ 5: скрипт «с CDN» подключён без атрибута integrity
    html = """<!doctype html><meta charset="utf-8">
<h1>Пожертвования</h1>
<p>Реквизиты для перевода: <b id="acct">загрузка…</b></p>
<script src="/cdn/widget.js"></script>"""
    return Response(html, mimetype="text/html")


@app.get("/cdn/widget.js")
def cdn_widget():
    return Response(CDN["widget"], mimetype="application/javascript")


@app.post("/cdn/compromise")
def cdn_compromise():
    """ЛАБ-ПОМОЩНИК: имитирует взлом стороннего CDN."""
    CDN["widget"] = EVIL_WIDGET
    return jsonify(ok=True, note="widget.js подменён")


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
