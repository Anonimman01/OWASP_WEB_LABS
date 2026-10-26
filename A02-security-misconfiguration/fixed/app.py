"""A02 Security Misconfiguration — ИСПРАВЛЕННАЯ версия.

Сайт кофейни Lumière Café — тот же, что в vulnerable/, но с исправленной
конфигурацией. Отличия от vulnerable/app.py помечены комментариями FIX.
"""
import logging
import os
import secrets
import uuid

from flask import Flask, abort, g, jsonify, render_template, request

from cafe import (LANGS, dashboard_data, get_item, home_data, item_data,
                  menu_data, register_lang, t as texts)

app = Flask(__name__)  # статика отдаётся только из папки ./static
logging.basicConfig(level=logging.INFO)

# Как в vulnerable: язык запроса определяется до всех остальных хуков
register_lang(app)

ADMIN_USER = "admin"
# FIX 1: пароль берётся из окружения; если он не задан, генерируется случайный
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = secrets.token_urlsafe(12)
    # Только для удобства лабы. В реальной системе секреты в логи не пишут.
    app.logger.warning("Сгенерирован пароль admin для лабы: %s", ADMIN_PASSWORD)


def _page(template, **extra):
    """Все страницы сайта проходят через один helper: язык, переводы,
    вариант лабы."""
    tt = texts()
    return render_template(template, lang=g.lang, t=tt, langs=LANGS,
                           variant_label=tt["fixed"], **extra)


def _wants_html():
    """Браузер шлёт Accept: text/html, curl/Postman — */*."""
    return "text/html" in request.headers.get("Accept", "")


# Как в vulnerable: хук регистрируется ДО register_ui, чтобы браузерный
# запрос к "/" открывал сайт, а не перенаправлялся на /ui.
@app.before_request
def _site_index():
    if request.path == "/" and request.method == "GET" and _wants_html():
        return _page("home.html", active="home", **home_data())


@app.get("/")
def index():
    """Для curl и Postman — JSON-описание API; браузер открывает сайт (хук выше)."""
    return jsonify(
        message="Lumiere Cafe — A02 Security Misconfiguration (fixed)",
        endpoints=["GET /menu", "GET /menu/<item_id>", "GET /admin",
                   "POST /login", "GET /static/<path:filename>"],
        langs=LANGS,
    )


@app.get("/menu")
def menu_page():
    return _page("menu.html", active="menu", **menu_data())


@app.get("/menu/<item_id>")
def menu_item(item_id):
    # FIX 3 (ввод): номер позиции проверяется — нечисловое значение это
    # обычный ввод, а не падение сервера
    try:
        number = int(item_id)
    except ValueError:
        if _wants_html():
            tt = texts()
            return _page("error.html", active="", title=tt["err_400_t"],
                         message=tt["err_400_m"]), 400
        return jsonify(error="id must be a number"), 400
    item = get_item(number)
    if item is None:
        abort(404)
    return _page("item.html", active="menu", **item_data(item))


@app.get("/admin")
def admin_login():
    return _page("login.html", active="")


@app.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    tt = texts()
    username = data.get("username", "")
    password = data.get("password", "")
    # FIX 1: сравнение за постоянное время, пароль не захардкожен
    ok = (secrets.compare_digest(username, ADMIN_USER)
          and secrets.compare_digest(password, ADMIN_PASSWORD))
    if ok:
        # Флаг лабы есть только в vulnerable: здесь вход просто работает
        if _wants_html():
            return _page("dashboard.html", active="", **dashboard_data())
        return jsonify(message="welcome, admin")
    if _wants_html():
        return _page("login.html", active="", error=tt["err_cred"]), 401
    return jsonify(error="invalid credentials"), 401


# FIX 2: маршрута /files нет — наружу отдаётся только ./static


# FIX 3: пользователю — нейтральное сообщение, подробности — только в серверный лог
@app.errorhandler(Exception)
def safe_error(exc):
    tt = texts()
    code = getattr(exc, "code", 500)
    if isinstance(code, int) and code < 500:
        if _wants_html():
            if code == 404:
                title, message = tt["err_404_t"], tt["err_404_m"]
            else:
                title, message = tt["err_400_t"], tt["err_generic_m"]
            return _page("error.html", active="", title=title,
                         message=message), code
        return jsonify(error=getattr(exc, "name", "error")), code
    error_id = uuid.uuid4().hex[:8]
    app.logger.exception("Unhandled error %s", error_id)
    if _wants_html():
        return _page("error.html", active="", title=tt["err_500_t"],
                     message=tt["err_500_id"].format(error_id=error_id)), 500
    return jsonify(error="internal server error", error_id=error_id), 500


# FIX 4: защитные заголовки, без баннера с версиями
@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Server"] = "app"
    # Для сайта достаточно своих же ресурсов; только учебной странице /ui
    # (она не часть уязвимости) разрешены её inline-скрипты и стили.
    if request.path == "/ui":
        resp.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
            "connect-src 'self'; frame-ancestors 'none'")
    else:
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; img-src 'self' data:; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'; "
            "object-src 'none'")
    return resp


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A02 Security Misconfiguration — fixed',
            notes='Сайт кофейни открывается на «/» (переключатель EN/RU/UZ — '
                  'в шапке). Здесь — консоль лабы: эндпоинты и ответы сервера.',
            presets={
                'POST /login': [('неверный пароль', {'username': 'user',
                                                     'password': 'test'})],
                'GET /menu/<item_id>': [('позиция №1', '/menu/1')],
            },
            uz={'notes': 'Kafe sayti «/» manzilida (EN/RU/UZ almashtirgichi '
                         'boshqaruv panelida). Bu yerda laboratoriya konsoli.',
                'presets': {'POST /login': [('notoʻgʻri parol',
                                             {'username': 'user',
                                              'password': 'test'})],
                            'GET /menu/<item_id>': [('1-pozitsiya', '/menu/1')]}},
            en={'notes': 'The cafe site opens at "/" (EN/RU/UZ switcher in the '
                         'header). This is the lab console: endpoints and '
                         'server responses.',
                'presets': {'POST /login': [('wrong password',
                                             {'username': 'user',
                                              'password': 'test'})],
                            'GET /menu/<item_id>': [('item #1', '/menu/1')]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
