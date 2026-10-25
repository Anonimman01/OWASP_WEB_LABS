"""A03 Software Supply Chain Failures — учебное приложение (fixed).

Код приложения тот же. Исправление находится в зависимостях:
обновлённые версии и lock-файл с хешами (requirements.txt).
"""
from importlib.metadata import PackageNotFoundError, version

from flask import Flask, jsonify

app = Flask(__name__)

PACKAGES = ["Flask", "Werkzeug", "Jinja2", "requests", "urllib3", "certifi", "idna"]


def installed_versions():
    result = {}
    for name in PACKAGES:
        try:
            result[name] = version(name)
        except PackageNotFoundError:
            result[name] = "not installed"
    return result


@app.get("/")
def index():
    return jsonify(
        message="A03 Software Supply Chain Failures lab (fixed)",
        endpoints=["GET /deps"],
        hint="Проверьте зависимости: pip-audit -r requirements.txt",
    )


@app.get("/deps")
def deps():
    return jsonify(installed_versions())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
