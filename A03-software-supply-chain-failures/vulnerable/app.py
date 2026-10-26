"""A03 Software Supply Chain Failures — УЯЗВИМАЯ версия.

Сайт Kestrel CI: лендинг, тарифы, документация, страница сборок и реестр
пакетов. Интерфейс многоязычный (EN / RU / UZ, переключатель в шапке).
Уязвимости здесь — про целостность: сервер верит тому, что прислала сборка.
Хеш артефакта не пересчитывается, профиль сборки разбирается через pickle,
вебхук не подписан, а имена пакетов разрешаются по обоим индексам сразу.

Только для обучения. Не публикуйте это приложение в интернете.
"""
import base64
import json
import os
import pickle
from importlib.metadata import PackageNotFoundError, version

from flask import Flask, g, jsonify, render_template, request

from kestrel import (LANGS, builds_data, docs_data, home_data, make_result,
                     pick_newest, pricing_data, register_lang, registry_data,
                     t as texts)

app = Flask(__name__)

# Язык запроса: ?lang=xx -> cookie -> Accept-Language. Регистрируем ДО хука
# главной страницы и ДО register_ui, чтобы g.lang было готово везде.
register_lang(app)

# Флаги лабы: их выдаёт сервер, когда запрос проходит «благодаря» дефекту.
FLAG_RELEASE = "FLAG{a03_unverified_release}"
FLAG_PICKLE = "FLAG{a03_insecure_deserialization}"
FLAG_WEBHOOK = "FLAG{a03_unsigned_webhook}"
FLAG_CONFUSION = "FLAG{a03_dependency_confusion}"

DEP_PACKAGES = ["Flask", "Werkzeug", "Jinja2", "requests", "urllib3", "certifi",
                "idna"]


def _page(template, **extra):
    """Все страницы сайта проходят через один helper: язык, переводы,
    вариант лабы."""
    tt = texts()
    return render_template(template, lang=g.lang, t=tt, langs=LANGS,
                           variant_label=tt["vuln"], **extra)


def _wants_html():
    """Браузер шлёт Accept: text/html, curl/Postman — */*."""
    return "text/html" in request.headers.get("Accept", "")


def _payload():
    return request.get_json(silent=True) or request.form


def _answer(template, data, result, status=200):
    """Браузеру — страница с блоком ответа, curl — короткий JSON."""
    if _wants_html():
        return _page(template, **dict(data, result=result)), status
    return jsonify(ok=result["ok"], message=result["title"],
                   detail=result["text"], flag=result["flag"]), status


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
        message="Kestrel CI — A03 Software Supply Chain Failures (vulnerable)",
        endpoints=["GET /builds", "GET /registry", "GET /deps",
                   "POST /api/releases", "POST /api/builds/run",
                   "POST /webhooks/ci", "POST /api/registry/install"],
        langs=LANGS,
    )


@app.get("/pricing")
def pricing_page():
    return _page("pricing.html", active="pricing", **pricing_data())


@app.get("/docs")
def docs_page():
    return _page("docs.html", active="docs", **docs_data())


@app.get("/builds")
def builds_page():
    return _page("builds.html", active="builds", **builds_data())


@app.get("/registry")
def registry_page():
    return _page("registry.html", active="registry", **registry_data())


@app.get("/deps")
def deps():
    """Версии установленных пакетов — вторая часть лабы (зависимости)."""
    installed = {}
    for name in DEP_PACKAGES:
        try:
            installed[name] = version(name)
        except PackageNotFoundError:
            installed[name] = "not installed"
    return jsonify(installed)


# ДЕФЕКТ 1: хеш артефакта берётся из запроса как есть, содержимое не
# пересчитывается, подпись ни с чем не сравнивается. Сборка может выпустить
# что угодно и назвать это любым хешем.
@app.post("/api/releases")
def publish_release():
    data = _payload()
    signature = (data.get("signature") or "").strip()
    code = "release_unverified" if signature else "release_no_signature"
    return _answer("builds.html", builds_data(),
                   make_result(code, flag=FLAG_RELEASE))


# ДЕФЕКТ 2: профиль сборки разбирается через pickle — то есть выполняется
# ещё до того, как сервер посмотрит на его поля. Профиль здесь считают
# данными, хотя это код.
@app.post("/api/builds/run")
def run_build():
    data = _payload()
    profile = (data.get("profile") or "").strip()
    try:
        parsed = pickle.loads(base64.b64decode(profile))
        used_pickle = True
    except Exception:
        try:
            parsed = json.loads(profile)
        except ValueError:
            return _answer("builds.html", builds_data(),
                           make_result("build_bad_format"), 400)
        used_pickle = False

    # Значение parsed здесь не используется: важен сам факт разбора.
    del parsed
    code = "build_pickle" if used_pickle else "build_ok"
    flag = FLAG_PICKLE if used_pickle else None
    return _answer("builds.html", builds_data(), make_result(code, flag=flag))


# ДЕФЕКТ 3: событию CI верят на слово. Заголовок с подписью можно не
# присылать, а можно прислать любой — сервер его не проверяет.
@app.post("/webhooks/ci")
def ci_webhook():
    return _answer("builds.html", builds_data(),
                   make_result("webhook_accepted", flag=FLAG_WEBHOOK))


# ДЕФЕКТ 4: внутренний и публичный индексы свалены в один список, хеши не
# сверяются, а побеждает самая новая версия имени — откуда бы она ни пришла.
@app.post("/api/registry/install")
def install_package():
    data = _payload()
    name = (data.get("name") or "").strip()
    wanted = (data.get("version") or "").strip()
    package = pick_newest(name, wanted)
    if package is None:
        return _answer("registry.html", registry_data(),
                       make_result("install_unknown"), 404)
    if package["source"] == "public":
        result = make_result("install_confusion", flag=FLAG_CONFUSION)
    else:
        result = make_result("install_internal")
    return _answer("registry.html", registry_data(), result)


@app.errorhandler(404)
def not_found(exc):
    tt = texts()
    if _wants_html():
        return _page("error.html", active="", title=tt["err_404_t"],
                     message=tt["err_404_m"]), 404
    return jsonify(error="not found"), 404


@app.errorhandler(500)
def server_error(exc):
    tt = texts()
    if _wants_html():
        return _page("error.html", active="", title=tt["err_500_t"],
                     message=tt["err_500_m"]), 500
    return jsonify(error="internal error"), 500


# Учебный интерфейс /ui: не часть уязвимости, одинаков в vulnerable и fixed
from labui import register_ui  # noqa: E402

RELEASE_PRESET = {'name': 'app', 'version': '2.14.0',
                  'digest': '9f2c1ad4e7b8c0f5a1d3e6b7402c8f9a5d1e3b7c4a6f8025d9e1c3b5a7f04d21',
                  'signature': '', 'artifact': 'app-2.14.0'}
WEBHOOK_PRESET = {'build': '#4821', 'env': 'production', 'signature': ''}
PROFILE_PRESET = {'profile': '{"cache": "pip", "env": "staging"}'}

register_ui(app, 'A03 Software Supply Chain Failures — vulnerable',
            notes='Сайт Kestrel CI открывается на «/» (переключатель EN/RU/UZ — '
                  'в шапке). Сборки: /builds, реестр пакетов: /registry. '
                  'Здесь — консоль лабы: эндпоинты и ответы сервера.',
            presets={
                'POST /api/releases': [('релиз без подписи', RELEASE_PRESET)],
                'POST /api/builds/run': [('профиль сборки', PROFILE_PRESET)],
                'POST /webhooks/ci': [('вебхук без подписи', WEBHOOK_PRESET)],
                'POST /api/registry/install': [('kestrel-utils (без версии)',
                                                {'name': 'kestrel-utils'})],
                'GET /deps': [('версии пакетов', '/deps')],
            },
            uz={'notes': 'Kestrel CI sayti «/» manzilida (EN/RU/UZ almashtirgichi '
                         'boshqaruv panelida). Yig\'ishlar: /builds, paketlar '
                         'reyestri: /registry. Bu yerda laboratoriya konsoli.',
                'presets': {
                    'POST /api/releases': [('imzosiz reliz', RELEASE_PRESET)],
                    'POST /api/builds/run': [('yig\'ish profili', PROFILE_PRESET)],
                    'POST /webhooks/ci': [('imzosiz vebhuk', WEBHOOK_PRESET)],
                    'POST /api/registry/install': [('kestrel-utils (versiyasiz)',
                                                    {'name': 'kestrel-utils'})],
                    'GET /deps': [('paket versiyalari', '/deps')]}},
            en={'notes': 'The Kestrel CI site opens at "/" (EN/RU/UZ switcher in '
                         'the header). Builds: /builds, package registry: '
                         '/registry. This is the lab console: endpoints and '
                         'server responses.',
                'presets': {
                    'POST /api/releases': [('release without a signature',
                                            RELEASE_PRESET)],
                    'POST /api/builds/run': [('build profile', PROFILE_PRESET)],
                    'POST /webhooks/ci': [('webhook without a signature',
                                           WEBHOOK_PRESET)],
                    'POST /api/registry/install': [('kestrel-utils (no version)',
                                                    {'name': 'kestrel-utils'})],
                    'GET /deps': [('package versions', '/deps')]}})


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")), debug=False)
