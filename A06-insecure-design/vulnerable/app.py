"""
A06:2025 Insecure Design — УЯЗВИМАЯ версия мини-магазина.

Код «чистый»: нет SQL-инъекций, XSS и т.п. Сломан сам ДИЗАЙН:
бизнес-логика доверяет клиенту, не ограничивает значения, не проверяет
порядок шагов и не защищает одноразовый код от перебора.

Только для локального запуска! Деньги хранятся в центах.
"""
import os
import random
from functools import wraps

from flask import Flask, Response, jsonify, request, session

app = Flask(__name__)
app.secret_key = "lab-only-secret"  # хранение секретов — тема A02/A04, здесь не важно

PRODUCTS = {
    1: {"name": "Кружка", "price": 1_000},              # $10.00
    2: {"name": "Ноутбук", "price": 150_000},           # $1500.00
    3: {"name": "Подарочный набор", "price": 500_000},  # $5000.00
}
COUPONS = {"WELCOME50": 50}  # скидка в процентах

USERS, ORDERS, RESETS = {}, {}, {}
_next_order_id = 1


def reset_state():
    """Сброс данных лабы (удобно после экспериментов)."""
    global _next_order_id
    USERS.clear()
    ORDERS.clear()
    RESETS.clear()
    _next_order_id = 1
    # пароли в открытом виде — упрощение, хэширование разбирается в A04
    USERS["alice"] = {"name": "alice", "password": "alice123", "balance": 10_000}        # $100
    USERS["bob"] = {"name": "bob", "password": "S3cr3t-b0b-pass", "balance": 1_000_000}  # $10 000


reset_state()


def body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


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
    html = """<h1>A06 Insecure Design — vulnerable</h1>
<p>API мини-магазина. Работайте через curl / Burp / Postman (JSON).</p>
<pre>
POST /login                        {"username","password"}      alice / alice123
GET  /me
GET  /products
POST /orders                       {"items":[{"product_id","quantity"}],"coupons":["WELCOME50"]}
GET  /orders/&lt;id&gt;
POST /orders/&lt;id&gt;/pay
POST /orders/&lt;id&gt;/ship
POST /password-reset/request       {"username"}   (код «приходит» в лог сервера)
POST /password-reset/confirm       {"username","otp","new_password"}
POST /reset-lab                    сбросить данные лабы
</pre>"""
    return Response(html, mimetype="text/html")


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
    total = 0
    items = []
    for it in d.get("items", []):
        product = PRODUCTS.get(it.get("product_id"))
        if not product:
            return jsonify(error="нет такого товара"), 400
        qty = it.get("quantity", 1)
        # ДЕФЕКТ 1: цена берётся из запроса клиента
        price = it.get("price", product["price"])
        # ДЕФЕКТ 2: количество не валидируется (можно -5)
        total += price * qty
        items.append({"product_id": it["product_id"], "quantity": qty, "price": price})

    # ДЕФЕКТ 3: купоны суммируются, без лимита и без «один раз на пользователя»
    pct = sum(COUPONS.get(code, 0) for code in d.get("coupons", []))
    total = total * (100 - pct) // 100

    order = {"id": _next_order_id, "owner": user["name"], "items": items,
             "total": total, "status": "created"}
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
    # ДЕФЕКТ 4: статус не проверяется — заказ можно «оплатить» повторно
    if user["balance"] < order["total"]:
        return jsonify(error="недостаточно средств"), 402
    # при отрицательном total баланс РАСТЁТ
    user["balance"] -= order["total"]
    order["status"] = "paid"
    return jsonify(ok=True, balance=user["balance"], status=order["status"])


@app.post("/orders/<int:oid>/ship")
@login_required
def ship(user, oid):
    order = own_order(user, oid)
    if not order:
        return jsonify(error="заказ не найден"), 404
    # ДЕФЕКТ 5: не проверяется, что заказ оплачен — шаг оплаты можно пропустить
    order["status"] = "shipped"
    resp = {"ok": True, "status": order["status"]}
    if any(i["product_id"] == 3 for i in order["items"]):
        resp["flag"] = "FLAG{A06_gift_delivered_without_paying_properly}"
    return jsonify(resp)


@app.post("/password-reset/request")
def reset_request():
    name = body().get("username")
    if name not in USERS:
        return jsonify(error="пользователь не найден"), 404
    otp = f"{random.randint(0, 9999):04d}"  # ДЕФЕКТ 6: всего 10 000 вариантов
    RESETS[name] = otp
    print(f"[mail] код сброса для {name}: {otp}", flush=True)
    return jsonify(ok=True, message="код отправлен")


@app.post("/password-reset/confirm")
def reset_confirm():
    d = body()
    name = d.get("username")
    # ДЕФЕКТ 7: нет лимита попыток и срока жизни кода — перебор за минуты
    if name not in RESETS or RESETS[name] != str(d.get("otp")):
        return jsonify(error="неверный код"), 403
    USERS[name]["password"] = str(d.get("new_password", ""))
    del RESETS[name]
    return jsonify(ok=True, message="пароль изменён")


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
