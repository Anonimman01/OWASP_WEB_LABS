"""
A06:2025 Insecure Design — ИСПРАВЛЕННАЯ версия мини-магазина.

Изменён не «один опасный вызов», а дизайн: сервер — единственный источник
истины, значения ограничены, процесс — конечный автомат, код сброса защищён.
Каждое исправление помечено комментарием FIX.
"""
import hmac
import os
import secrets
import time
from functools import wraps

from flask import Flask, Response, jsonify, request, session

app = Flask(__name__)
app.secret_key = "lab-only-secret"

PRODUCTS = {
    1: {"name": "Кружка", "price": 1_000},
    2: {"name": "Ноутбук", "price": 150_000},
    3: {"name": "Подарочный набор", "price": 500_000},
}
COUPONS = {"WELCOME50": 50}

MAX_ITEMS = 20
MAX_QTY = 10
OTP_TTL = 300         # секунд жизни кода
OTP_MAX_ATTEMPTS = 5  # попыток на один код
OTP_COOLDOWN = 60     # не чаще одного нового кода в минуту

USERS, ORDERS, RESETS = {}, {}, {}
_next_order_id = 1


def reset_state():
    global _next_order_id
    USERS.clear()
    ORDERS.clear()
    RESETS.clear()
    _next_order_id = 1
    USERS["alice"] = {"name": "alice", "password": "alice123", "balance": 10_000,
                      "used_coupons": set()}
    USERS["bob"] = {"name": "bob", "password": "S3cr3t-b0b-pass", "balance": 1_000_000,
                    "used_coupons": set()}


reset_state()


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = USERS.get(session.get("user"))
        if not user:
            return jsonify(error="сначала войдите: POST /login"), 401
        return f(user, *args, **kwargs)
    return wrapper


def own_order(user, oid):
    order = ORDERS.get(oid)
    if order and order["owner"] == user["name"]:
        return order
    return None


@app.get("/")
def index():
    return Response("<h1>A06 Insecure Design — fixed</h1><p>Те же эндпоинты, что в vulnerable.</p>",
                    mimetype="text/html")


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
    session["user"] = user["name"]
    return jsonify(ok=True, user=user["name"], balance=user["balance"])


@app.get("/me")
@login_required
def me(user):
    return jsonify(user=user["name"], balance=user["balance"])


@app.get("/products")
def products():
    return jsonify(products=PRODUCTS)


@app.post("/orders")
@login_required
def create_order(user):
    global _next_order_id
    d = body()
    raw_items = d.get("items")
    # FIX 2: строгая валидация структуры и диапазонов
    if not isinstance(raw_items, list) or not 1 <= len(raw_items) <= MAX_ITEMS:
        return jsonify(error=f"items: от 1 до {MAX_ITEMS} позиций"), 400

    total = 0
    items = []
    for it in raw_items:
        if not isinstance(it, dict):
            return jsonify(error="неверная позиция"), 400
        product = PRODUCTS.get(it.get("product_id"))
        if not product:
            return jsonify(error="нет такого товара"), 400
        qty = it.get("quantity", 1)
        if not is_int(qty) or not 1 <= qty <= MAX_QTY:
            return jsonify(error=f"quantity: целое от 1 до {MAX_QTY}"), 400
        # FIX 1: цена ТОЛЬКО из каталога на сервере, поле price из запроса игнорируется
        price = product["price"]
        total += price * qty
        items.append({"product_id": it["product_id"], "quantity": qty, "price": price})

    # FIX 3: не более одного купона, он должен существовать и быть не использован
    coupons = d.get("coupons", [])
    if not isinstance(coupons, list) or len(coupons) > 1:
        return jsonify(error="можно применить не больше одного купона"), 400
    coupon = None
    if coupons:
        coupon = coupons[0]
        if coupon not in COUPONS:
            return jsonify(error="неизвестный купон"), 400
        if coupon in user["used_coupons"]:
            return jsonify(error="купон уже использован"), 400
        total = total * (100 - COUPONS[coupon]) // 100
    total = max(total, 0)  # страховка: итог никогда не отрицательный

    order = {"id": _next_order_id, "owner": user["name"], "items": items,
             "total": total, "coupon": coupon, "status": "created"}
    ORDERS[_next_order_id] = order
    _next_order_id += 1
    return jsonify(order), 201


@app.get("/orders/<int:oid>")
@login_required
def get_order(user, oid):
    order = own_order(user, oid)
    return (jsonify(order), 200) if order else (jsonify(error="заказ не найден"), 404)


@app.post("/orders/<int:oid>/pay")
@login_required
def pay(user, oid):
    order = own_order(user, oid)
    if not order:
        return jsonify(error="заказ не найден"), 404
    # FIX 4: конечный автомат — оплатить можно только заказ в статусе created
    if order["status"] != "created":
        return jsonify(error=f"заказ в статусе {order['status']}, оплата невозможна"), 409
    # FIX 3: купон «сгорает» в момент оплаты; повторно использовать нельзя
    if order["coupon"] and order["coupon"] in user["used_coupons"]:
        return jsonify(error="купон уже использован"), 409
    if user["balance"] < order["total"]:
        return jsonify(error="недостаточно средств"), 402
    user["balance"] -= order["total"]
    if order["coupon"]:
        user["used_coupons"].add(order["coupon"])
    order["status"] = "paid"
    return jsonify(ok=True, balance=user["balance"], status=order["status"])


@app.post("/orders/<int:oid>/ship")
@login_required
def ship(user, oid):
    order = own_order(user, oid)
    if not order:
        return jsonify(error="заказ не найден"), 404
    # FIX 5: отгрузка только после оплаты
    if order["status"] != "paid":
        return jsonify(error="сначала нужно оплатить заказ"), 409
    order["status"] = "shipped"
    resp = {"ok": True, "status": order["status"]}
    if any(i["product_id"] == 3 for i in order["items"]):
        resp["flag"] = "FLAG{A06_gift_delivered_without_paying_properly}"
    return jsonify(resp)


@app.post("/password-reset/request")
def reset_request():
    name = body().get("username")
    now = time.time()
    # FIX 8: одинаковый ответ в любом случае — нет перечисления пользователей
    generic = jsonify(ok=True, message="если пользователь существует, код отправлен")
    if name in USERS:
        current = RESETS.get(name)
        # FIX 7: кулдаун — нельзя бесконечно перевыпускать код и обнулять счётчик попыток
        if not current or now - current["issued"] >= OTP_COOLDOWN:
            otp = f"{secrets.randbelow(10**6):06d}"  # FIX 6: 6 цифр, криптостойкий генератор
            RESETS[name] = {"otp": otp, "issued": now, "attempts": 0}
            print(f"[mail] код сброса для {name}: {otp}", flush=True)
    return generic


@app.post("/password-reset/confirm")
def reset_confirm():
    d = body()
    name = d.get("username")
    new_password = d.get("new_password")
    fail = (jsonify(error="неверный или просроченный код"), 403)

    entry = RESETS.get(name)
    if not entry:
        return fail
    # FIX 7: срок жизни и лимит попыток
    if time.time() - entry["issued"] > OTP_TTL:
        del RESETS[name]
        return fail
    entry["attempts"] += 1
    if entry["attempts"] > OTP_MAX_ATTEMPTS:
        del RESETS[name]  # после лимита код уничтожается, нужен новый
        return fail
    if not hmac.compare_digest(entry["otp"], str(d.get("otp", ""))):
        return fail
    if not isinstance(new_password, str) or len(new_password) < 8:
        return jsonify(error="пароль минимум 8 символов"), 400

    USERS[name]["password"] = new_password
    del RESETS[name]
    return jsonify(ok=True, message="пароль изменён")


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
