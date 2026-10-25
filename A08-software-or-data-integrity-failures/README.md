# A08 — Software or Data Integrity Failures (нарушения целостности ПО и данных)

**Статус:** ✅ готово

## О чём лаба
Приложение принимает код и данные, подлинность которых никто не проверил: состояние пользователя в cookie, «подписанную» лицензию, обновление с зеркала, уведомление платёжной системы и скрипт со стороннего CDN. Если злоумышленник может изменить такие данные «по дороге» или в хранилище, приложение выполнит его волю.

## Чему научитесь
- Отличать контрольную сумму (хеш) от настоящей подписи (HMAC / асимметричная подпись)
- Не хранить доверенное состояние на стороне клиента без подписи
- Проверять целостность обновлений и зависимостей (lock-файлы, закреплённые хеши, подписи)
- Проверять подлинность webhook-ов: подпись, свежесть, повторная доставка (replay)
- Подключать сторонние скрипты с SRI

## Запуск

```bash
docker compose up --build
```

| Версия | Адрес |
|--------|-------|
| vulnerable (уязвимая) | http://127.0.0.1:8071 |
| fixed (исправленная) | http://127.0.0.1:8072 |

Без Docker:

```bash
pip install -r vulnerable/requirements.txt
PORT=8071 python vulnerable/app.py   # http://127.0.0.1:8071
```

> ⚠️ Приложение уязвимо специально. Запускайте только локально и не публикуйте в интернет.

## Задание
Тестовые аккаунты: `alice` / `alice123` (обычный пользователь) и `admin` (пароль вам не нужен). Работать удобно через `curl` (в Windows — Git Bash/WSL или `curl.exe`) и короткие скрипты на Python. `POST /reset-lab` сбрасывает данные лабы. Эндпоинты `/mirror/publish` и `/cdn/compromise` — лабораторные помощники: они имитируют злоумышленника, получившего доступ к зеркалу обновлений и к CDN.

1. Войдите как `alice` и получите доступ к `GET /admin`, **не зная пароля admin**.
2. Купите тариф `basic` (`POST /buy`) и получите доступ к `GET /pro`, **не платя за pro**.
3. Через автообновление (`POST /system/run-update`) подмените `payout_account` в настройках на счёт злоумышленника (флаг появится в `GET /settings`).
4. Сделайте заказ `1001` оплаченным (`GET /orders/1001` покажет ключ), **не платя**.
5. Откройте `GET /donate` в браузере, затем `POST /cdn/compromise` и перезагрузите страницу: какие реквизиты теперь видит жертва? Что изменилось в fixed?

## Эндпоинты

```
POST /login                  {"username","password"}
GET  /me
GET  /admin
POST /buy                    {"plan":"basic"}
GET  /pro
POST /system/run-update      имитация cron: автообновление с зеркала
POST /mirror/publish         {"package","version","content":{}}   (помощник: «взлом» зеркала)
GET  /settings
GET  /orders/<id>
POST /webhook/payment        {"order_id","status","amount"}
GET  /donate                 HTML-страница со сторонним скриптом
POST /cdn/compromise         (помощник: «взлом» CDN)
POST /reset-lab
```

## Подсказки

<details>
<summary>Подсказка 1 — cookie после входа</summary>

Войдите и посмотрите cookie `a08v_profile`. Это похоже на base64? Что получится, если его декодировать, изменить одно поле и закодировать обратно?
</details>

<details>
<summary>Подсказка 2 — cookie лицензии</summary>

У cookie `a08v_license` есть «подпись» после точки. Чем она считается? Нужен ли для этого какой-то секрет, который знает только сервер?
</details>

<details>
<summary>Подсказка 3 — зеркало обновлений</summary>

Что проверяет `/system/run-update` перед тем, как применить пакет с зеркала? И какие поля настроек пакет вообще имеет право менять?
</details>

<details>
<summary>Подсказка 4 — webhook</summary>

Кто, кроме платёжной системы, может отправить POST на `/webhook/payment`? Как сервер отличает настоящее уведомление от подделки?
</details>

<details>
<summary>Подсказка 5 — SRI</summary>

Посмотрите HTML страницы `/donate` в vulnerable и в fixed (исходный код страницы). Чем отличаются теги `<script>`?
</details>

## Что сравнить в fixed/
Откройте `fixed/app.py` и найдите комментарии `# FIX N`: номер совпадает с номером дефекта во `vulnerable/app.py`.

## Структура
- `vulnerable/` — уязвимая версия
- `fixed/` — исправленная версия
- `SOLUTION.md` — разбор решения (со спойлерами)
- `docker-compose.yml` — запуск обеих версий

## Дальше
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP Cheat Sheet: Deserialization](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- [SLSA](https://slsa.dev/) и [Sigstore](https://www.sigstore.dev/) — подпись и происхождение артефактов
- [MDN: Subresource Integrity](https://developer.mozilla.org/docs/Web/Security/Subresource_Integrity)
