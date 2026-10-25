# OWASP Top 10:2025 — учебные лаборатории

Открытый проект с учебными лабами по каждой категории **OWASP Top 10:2025**.
Лабы намеренно уязвимы: их можно скачать через Git, запустить у себя и безопасно потренироваться находить и исправлять уязвимости.

> ⚠️ **Важно.** Приложения в этом репозитории специально уязвимы.
> - Запускайте их только локально (`127.0.0.1`) или в изолированной среде (Docker, виртуальная машина).
> - **Никогда не выкладывайте их в интернет.**
> - Применяйте полученные знания только на своих системах или на тех, где у вас есть явное разрешение на тестирование.

## Список лаб

| №   | Папка | Категория | Порты (vulnerable / fixed) | Статус |
|-----|-------|-----------|----------------------------|--------|
| A01 | [A01-broken-access-control](./A01-broken-access-control) | Нарушение контроля доступа | 8001 / 8002 | ✅ готово |
| A02 | [A02-security-misconfiguration](./A02-security-misconfiguration) | Небезопасная конфигурация | 8011 / 8012 | ✅ готово |
| A03 | [A03-software-supply-chain-failures](./A03-software-supply-chain-failures) | Сбои в цепочке поставок ПО | 8021 / 8022 | ✅ готово |
| A04 | [A04-cryptographic-failures](./A04-cryptographic-failures) | Криптографические сбои | 8031 / 8032 | ✅ готово |
| A05 | [A05-injection](./A05-injection) | Инъекции (SQLi, XSS и др.) | 8041 / 8042 | ✅ готово |
| A06 | [A06-insecure-design](./A06-insecure-design) | Небезопасная архитектура | — | 🕓 запланировано |
| A07 | [A07-authentication-failures](./A07-authentication-failures) | Сбои аутентификации | — | 🕓 запланировано |
| A08 | [A08-software-or-data-integrity-failures](./A08-software-or-data-integrity-failures) | Нарушения целостности ПО и данных | — | 🕓 запланировано |
| A09 | [A09-logging-and-alerting-failures](./A09-logging-and-alerting-failures) | Сбои логирования и оповещений | — | 🕓 запланировано |
| A10 | [A10-mishandling-of-exceptional-conditions](./A10-mishandling-of-exceptional-conditions) | Неверная обработка исключительных ситуаций | — | 🕓 запланировано |

## Как устроена каждая лаба

```
AXX-название-категории/
  README.md            описание, цель, подсказки
  SOLUTION.md          разбор решения (со спойлерами)
  vulnerable/          уязвимая версия приложения
  fixed/               исправленная версия (для сравнения)
  Dockerfile
  docker-compose.yml   запуск одной командой
```

Формат «сломай → почини»: сначала находим уязвимость в `vulnerable/`, затем смотрим, как она исправлена в `fixed/`.

## Быстрый старт

Нужны Git и Docker (с плагином Compose).

```bash
git clone https://github.com/Anonimman01/OWASP_WEB_LABS.git
cd OWASP_WEB_LABS/A01-broken-access-control
docker compose up --build
```

Обе версии (уязвимая и исправленная) запускаются одновременно на портах из таблицы выше, только на `127.0.0.1`.

Без Docker (нужен Python 3.11+):

```bash
cd OWASP_WEB_LABS/A01-broken-access-control
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

## Полезные ссылки

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)
- OWASP ASVS и Web Security Testing Guide — для более глубокого изучения

