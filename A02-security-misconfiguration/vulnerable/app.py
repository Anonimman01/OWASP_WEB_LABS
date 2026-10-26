"""A02 Security Misconfiguration — УЯЗВИМАЯ версия.

Сайт кофейни Lumière Café: лендинг, меню, страницы блюд и вход для
персонала. Интерфейс многоязычный (EN / RU / UZ, переключатель в шапке).
Уязвимости здесь — неправильные НАСТРОЙКИ, а не небезопасный код: пароль
по умолчанию, открытое дерево файлов, подробные ошибки и отсутствие
защитных заголовков.

Только для обучения. Не публикуйте это приложение в интернете.
"""
import os
import traceback

from flask import (Flask, abort, g, jsonify, render_template, request,
                   send_from_directory)

from cafe import (LANGS, dashboard_data, get_item, home_data, item_data,
                  menu_data, register_lang, t as texts)

app = Flask(__name__)

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Язык запроса: ?lang=xx -> cookie -> Accept-Language. Регистрируем ДО хука
# главной страницы и ДО register_ui, чтобы g.lang было готово везде.
register_lang(app)


def _page(template, **extra):
    """Все страницы сайта проходят через один helper: язык, переводы,
    вариант лабы."""
    tt = texts()
    return render_template(template, lang=g.lang, t=tt, langs=LANGS,
                           variant_label=tt["vuln"], **extra)


def _wants_html():
    """Браузер шлёт Accept: text/html, curl/Postman — */*."""
    return "text/html" in request.headers.get("Accept", "")


# ВАЖНО для лабы: хук регистрируется ДО register_ui (см. конец файла),
# иначе браузерный запрос к "/" перехватит редирект labui на страницу /ui.
@app.before_request
def _site_index():
    if request.path == "/" and request.method == "GET" and _wants_html():
        return _page("home.html", active="home", **home_data())


@app.get("/")
def index():
    """Для curl и Postman — JSON-описание API; браузер открывает сайт (хук выше)."""
    return jsonify(
        message="Lumiere Cafe — A02 Security Misconfiguration (vulnerable)",
        endpoints=["GET /menu", "GET /menu/<item_id>", "GET /admin",
                   "POST /login", "GET /files/<path:name>"],
        langs=LANGS,
    )


@app.get("/menu")
def menu_page():
    return _page("menu.html", active="menu", **menu_data())


@app.get("/menu/<item_id>")
def menu_item(item_id):
    # ДЕФЕКТ 3: номер позиции не проверяется. Нечисловое значение роняет
    # запрос, а обработчик ошибок ниже отдаёт клиенту трассировку и конфигурацию.
    item = get_item(int(item_id))
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
    # ДЕФЕКТ 1: пароль по умолчанию admin/admin
    ok = (data.get("username") == "admin"
          and data.get("password") == "admin")
    if ok:
        if _wants_html():
            return _page("dashboard.html", active="",
                         **dashboard_data(flag="FLAG{a02_default_credentials}"))
        return jsonify(message="welcome, admin",
                       flag="FLAG{a02_default_credentials}")
    if _wants_html():
        return _page("login.html", active="", error=tt["err_cred"]), 401
    return jsonify(error="invalid credentials"), 401


# ДЕФЕКТ 2: отдаём любые файлы из корня приложения — включая .env, бэкапы
# и исходники. Наружу нужно отдавать только каталог статики.
@app.get("/files/<path:name>")
def files(name):
    return send_from_directory(APP_DIR, name)


# ДЕФЕКТ 3: подробная ошибка — трассировка и конфигурация наружу
@app.errorhandler(Exception)
def verbose_error(exc):
    tt = texts()
    code = getattr(exc, "code", None)
    if isinstance(code, int) and code < 500:
        if _wants_html():
            if code == 404:
                title, message = tt["err_404_t"], tt["err_404_m"]
            else:
                title, message = tt["err_400_t"], tt["err_generic_m"]
            return _page("error.html", active="", title=title,
                         message=message), code
        return jsonify(error=str(exc)), code

    tb = traceback.format_exc().splitlines()
    config = {"DB_URL": "postgres://labuser:LabDbPass123@db.internal:5432/cafe",
              "SECRET_KEY": "FLAG{a02_verbose_errors}",
              "APP_DIR": APP_DIR}
    if _wants_html():
        return _page("error.html", active="", title=tt["err_500_t"],
                     message=tt["err_500_m"], traceback=tb,
                     config=config), 500
    return jsonify(error=str(exc), traceback=tb, config=config), 500


# ДЕФЕКТ 4: нет защитных заголовков, зато есть баннер с версиями
@app.after_request
def add_banner(resp):
    resp.headers["X-Powered-By"] = "Flask 3.1.3 / Python 3.11"
    return resp


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402
register_ui(app, 'A02 Security Misconfiguration — vulnerable',
            notes='Сайт кофейни открывается на «/» (переключатель EN/RU/UZ — '
                  'в шапке). Здесь — консоль лабы: эндпоинты и ответы сервера.',
            presets={
                'POST /login': [('неверный пароль', {'username': 'user',
                                                     'password': 'test'})],
                'GET /menu/<item_id>': [('позиция №1', '/menu/1')],
                'GET /files/<path:name>': [('app.py', '/files/app.py')],
            },
            uz={'notes': 'Kafe sayti «/» manzilida (EN/RU/UZ almashtirgichi '
                         'boshqaruv panelida). Bu yerda laboratoriya konsoli.',
                'presets': {'POST /login': [('notoʻgʻri parol',
                                             {'username': 'user',
                                              'password': 'test'})],
                            'GET /menu/<item_id>': [('1-позиция', '/menu/1')],
                            'GET /files/<path:name>': [('app.py',
                                                        '/files/app.py')]}},
            en={'notes': 'The cafe site opens at "/" (EN/RU/UZ switcher in the '
                         'header). This is the lab console: endpoints and '
                         'server responses.',
                'presets': {'POST /login': [('wrong password',
                                             {'username': 'user',
                                              'password': 'test'})],
                            'GET /menu/<item_id>': [('item #1', '/menu/1')],
                            'GET /files/<path:name>': [('app.py',
                                                        '/files/app.py')]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
