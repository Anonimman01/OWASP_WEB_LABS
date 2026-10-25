# OWASP Top 10:2025 — учебные лаборатории

Открытый проект с учебными лабами по каждой категории **OWASP Top 10:2025**.
Лабы намеренно уязвимы: их можно скачать через Git, запустить у себя и безопасно потренироваться находить и исправлять уязвимости.

> ⚠️ **Важно.** Приложения в этом репозитории специально уязвимы.
> - Запускайте их только локально (`127.0.0.1`) или в изолированной среде (Docker, виртуальная машина).
> - **Никогда не выкладывайте их в интернет.**
> - Применяйте полученные знания только на своих системах или на тех, где у вас есть явное разрешение на тестирование.

## Список лаб

| №   | Папка | Категория | Статус |
|-----|-------|-----------|--------|
| A01 | [A01-broken-access-control](./A01-broken-access-control) | Нарушение контроля доступа | 🕓 запланировано |
| A02 | [A02-security-misconfiguration](./A02-security-misconfiguration) | Небезопасная конфигурация | 🕓 запланировано |
| A03 | [A03-software-supply-chain-failures](./A03-software-supply-chain-failures) | Сбои в цепочке поставок ПО | 🕓 запланировано |
| A04 | [A04-cryptographic-failures](./A04-cryptographic-failures) | Криптографические сбои | 🕓 запланировано |
| A05 | [A05-injection](./A05-injection) | Инъекции (SQLi, XSS и др.) | 🕓 запланировано |
| A06 | [A06-insecure-design](./A06-insecure-design) | Небезопасная архитектура | 🕓 запланировано |
| A07 | [A07-authentication-failures](./A07-authentication-failures) | Сбои аутентификации | 🕓 запланировано |
| A08 | [A08-software-or-data-integrity-failures](./A08-software-or-data-integrity-failures) | Нарушения целостности ПО и данных | 🕓 запланировано |
| A09 | [A09-logging-and-alerting-failures](./A09-logging-and-alerting-failures) | Сбои логирования и оповещений | 🕓 запланировано |
| A10 | [A10-mishandling-of-exceptional-conditions](./A10-mishandling-of-exceptional-conditions) | Неверная обработка исключительных ситуаций | 🕓 запланировано |

## Как устроена каждая лаба

```
AXX-название-категории/
  README.md            описание, цель, подсказки
  vulnerable/          уязвимая версия приложения
  fixed/               исправленная версия (для сравнения)
  docker-compose.yml   запуск одной командой
```

Формат «сломай → почини»: сначала находим уязвимость в `vulnerable/`, затем смотрим, как она исправлена в `fixed/`.

## Быстрый старт

```bash
git clone <адрес-репозитория>
cd owasp-labs/A01-broken-access-control
docker compose up
```

Приложение откроется на `http://127.0.0.1:8080` (порт может отличаться, смотрите README конкретной лабы).

## Полезные ссылки

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)
- OWASP ASVS и Web Security Testing Guide — для более глубокого изучения

