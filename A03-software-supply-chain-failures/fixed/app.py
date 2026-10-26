"""A03 Software Supply Chain Failures — ИСПРАВЛЕННАЯ версия.

Тот же сайт Kestrel CI (шаблоны и kestrel.py побайтно совпадают с vulnerable).
Отличие только в app.py: сервер проверяет целостность того, что ему прислали,
и не разбирает данные как код.

Только для обучения. Не публикуйте это приложение в интернете.
"""
import hashlib
import hmac
import json
import os
from importlib.metadata import PackageNotFoundError, version

from flask import Flask, g, jsonify, render_template, request

from kestrel import (INDEX_DIGESTS, LANGS, LOCKED_DIGESTS, PROJECT_KEY,
                     PUBLIC_MIRROR, builds_data, docs_data, find_internal,
                     home_data, make_result, pricing_data, register_lang,
                     registry_data, t as texts)

app = Flask(__name__)

register_lang(app)

DEP_PACKAGES = ["Flask", "Werkzeug", "Jinja2", "requests", "urllib3", "certifi",
                "idna"]


def _page(template, **extra):
    tt = texts()
    return render_template(template, lang=g.lang, t=tt, langs=LANGS,
                           variant_label=tt["fixed"], **extra)


def _wants_html():
    return "text/html" in request.headers.get("Accept", "")


def _payload():
    return request.get_json(silent=True) or request.form


def _answer(template, data, result, status=200):
    """Браузеру — страница с блоком ответа, curl — короткий JSON."""
    if _wants_html():
        return _page(template, **dict(data, result=result)), status
    return jsonify(ok=result["ok"], message=result["title"],
                   detail=result["text"]), status


def _sign(body):
    """HMAC-SHA256 тела запроса ключом проекта."""
    return hmac.new(PROJECT_KEY.encode(), body, hashlib.sha256).hexdigest()


@app.before_request
def _site_index():
    if request.path == "/" and request.method == "GET" and _wants_html():
        return _page("home.html", active="home", **home_data())


@app.get("/")
def index():
    return jsonify(
        message="Kestrel CI — A03 Software Supply Chain Failures (fixed)",
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
    installed = {}
    for name in DEP_PACKAGES:
        try:
            installed[name] = version(name)
        except PackageNotFoundError:
            installed[name] = "not installed"
    return jsonify(installed)


# ИСПРАВЛЕНО: сервер сам считает SHA-256 от содержимого артефакта, сверяет
# его с заявленным и проверяет HMAC-подпись ключом проекта.
@app.post("/api/releases")
def publish_release():
    data = _payload()
    artifact = data.get("artifact") or ""
    declared = (data.get("digest") or "").strip().lower()
    declared = declared.replace("sha256:", "")
    signature = (data.get("signature") or "").strip().lower()

    actual = hashlib.sha256(artifact.encode()).hexdigest()
    if not declared or not hmac.compare_digest(declared, actual):
        return _answer("builds.html", builds_data(),
                       make_result("release_bad_digest"), 400)

    if not signature or not hmac.compare_digest(signature, _sign(actual.encode())):
        return _answer("builds.html", builds_data(),
                       make_result("release_bad_signature"), 400)

    return _answer("builds.html", builds_data(), make_result("release_accepted"))


# ИСПРАВЛЕНО: профиль — это данные. Читаем только JSON и никогда не
# восстанавливаем из него объекты.
@app.post("/api/builds/run")
def run_build():
    data = _payload()
    profile = (data.get("profile") or "").strip()
    try:
        parsed = json.loads(profile)
    except ValueError:
        return _answer("builds.html", builds_data(),
                       make_result("build_bad_format"), 400)
    if not isinstance(parsed, dict):
        return _answer("builds.html", builds_data(),
                       make_result("build_bad_format"), 400)
    return _answer("builds.html", builds_data(), make_result("build_ok"))


# ИСПРАВЛЕНО: событие CI принимается только с подписью, которая сходится
# с телом запроса. Сравнение — constant-time.
@app.post("/webhooks/ci")
def ci_webhook():
    body = request.get_data()
    header = (request.headers.get("X-Kestrel-Signature") or "").strip().lower()
    header = header.replace("sha256=", "")
    if not header or not hmac.compare_digest(header, _sign(body)):
        return _answer("builds.html", builds_data(),
                       make_result("webhook_rejected"), 403)
    return _answer("builds.html", builds_data(), make_result("webhook_verified"))


# ИСПРАВЛЕНО: имена разрешаются только по внутреннему индексу, версия должна
# быть закреплена, а хеш — совпадать с lock-файлом.
@app.post("/api/registry/install")
def install_package():
    data = _payload()
    name = (data.get("name") or "").strip()
    wanted = (data.get("version") or "").strip()

    package = find_internal(name, wanted)
    if package is None:
        in_public = any(item["name"] == name for item in PUBLIC_MIRROR)
        code = "install_public_blocked" if in_public else "install_unknown"
        return _answer("registry.html", registry_data(), make_result(code), 404)

    if not wanted:
        return _answer("registry.html", registry_data(),
                       make_result("install_unpinned"), 400)

    served = INDEX_DIGESTS.get((package["name"], package["version"]))
    pinned = LOCKED_DIGESTS.get((package["name"], package["version"]))
    if not served or not pinned or not hmac.compare_digest(served, pinned):
        return _answer("registry.html", registry_data(),
                       make_result("install_hash_mismatch"), 400)

    return _answer("registry.html", registry_data(),
                   make_result("install_internal"))


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

register_ui(app, 'A03 Software Supply Chain Failures — fixed',
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
