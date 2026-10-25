"""A01 Broken Access Control — УЯЗВИМАЯ версия.

Только для обучения. Не публикуйте это приложение в интернете.
"""
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


@app.get("/")
def index():
    return jsonify(
        message="A01 Broken Access Control lab (vulnerable)",
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
def me():
    if not current_user():
        return jsonify(error="login required"), 401
    return jsonify(user=current_user(), role=USERS[current_user()]["role"])


@app.get("/api/notes")
def my_notes():
    if not current_user():
        return jsonify(error="login required"), 401
    return jsonify([n for n in NOTES.values() if n["owner"] == current_user()])


@app.get("/api/notes/<int:note_id>")
def get_note(note_id):
    if not current_user():
        return jsonify(error="login required"), 401
    note = NOTES.get(note_id)
    if not note:
        return jsonify(error="not found"), 404
    # УЯЗВИМОСТЬ: нет проверки, что заметка принадлежит текущему пользователю (IDOR)
    return jsonify(note)


@app.get("/admin/users")
def admin_users():
    if not current_user():
        return jsonify(error="login required"), 401
    # УЯЗВИМОСТЬ: нет проверки роли admin (доступ к функции без прав)
    return jsonify(
        users=[{"username": u, "role": d["role"]} for u, d in USERS.items()],
        flag="FLAG{a01_admin_panel_open}",
    )


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A01 Broken Access Control — vulnerable', notes='Аккаунты: alice / alice123, bob / bob123, admin / Adm1n-lab-pass',
            presets={'POST /login': [('alice', {'username': 'alice', 'password': 'alice123'}), ('bob', {'username': 'bob', 'password': 'bob123'})]},
            uz={'notes': 'Akkauntlar: alice / alice123, bob / bob123, admin / Adm1n-lab-pass'},
            en={'notes': 'Accounts: alice / alice123, bob / bob123, admin / Adm1n-lab-pass'})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
