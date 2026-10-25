"""A02 Security Misconfiguration — ИСПРАВЛЕННАЯ версия.

Отличия от vulnerable/app.py помечены комментариями FIX.
"""
import logging
import os
import secrets
import uuid

from flask import Flask, jsonify, request

app = Flask(__name__)  # статика отдаётся только из папки ./static
logging.basicConfig(level=logging.INFO)

ADMIN_USER = "admin"
# FIX: пароль берётся из окружения; если он не задан, генерируется случайный
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = secrets.token_urlsafe(12)
    # Только для удобства лабы. В реальной системе секреты в логи не пишут.
    app.logger.warning("Сгенерирован пароль admin для лабы: %s", ADMIN_PASSWORD)


@app.get("/")
def index():
    return jsonify(
        message="A02 Security Misconfiguration lab (fixed)",
        endpoints=["POST /login", "GET /items?id=<число>", "GET /static/public.txt"],
    )


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "")
    password = data.get("password", "")
    # FIX: сравнение за постоянное время
    if secrets.compare_digest(username, ADMIN_USER) and secrets.compare_digest(
        password, ADMIN_PASSWORD
    ):
        return jsonify(message="welcome, admin")
    return jsonify(error="invalid credentials"), 401


@app.get("/items")
def items():
    try:
        item_id = int(request.args.get("id", "1"))
    except ValueError:
        return jsonify(error="id must be a number"), 400
    return jsonify(id=item_id, name=f"item-{item_id}")


# FIX: маршрута /files нет: наружу отдаётся только ./static


# FIX: пользователю — нейтральное сообщение, подробности — только в серверный лог
@app.errorhandler(Exception)
def safe_error(exc):
    code = getattr(exc, "code", 500)
    if isinstance(code, int) and code < 500:
        return jsonify(error=getattr(exc, "name", "error")), code
    error_id = uuid.uuid4().hex[:8]
    app.logger.exception("Unhandled error %s", error_id)
    return jsonify(error="internal server error", error_id=error_id), 500


# FIX: защитные заголовки, без баннера с версиями
@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Server"] = "app"
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
