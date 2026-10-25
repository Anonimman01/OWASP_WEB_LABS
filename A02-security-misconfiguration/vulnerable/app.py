"""A02 Security Misconfiguration — УЯЗВИМАЯ версия.

Только для обучения. Не публикуйте это приложение в интернете.
"""
import os
import traceback

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# МИСКОНФИГ №1: учётная запись по умолчанию
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin"

# Вымышленные данные для лабы
DB_URL = "postgres://labuser:LabDbPass123@db.internal:5432/shop"


@app.get("/")
def index():
    return jsonify(
        message="A02 Security Misconfiguration lab (vulnerable)",
        endpoints=["POST /login", "GET /items?id=<число>", "GET /files/<имя файла>"],
    )


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    if data.get("username") == ADMIN_USER and data.get("password") == ADMIN_PASSWORD:
        return jsonify(message="welcome, admin", flag="FLAG{a02_default_credentials}")
    return jsonify(error="invalid credentials"), 401


@app.get("/items")
def items():
    item_id = int(request.args.get("id", "1"))  # ошибка при нечисловом id
    return jsonify(id=item_id, name=f"item-{item_id}")


# МИСКОНФИГ №2: отдаём файлы из корня приложения, включая .env и бэкапы
@app.get("/files/<path:name>")
def files(name):
    return send_from_directory(APP_DIR, name)


# МИСКОНФИГ №3: подробные ошибки с трассировкой и конфигурацией
@app.errorhandler(Exception)
def verbose_error(exc):
    if hasattr(exc, "code") and isinstance(exc.code, int) and exc.code < 500:
        return jsonify(error=str(exc)), exc.code
    return (
        jsonify(
            error=str(exc),
            traceback=traceback.format_exc().splitlines(),
            config={"DB_URL": DB_URL, "APP_DIR": APP_DIR},
        ),
        500,
    )


# МИСКОНФИГ №4: нет защитных заголовков, лишний баннер с версиями
@app.after_request
def add_banner(resp):
    resp.headers["X-Powered-By"] = "Flask 3.1.3 / Python 3.11"
    return resp


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A02 Security Misconfiguration — vulnerable', notes='Аккаунтов нет: найдите вход сами.',
            presets={'POST /login': [('неверный пароль', {'username': 'user', 'password': 'test'})], 'GET /items': [('id=1', '?id=1')], 'GET /files/<path:name>': [('public.txt', '/files/public.txt')]},
            uz={'notes': 'Akkauntlar yoʻq: kirishni oʻzingiz toping.', 'presets': {'POST /login': [('notoʻgʻri parol', {'username': 'user', 'password': 'test'})]}},
            en={'notes': 'No accounts: find the way in yourself.',
             'presets': {'POST /login': [['wrong password', {'username': 'user', 'password': 'test'}]]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
