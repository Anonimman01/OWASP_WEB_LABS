"""A01 Broken Access Control — ИСПРАВЛЕННАЯ версия.

Отличия от vulnerable/app.py помечены комментариями FIX.
"""
from functools import wraps

import os
from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.secret_key = "lab-secret-not-for-production"

USERS = {
    "alice": {"password": "alice123", "role": "user"},
    "bob": {"password": "bob123", "role": "user"},
    "admin": {"password": "Adm1n-lab-pass", "role": "admin"},
}

NOTES = {
    1: {"id": 1, "owner": "alice", "text": "Заметка Алисы: список покупок"},
    2: {"id": 2, "owner": "bob", "text": "Заметка Боба: черновик письма"},
    3: {"id": 3, "owner": "admin", "text": "Секрет админа: FLAG{a01_idor_admin_note}"},
}


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
        endpoints=["GET /me", "GET /api/notes", "GET /api/notes/<id>", "GET /admin/users"],
    )


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    user = USERS.get(data.get("username", ""))
    if not user or user["password"] != data.get("password"):
        return jsonify(error="invalid credentials"), 401
    session["user"] = data["username"]
    return jsonify(message="logged in", user=data["username"])


@app.get("/me")
@login_required
def me():
    return jsonify(user=current_user(), role=USERS[current_user()]["role"])


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


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A01 Broken Access Control — fixed', notes='Аккаунты: alice / alice123, bob / bob123, admin / Adm1n-lab-pass',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'alice123'}), ('bob', {'username': 'bob', 'password': 'bob123'})]})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
