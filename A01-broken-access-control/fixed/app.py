"""A01 Broken Access Control — ИСПРАВЛЕННАЯ версия.

Отличия от vulnerable/app.py помечены комментариями FIX.
"""
from functools import wraps

import os
from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-production"
# Разные имена cookie: vulnerable и fixed на 127.0.0.1 не должны делить сессию
app.config["SESSION_COOKIE_NAME"] = "a01_fixed_session"

USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "bob": {"password": "bob123", "role": "user"},
    "admin": {"password": "Adm1n-lab-pass", "role": "admin"},
}

# Заявки сотрудников в HR (маршрут по-прежнему /api/notes)
NOTES = {
    1: {"id": 1, "owner": "alice", "text": "Заявка Алисы: отпуск с 14 по 28 июля"},
    2: {"id": 2, "owner": "bob", "text": "Заявка Боба: перенос рабочего графика на 10:00"},
    3: {"id": 3, "owner": "admin", "text": "Конфиденциально (админ): FLAG{a01_idor_admin_note}"},
}

# Справочник сотрудников для портала. department/position это коды,
# названия подставляет интерфейс на выбранном языке. username=None: у
# коллеги нет учётной записи в лабе.
EMPLOYEES = [
    {"username": "alice", "name": "Alice Johnson", "department": "qa", "position": "qa_engineer"},
    {"username": "bob", "name": "Bob Smith", "department": "dev", "position": "developer"},
    {"username": "admin", "name": "Admin", "department": "hr", "position": "hr_admin"},
    {"username": None, "name": "Dilnoza Karimova", "department": "design", "position": "designer"},
    {"username": None, "name": "Jasur Rakhimov", "department": "dev", "position": "developer"},
    {"username": None, "name": "Malika Yusupova", "department": "finance", "position": "accountant"},
    {"username": None, "name": "Timur Abdullaev", "department": "sales", "position": "sales_manager"},
]


def employee_public(e):
    slug = e["name"].lower().replace(" ", ".")
    return {"name": e["name"], "department": e["department"],
            "position": e["position"], "email": f"{slug}@testlab.example"}


def current_user():
    return session.get("user")


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user():
            return jsonify(error="login required"), 401
        return view(*args, **kwargs)

    return wrapper


# FIX: роль проверяется на сервере для каждой защищённой функции
def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if USERS[current_user()]["role"] != "admin":
            return jsonify(error="forbidden"), 403
        return view(*args, **kwargs)

    return wrapper


@app.get("/")
def index():
    return jsonify(
        message="A01 Broken Access Control lab (fixed)",
        login="POST /login (JSON: username, password). Тестовый аккаунт: alice / alice123",
        endpoints=["GET /me", "GET /api/notes", "GET /api/notes/<id>", "GET /api/employees",
                   "GET /admin/users", "POST /logout"],
        portal="Откройте / в браузере: HR-портал TestLab HR (консоль эндпоинтов: /ui)",
    )


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    user = USERS.get(data.get("username", ""))
    if not user or user["password"] != data.get("password"):
        return jsonify(error="invalid credentials"), 401
    session["user"] = data["username"]
    return jsonify(message="logged in", user=data["username"])


@app.post("/logout")
def logout():
    session.clear()
    return jsonify(message="logged out")


@app.get("/me")
@login_required
def me():
    profile = next(e for e in EMPLOYEES if e["username"] == current_user())
    return jsonify(user=current_user(), role=USERS[current_user()]["role"],
                   name=profile["name"], department=profile["department"],
                   position=profile["position"])


@app.get("/api/employees")
@login_required
def employees():
    return jsonify([employee_public(e) for e in EMPLOYEES])


@app.get("/api/notes")
@login_required
def my_notes():
    return jsonify([n for n in NOTES.values() if n["owner"] == current_user()])


@app.get("/api/notes/<int:note_id>")
@login_required
def get_note(note_id):
    note = NOTES.get(note_id)
    if not note:
        return jsonify(error="not found"), 404
    # FIX: проверяем владельца ресурса (запрет по умолчанию)
    if note["owner"] != current_user():
        return jsonify(error="forbidden"), 403
    return jsonify(note)


@app.get("/admin/users")
@admin_required
def admin_users():
    return jsonify(
        users=[{"username": u, "role": d["role"]} for u, d in USERS.items()],
        flag="FLAG{a01_admin_panel_open}",
    )


# Учебная обвязка: не часть уязвимости, одинакова в vulnerable и fixed.
# Портал ("/" в браузере) подключается ДО /ui, чтобы "/" не уходил в консоль.
from portal import register_portal  # noqa: E402
register_portal(app, "fixed")
from labui import register_ui  # noqa: E402
register_ui(app, 'A01 Broken Access Control — fixed', notes='Аккаунты: alice / alice123, bob / bob123, admin / Adm1n-lab-pass',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'alice123'}), ('bob', {'username': 'bob', 'password': 'bob123'})]},
            uz={'notes': 'Akkauntlar: alice / alice123, bob / bob123, admin / Adm1n-lab-pass'},
            en={'notes': 'Accounts: alice / alice123, bob / bob123, admin / Adm1n-lab-pass'})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
