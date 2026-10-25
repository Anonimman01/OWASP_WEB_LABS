🌐 **Русский** · [Oʻzbekcha](./SOLUTION.uz.md)

# A03 — Решение (спойлеры!)

Сначала попробуйте пройти лабу сами, используя подсказки из [README](./README.md).

## Поиск уязвимых зависимостей

```bash
pip install pip-audit
pip-audit -r vulnerable/requirements.txt --no-deps --disable-pip
```

`--no-deps --disable-pip` нужны, потому что все версии в файле уже закреплены и ничего устанавливать для проверки не требуется.

На момент создания лабы (октябрь 2026) `pip-audit` находит уведомления в **семи** пакетах:

| Пакет | Версия | Как попал в проект |
|-------|--------|--------------------|
| Flask | 2.2.2 | напрямую |
| Werkzeug | 2.2.2 | зависимость Flask |
| Jinja2 | 3.1.2 | зависимость Flask |
| requests | 2.25.1 | напрямую |
| urllib3 | 1.26.4 | зависимость requests |
| idna | 2.10 | зависимость requests |
| certifi | 2024.8.30 | зависимость requests |

Большинство проблем находится в **транзитивных** зависимостях: в проекте их никто не выбирал, но они работают в продакшене. Точные числа и идентификаторы со временем меняются, потому что базы уязвимостей пополняются.

## Исправление (fixed)

1. Обновлены версии: Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6, requests 2.33.0 (и их зависимости).
2. В `requirements.in` перечислены только прямые зависимости, а `requirements.txt` сгенерирован `pip-compile` вместе со всеми транзитивными пакетами и хешами:

   ```bash
   pip install pip-tools
   pip-compile --generate-hashes --strip-extras --output-file=requirements.txt requirements.in
   ```

3. Установка в Docker идёт с `--require-hashes`: pip откажется ставить пакет, если его содержимое не совпадает с хешем.

Проверка:

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip
# No known vulnerabilities found
```

## Эксперимент с хешем

```bash
sed 's/--hash=sha256:[0-9a-f]\{64\}/--hash=sha256:0000000000000000000000000000000000000000000000000000000000000000/g' \
  fixed/requirements.txt > tampered.txt
python -m venv /tmp/venv-test
/tmp/venv-test/bin/pip install --require-hashes -r tampered.txt
```

Результат: `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE ...`, установка не выполняется. Так pip защищает от подмены пакета на пути с индекса.

> Эксперимент нужно делать в **чистом** окружении: если пакеты уже установлены, pip их не скачивает и хеши не сверяет.

## SBOM

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip -f cyclonedx-json -o sbom.json
```

Получится перечень компонентов проекта в формате CycloneDX (JSON). Его можно хранить рядом с релизом и сверять с новыми уведомлениями.

## Что ещё стоит помнить
- Lock-файл с хешами защищает от подмены, но **не** от уязвимостей: версии всё равно нужно обновлять.
- Проверку зависимостей стоит запускать автоматически (например, в CI) и по расписанию.
- Эта лаба не показывает вредоносные пакеты. Подмена внутреннего пакета публичным (dependency confusion) и опечатки в именах (typosquatting) разбираются теоретически: ставьте только то, что ожидаете, из доверенных индексов.
