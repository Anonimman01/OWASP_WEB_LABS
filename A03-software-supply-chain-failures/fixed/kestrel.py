"""Сайт Kestrel CI — данные, переводы и помощники страниц.

Файл одинаковый в vulnerable/ и fixed/ (побайтно), как cafe.py в A02:
содержимое сайта от версии не зависит, все отличия — в app.py.

Kestrel CI — вымышленный SaaS для сборки и доставки релизов. Страницы:
лендинг, тарифы, документация, страница сборок и реестр пакетов.
Язык интерфейса: EN / RU / UZ. Выбор хранится в cookie `site_lang`
и задаётся ссылкой `?lang=xx` (переключатель в шапке сайта).
"""
from flask import g, request

LANGS = ["en", "ru", "uz"]
DEFAULT_LANG = "en"
LANG_COOKIE = "site_lang"

BRAND = "KESTREL"
BRAND_SUFFIX = "CI"

# Лабораторный ключ проекта: им подписываются релизы и вебхуки.
PROJECT_KEY = "kestrel-lab-project-key"

# ------------------------------------------------------------------ переводы
T = {
    "en": {
        "nav_product": "Product", "nav_pricing": "Pricing", "nav_docs": "Docs",
        "nav_builds": "Builds", "nav_registry": "Registry",
        "nav_label": "Main navigation", "lang_label": "Language",
        "cta_console": "Open console", "cta_docs": "Documentation",

        "hero_eyebrow": "CI/CD for teams under fifty",
        "hero_l1": "Build twice as fast.",
        "hero_l2": "Ship signed.",
        "hero_text": "Kestrel runs your pipeline, caches dependencies and hands "
                     "back an artifact with a digest and a signature. One file "
                     "in the repository, no self-hosted runners to look after.",
        "hero_btn": "Start for free", "hero_btn2": "See how it works",
        "term_title": "release pipeline",
        "term_deps": "dependency cache restored",
        "term_tests": "tests passed",
        "term_build": "image built",
        "term_sign": "artifact signed",
        "term_push": "pushed to registry",

        "stat_build": "median build time", "stat_teams": "teams on Kestrel",
        "stat_uptime": "uptime last 12 months", "stat_reviews": "releases a day",

        "feat_eyebrow": "What you get", "feat_title": "Everything a small team needs",
        "feat_lead": "No plugin marketplace and no YAML generator: four things "
                     "that cover the whole path from a commit to production.",

        "how_eyebrow": "How it works", "how_title": "Three steps to the first release",

        "cta_band_title": "Ship your next release with a signature on it",
        "cta_band_text": "The free plan covers private repositories and one "
                         "concurrent build. No card required.",

        "pricing_eyebrow": "Pricing", "pricing_title": "Plans that scale with the team",
        "pricing_lead": "Per user, per month, billed yearly. The free plan does "
                        "not expire.",
        "per_month": "per user / month",
        "plan_free_name": "Starter", "plan_team_name": "Team",
        "plan_biz_name": "Business", "plan_free_price": "0",
        "plan_team_price": "29", "plan_biz_price": "99",
        "plan_free_text": "For side projects and the first prototype.",
        "plan_team_text": "For product teams shipping every week.",
        "plan_biz_text": "For companies with requirements and audits.",
        "plan_cta_free": "Start now", "plan_cta_paid": "Choose plan",
        "plan_pop": "Popular",
        "plan_free_f": ["Private repositories", "1 concurrent build",
                        "7-day build history", "Community support"],
        "plan_team_f": ["Unlimited concurrent builds", "Signed artifacts",
                        "Private dependency mirror", "90-day build history",
                        "Support within one day"],
        "plan_biz_f": ["SSO and audit log", "Release approvals",
                       "Self-hosted runners", "Retention up to 2 years",
                       "Support within two hours"],
        "included_h": "In every plan",
        "included": ["Reproducible builds", "Artifact digests (SHA-256)",
                     "Signed CI webhooks", "SBOM on every release"],
        "pricing_note_h": "Self-hosted",
        "pricing_note": "Kestrel runs inside your network on request: the same "
                        "pipeline, your own runners and your own artifact store.",

        "docs_eyebrow": "Documentation", "docs_title": "Quick start",
        "docs_lead": "From an empty repository to a signed release in about ten "
                     "minutes. Everything below works with the lab instance you "
                     "have open.",
        "docs_nav_qs": "Install the CLI", "docs_nav_pipeline": "Pipeline file",
        "docs_nav_signing": "Signing and verification",
        "docs_nav_api": "HTTP API", "docs_nav_console": "Lab console",
        "docs_qs_title": "1. Install the CLI",
        "docs_qs_text": "The CLI talks to the Kestrel API. Point it at your "
                        "instance with KESTREL_URL: port 5000 for a direct run, "
                        "8021 or 8022 under docker compose.",
        "docs_pipe_title": "2. Describe the pipeline",
        "docs_pipe_text": "Stages run in order, the dependency cache is restored "
                          "before the tests. Secrets stay in the project "
                          "settings, never in this file.",
        "docs_sign_title": "3. Sign the release",
        "docs_sign_text": "Kestrel computes the SHA-256 digest of the artifact "
                          "and signs it with HMAC-SHA256 using the project key. "
                          "Verification before deploy is a two-line call.",
        "docs_sign_warn": "The key below is the lab key from this instance. In "
                          "production it lives in the project settings and is "
                          "never committed.",
        "docs_api_title": "HTTP API",
        "docs_api_text": "The same endpoints the console and the CLI use. "
                         "Browser requests render a page, curl gets JSON.",
        "docs_api_method": "Method", "docs_api_path": "Endpoint",
        "docs_api_desc": "What it does",
        "docs_console_title": "Lab console",
        "docs_console_text": "Forms for every endpoint, with ready-made requests "
                             "and the server responses in one place.",
        "docs_console_btn": "Open /ui",

        "builds_eyebrow": "Workspace", "builds_title": "Builds",
        "builds_lead": "Every run keeps the commit, the duration and the digest "
                       "of the artifact it produced.",
        "builds_stat_median": "median build", "builds_stat_today": "runs today",
        "builds_stat_failed": "failed today",
        "runs_h": "Recent runs", "builds_branch": "branch",
        "col_no": "Run", "col_branch": "Branch", "col_commit": "Commit",
        "col_status": "Status", "col_time": "Duration", "col_digest": "Artifact digest",
        "run_ok": "passed", "run_failed": "failed", "run_running": "running",
        "run_queued": "queued",
        "release_h": "Publish a release",
        "release_text": "Send the artifact and the digest Kestrel should record. "
                        "The signature is the HMAC of the digest with the "
                        "project key.",
        "f_name": "Package", "f_version": "Version", "f_digest": "Digest (SHA-256)",
        "f_signature": "Signature (HMAC-SHA256)", "f_artifact": "Artifact body",
        "f_submit_release": "Publish release",
        "profile_h": "Run a build from a profile",
        "profile_text": "Profiles are the saved parameters of a run: cache "
                        "policy, environment and stage overrides, sent as a "
                        "base64 blob.",
        "f_submit_profile": "Run build",
        "webhook_h": "CI webhooks",
        "webhook_text": "The pipeline sends one signed POST to /webhooks/ci when "
                        "a build finishes. Use it to promote a release or to "
                        "ping a chat.",
        "result_h": "Response",
        "result_flag_h": "Lab flag",
        "hint_release": "The digest in the example does not match the artifact "
                         "body. Watch what the server does with it.",
        "hint_profile": "This form sends JSON. The API also takes a base64 "
                         "blob of a serialized profile.",
        "hint_webhook": "The signature field is optional here: send the "
                         "request with an empty one and see what the server "
                         "requires.",
        "webhook_send": "Send event",

        "reg_eyebrow": "Packages", "reg_title": "Dependency registry",
        "reg_lead": "Your own wheels and sdists live next to the public ones. "
                    "Builds resolve names through this registry.",
        "reg_internal_h": "Internal index",
        "reg_internal_text": "Built by your team and published from CI.",
        "reg_public_h": "Public mirror",
        "reg_public_text": "Third-party packages, forwarded from the upstream "
                           "index as they are.",
        "col_pkg": "Package", "col_version": "Version", "col_kind": "Format",
        "col_size": "Size", "col_sum": "SHA-256", "col_publisher": "Publisher",
        "kind_wheel": "wheel", "kind_sdist": "sdist",
        "badge_pinned": "pinned",
        "install_h": "Install a package",
        "install_text": "Build-time resolution: a name without a version takes "
                        "the newest one available.",
        "f_pkg_name": "Package name", "f_pkg_version": "Version (optional)",
        "f_submit_install": "Resolve and install",
        "reg_hint_h": "Why the digests matter",
        "reg_hint": "The lock file of a project pins the digest of every "
                    "dependency. Resolution without it trusts whatever the "
                    "index returns.",

        "err_404_t": "Page not found",
        "err_404_m": "Check the address or go back to the home page.",
        "err_500_t": "Internal server error",
        "err_500_m": "Something went wrong. Please try again later.",
        "go_home": "Go to the homepage",

        "vuln": "Vulnerable version", "fixed": "Fixed version",
        "foot_about": "Continuous delivery for small teams: pipelines, signed "
                      "artifacts and a private dependency registry.",
        "foot_product": "Product", "foot_dev": "Developers",
        "foot_console": "Lab console /ui", "foot_deps": "Installed versions /deps",
        "foot_note": "Training site for lab A03 (Software Supply Chain "
                     "Failures). Run it locally only.",
    },
    "ru": {
        "nav_product": "Продукт", "nav_pricing": "Тарифы", "nav_docs": "Документация",
        "nav_builds": "Сборки", "nav_registry": "Реестр",
        "nav_label": "Главное меню", "lang_label": "Язык",
        "cta_console": "Открыть консоль", "cta_docs": "Документация",

        "hero_eyebrow": "CI/CD для команд до пятидесяти человек",
        "hero_l1": "Собирайте вдвое быстрее.",
        "hero_l2": "Доставляйте подписанным.",
        "hero_text": "Kestrel прогоняет пайплайн, кэширует зависимости и отдаёт "
                     "артефакт вместе с его хешем и подписью. Один файл в "
                     "репозитории — и никаких собственных раннеров, за которыми "
                     "нужно следить.",
        "hero_btn": "Начать бесплатно", "hero_btn2": "Как это работает",
        "term_title": "пайплайн релиза",
        "term_deps": "кэш зависимостей восстановлен",
        "term_tests": "тесты прошли",
        "term_build": "образ собран",
        "term_sign": "артефакт подписан",
        "term_push": "отправлен в реестр",

        "stat_build": "медианная сборка", "stat_teams": "команд на Kestrel",
        "stat_uptime": "доступность за 12 месяцев", "stat_reviews": "релизов в день",

        "feat_eyebrow": "Что внутри", "feat_title": "Всё, что нужно небольшой команде",
        "feat_lead": "Без магазина плагинов и генератора YAML: четыре вещи, "
                     "которые закрывают путь от коммита до продакшена.",

        "how_eyebrow": "Как это работает", "how_title": "Три шага до первого релиза",

        "cta_band_title": "Выпустите следующий релиз с подписью",
        "cta_band_text": "На бесплатном плане есть приватные репозитории и одна "
                         "одновременная сборка. Карта не нужна.",

        "pricing_eyebrow": "Тарифы", "pricing_title": "Планы, которые растут вместе с командой",
        "pricing_lead": "За пользователя в месяц, оплата за год. Бесплатный план "
                        "не заканчивается.",
        "per_month": "за пользователя в месяц",
        "plan_free_name": "Starter", "plan_team_name": "Team",
        "plan_biz_name": "Business", "plan_free_price": "0",
        "plan_team_price": "29", "plan_biz_price": "99",
        "plan_free_text": "Для пет-проектов и первого прототипа.",
        "plan_team_text": "Для продуктовых команд, которые выпускают каждую неделю.",
        "plan_biz_text": "Для компаний с требованиями и аудитом.",
        "plan_cta_free": "Начать", "plan_cta_paid": "Выбрать план",
        "plan_pop": "Популярный",
        "plan_free_f": ["Приватные репозитории", "1 одновременная сборка",
                        "История сборок 7 дней", "Поддержка в сообществе"],
        "plan_team_f": ["Неограниченно сборок одновременно", "Подписанные артефакты",
                        "Приватное зеркало зависимостей", "История сборок 90 дней",
                        "Ответ поддержки в течение дня"],
        "plan_biz_f": ["SSO и журнал аудита", "Подтверждение релизов",
                       "Свои раннеры", "Хранение истории до 2 лет",
                       "Ответ поддержки в течение двух часов"],
        "included_h": "Во всех планах",
        "included": ["Воспроизводимые сборки", "Хеш артефакта (SHA-256)",
                     "Подписанные вебхуки CI", "SBOM на каждый релиз"],
        "pricing_note_h": "Self-hosted",
        "pricing_note": "Kestrel разворачивается и внутри вашей сети: тот же "
                        "пайплайн, свои раннеры и своё хранилище артефактов.",

        "docs_eyebrow": "Документация", "docs_title": "Быстрый старт",
        "docs_lead": "От пустого репозитория до подписанного релиза — примерно "
                     "десять минут. Всё ниже работает на том экземпляре лабы, "
                     "который у вас открыт.",
        "docs_nav_qs": "Установка CLI", "docs_nav_pipeline": "Файл пайплайна",
        "docs_nav_signing": "Подпись и проверка",
        "docs_nav_api": "HTTP API", "docs_nav_console": "Консоль лабы",
        "docs_qs_title": "1. Установите CLI",
        "docs_qs_text": "CLI обращается к API Kestrel. Адрес задаётся "
                        "переменной KESTREL_URL: порт 5000 при прямом запуске, "
                        "8021 или 8022 под docker compose.",
        "docs_pipe_title": "2. Опишите пайплайн",
        "docs_pipe_text": "Стадии идут по порядку, кэш зависимостей "
                          "восстанавливается до тестов. Секреты лежат в "
                          "настройках проекта, а не в этом файле.",
        "docs_sign_title": "3. Подпишите релиз",
        "docs_sign_text": "Kestrel считает SHA-256 от артефакта и подписывает "
                          "хеш алгоритмом HMAC-SHA256 ключом проекта. Проверка "
                          "перед деплоем — это две строки.",
        "docs_sign_warn": "Ключ ниже — лабораторный, из этого экземпляра. В "
                          "продакшене он лежит в настройках проекта и в "
                          "репозиторий не попадает.",
        "docs_api_title": "HTTP API",
        "docs_api_text": "Те же эндпоинты, что используют консоль и CLI. "
                         "Запрос из браузера получает страницу, curl — JSON.",
        "docs_api_method": "Метод", "docs_api_path": "Эндпоинт",
        "docs_api_desc": "Что делает",
        "docs_console_title": "Консоль лабы",
        "docs_console_text": "Формы для всех эндпоинтов: готовые запросы и "
                             "ответы сервера в одном месте.",
        "docs_console_btn": "Открыть /ui",

        "builds_eyebrow": "Рабочее пространство", "builds_title": "Сборки",
        "builds_lead": "У каждого запуска сохраняются коммит, длительность и "
                       "хеш артефакта, который он собрал.",
        "builds_stat_median": "медианная сборка", "builds_stat_today": "запусков сегодня",
        "builds_stat_failed": "упало сегодня",
        "runs_h": "Последние запуски", "builds_branch": "ветка",
        "col_no": "Запуск", "col_branch": "Ветка", "col_commit": "Коммит",
        "col_status": "Статус", "col_time": "Длительность", "col_digest": "Хеш артефакта",
        "run_ok": "успешно", "run_failed": "ошибка", "run_running": "выполняется",
        "run_queued": "в очереди",
        "release_h": "Опубликовать релиз",
        "release_text": "Передайте артефакт и хеш, который Kestrel должен "
                        "записать. Подпись — это HMAC от хеша ключом проекта.",
        "f_name": "Пакет", "f_version": "Версия", "f_digest": "Хеш (SHA-256)",
        "f_signature": "Подпись (HMAC-SHA256)", "f_artifact": "Содержимое артефакта",
        "f_submit_release": "Опубликовать релиз",
        "profile_h": "Сборка по профилю",
        "profile_text": "Профиль — сохранённые параметры запуска: политика кэша, "
                        "окружение и переопределения стадий. Передаётся "
                        "base64-блобом.",
        "f_submit_profile": "Запустить сборку",
        "webhook_h": "Вебхуки CI",
        "webhook_text": "Когда сборка заканчивается, пайплайн отправляет один "
                        "подписанный POST на /webhooks/ci. Им удобно "
                        "переводить релиз в прод или писать в чат.",
        "result_h": "Ответ сервера",
        "result_flag_h": "Флаг лабы",
        "hint_release": "Хеш в примере не совпадает с содержимым артефакта. "
                         "Посмотрите, что с ним сделает сервер.",
        "hint_profile": "Эта форма отправляет JSON. API принимает и "
                         "base64-блоб сериализованного профиля.",
        "hint_webhook": "Поле подписи здесь необязательное: отправьте запрос "
                         "с пустым и посмотрите, что потребует сервер.",
        "webhook_send": "Отправить событие",

        "reg_eyebrow": "Пакеты", "reg_title": "Реестр зависимостей",
        "reg_lead": "Свои wheel- и sdist-пакеты лежат рядом с публичными. "
                    "Сборки разрешают имена через этот реестр.",
        "reg_internal_h": "Внутренний индекс",
        "reg_internal_text": "Собрано вашей командой и опубликовано из CI.",
        "reg_public_h": "Публичное зеркало",
        "reg_public_text": "Сторонние пакеты, проброшенные с внешнего индекса "
                           "как есть.",
        "col_pkg": "Пакет", "col_version": "Версия", "col_kind": "Формат",
        "col_size": "Размер", "col_sum": "SHA-256", "col_publisher": "Издатель",
        "kind_wheel": "wheel", "kind_sdist": "sdist",
        "badge_pinned": "закреплён",
        "install_h": "Установить пакет",
        "install_text": "Разрешение имени на этапе сборки: имя без версии "
                        "берёт самую новую доступную.",
        "f_pkg_name": "Имя пакета", "f_pkg_version": "Версия (необязательно)",
        "f_submit_install": "Разрешить и установить",
        "reg_hint_h": "Зачем нужны хеши",
        "reg_hint": "Lock-файл проекта закрепляет хеш каждой зависимости. "
                    "Разрешение без него доверяет тому, что вернёт индекс.",

        "err_404_t": "Страница не найдена",
        "err_404_m": "Проверьте адрес или вернитесь на главную.",
        "err_500_t": "Внутренняя ошибка сервера",
        "err_500_m": "Что-то пошло не так. Попробуйте позже.",
        "go_home": "На главную",

        "vuln": "Уязвимая версия", "fixed": "Исправленная версия",
        "foot_about": "Непрерывная доставка для небольших команд: пайплайны, "
                      "подписанные артефакты и свой реестр зависимостей.",
        "foot_product": "Продукт", "foot_dev": "Разработчикам",
        "foot_console": "Консоль лабы /ui",
        "foot_deps": "Версии пакетов /deps",
        "foot_note": "Учебный сайт лабы A03 (Software Supply Chain Failures). "
                     "Запускайте только локально.",
    },
    "uz": {
        "nav_product": "Mahsulot", "nav_pricing": "Narxlar", "nav_docs": "Hujjatlar",
        "nav_builds": "Yig'ishlar", "nav_registry": "Reyestr",
        "nav_label": "Asosiy menyu", "lang_label": "Til",
        "cta_console": "Konsolni ochish", "cta_docs": "Hujjatlar",

        "hero_eyebrow": "Ellik kishigacha bo'lgan jamoalar uchun CI/CD",
        "hero_l1": "Ikki barobar tez yig'ing.",
        "hero_l2": "Imzolangan holda yetkazing.",
        "hero_text": "Kestrel quvurni ishga tushiradi, bog'liqliklarni keshlaydi "
                     "va artefaktni xesh hamda imzo bilan qaytaradi. Repozitoriyda "
                     "bitta fayl — o'z runnerlarini kuzatish shart emas.",
        "hero_btn": "Bepul boshlash", "hero_btn2": "Bu qanday ishlaydi",
        "term_title": "reliz quvuri",
        "term_deps": "bog'liqlik keshi tiklandi",
        "term_tests": "testlar o'tdi",
        "term_build": "obraz yig'ildi",
        "term_sign": "artefakt imzolandi",
        "term_push": "reyestrga yuborildi",

        "stat_build": "o'rtacha yig'ish vaqti", "stat_teams": "Kestrel'dagi jamoa",
        "stat_uptime": "12 oylik ish vaqti", "stat_reviews": "kuniga reliz",

        "feat_eyebrow": "Nima bor", "feat_title": "Kichik jamoa uchun yetarli hamma narsa",
        "feat_lead": "Plaginlar do'koni va YAML generatorisiz: kommitdan "
                     "prodakshngacha bo'lgan yo'lni yopadigan to'rt narsa.",

        "how_eyebrow": "Qanday ishlaydi", "how_title": "Birinchi relizgacha uch qadam",

        "cta_band_title": "Keyingi relizni imzo bilan chiqaring",
        "cta_band_text": "Bepul rejada yopiq repozitoriylar va bitta bir vaqtli "
                         "yig'ish bor. Karta kerak emas.",

        "pricing_eyebrow": "Narxlar", "pricing_title": "Jamoa bilan o'sadigan rejalar",
        "pricing_lead": "Foydalanuvchi uchun oyiga, yillik to'lovda. Bepul reja "
                        "tugamaydi.",
        "per_month": "foydalanuvchi uchun oyiga",
        "plan_free_name": "Starter", "plan_team_name": "Team",
        "plan_biz_name": "Business", "plan_free_price": "0",
        "plan_team_price": "29", "plan_biz_price": "99",
        "plan_free_text": "Shaxsiy loyihalar va birinchi prototip uchun.",
        "plan_team_text": "Har hafta reliz chiqaradigan jamoalar uchun.",
        "plan_biz_text": "Talab va auditlari bo'lgan kompaniyalar uchun.",
        "plan_cta_free": "Boshlash", "plan_cta_paid": "Rejani tanlash",
        "plan_pop": "Ommabop",
        "plan_free_f": ["Yopiq repozitoriylar", "1 bir vaqtli yig'ish",
                        "7 kunlik yig'ish tarixi", "Hamjamiyat yordami"],
        "plan_team_f": ["Bir vaqtda cheksiz yig'ish", "Imzolangan artefaktlar",
                        "Yopiq bog'liqlik oynasi", "90 kunlik yig'ish tarixi",
                        "Yordam bir kun ichida"],
        "plan_biz_f": ["SSO va audit jurnali", "Relizni tasdiqlash",
                       "O'z runnerlari", "Tarixni 2 yilgacha saqlash",
                       "Yordam ikki soat ichida"],
        "included_h": "Barcha rejalarda",
        "included": ["Takrorlanadigan yig'ishlar", "Artefakt xeshi (SHA-256)",
                     "Imzolangan CI vebhuklari", "Har relizda SBOM"],
        "pricing_note_h": "Self-hosted",
        "pricing_note": "Kestrel sizning tarmog'ingizda ham ishga tushadi: "
                        "o'sha quvur, o'z runnerlari va o'z artefakt ombori.",

        "docs_eyebrow": "Hujjatlar", "docs_title": "Tez boshlash",
        "docs_lead": "Bo'sh repozitoriydan imzolangan relizgacha — taxminan o'n "
                     "daqiqa. Quyidagilarning barchasi sizda ochiq turgan "
                     "laboratoriya nusxasida ishlaydi.",
        "docs_nav_qs": "CLI o'rnatish", "docs_nav_pipeline": "Quvur fayli",
        "docs_nav_signing": "Imzo va tekshirish",
        "docs_nav_api": "HTTP API", "docs_nav_console": "Laboratoriya konsoli",
        "docs_qs_title": "1. CLI o'rnating",
        "docs_qs_text": "CLI Kestrel API'siga murojaat qiladi. Manzil "
                        "KESTREL_URL o'zgaruvchisi bilan beriladi: "
                        "to'g'ridan-to'g'ri ishga tushirishda 5000-port, docker "
                        "compose ostida 8021 yoki 8022.",
        "docs_pipe_title": "2. Quvurni ta'riflang",
        "docs_pipe_text": "Bosqichlar tartib bilan ishlaydi, bog'liqlik keshi "
                          "testlardan oldin tiklanadi. Sirlar loyiha sozlamalarida "
                          "saqlanadi, bu faylda emas.",
        "docs_sign_title": "3. Relizni imzolang",
        "docs_sign_text": "Kestrel artefaktning SHA-256 xeshini hisoblaydi va uni "
                          "loyiha kaliti bilan HMAC-SHA256 orqali imzolaydi. "
                          "Joylashtirishdan oldingi tekshiruv — ikki qator.",
        "docs_sign_warn": "Quyidagi kalit — shu nusxaning laboratoriya kaliti. "
                          "Prodakshnda u loyiha sozlamalarida bo'ladi va "
                          "repozitoriyga tushmaydi.",
        "docs_api_title": "HTTP API",
        "docs_api_text": "Konsol va CLI ishlatadigan o'sha endpointlar. Brauzer "
                         "sahifa oladi, curl — JSON.",
        "docs_api_method": "Metod", "docs_api_path": "Endpoint",
        "docs_api_desc": "Nima qiladi",
        "docs_console_title": "Laboratoriya konsoli",
        "docs_console_text": "Barcha endpointlar uchun formalar: tayyor so'rovlar "
                             "va server javoblari bir joyda.",
        "docs_console_btn": "/ui ni ochish",

        "builds_eyebrow": "Ish maydoni", "builds_title": "Yig'ishlar",
        "builds_lead": "Har bir ishga tushishda kommit, davomiylik va yig'ilgan "
                       "artefakt xeshi saqlanadi.",
        "builds_stat_median": "o'rtacha yig'ish", "builds_stat_today": "bugungi ishga tushish",
        "builds_stat_failed": "bugun xato bo'ldi",
        "runs_h": "Oxirgi ishga tushishlar", "builds_branch": "tarmoq",
        "col_no": "Ishga tushish", "col_branch": "Tarmoq", "col_commit": "Kommit",
        "col_status": "Holat", "col_time": "Davomiylik", "col_digest": "Artefakt xeshi",
        "run_ok": "muvaffaqiyatli", "run_failed": "xato", "run_running": "bajarilmoqda",
        "run_queued": "navbatda",
        "release_h": "Relizni e'lon qilish",
        "release_text": "Artefaktni va Kestrel yozib olishi kerak bo'lgan xeshni "
                        "yuboring. Imzo — xeshning loyiha kaliti bilan HMAC'i.",
        "f_name": "Paket", "f_version": "Versiya", "f_digest": "Xesh (SHA-256)",
        "f_signature": "Imzo (HMAC-SHA256)", "f_artifact": "Artefakt mazmuni",
        "f_submit_release": "Relizni e'lon qilish",
        "profile_h": "Profil bo'yicha yig'ish",
        "profile_text": "Profil — ishga tushishning saqlangan parametrlari: kesh "
                        "siyosati, muhit va bosqichlarni almashtirish. base64 "
                        "blob sifatida yuboriladi.",
        "f_submit_profile": "Yig'ishni boshlash",
        "webhook_h": "CI vebhuklari",
        "webhook_text": "Yig'ish tugagach, quvur /webhooks/ci manziliga bitta "
                        "imzolangan POST yuboradi. U bilan relizni prodga "
                        "o'tkazish yoki chatga yozish qulay.",
        "result_h": "Server javobi",
        "result_flag_h": "Laboratoriya flagi",
        "hint_release": "Misoldagi xesh artefakt mazmuniga mos kelmaydi. "
                         "Server u bilan nima qilishini kuzating.",
        "hint_profile": "Bu forma JSON yuboradi. API seriyalangan profilning "
                         "base64 blob'ini ham qabul qiladi.",
        "hint_webhook": "Imzo maydoni bu yerda ixtiyoriy: bo'sh yuborib, "
                         "server nima talab qilishini ko'ring.",
        "webhook_send": "Hodisa yuborish",

        "reg_eyebrow": "Paketlar", "reg_title": "Bog'liqliklar reyestri",
        "reg_lead": "O'z wheel va sdist paketlaringiz ommaviy paketlar yonida "
                    "turadi. Yig'ishlar nomlarni shu reyestr orqali hal qiladi.",
        "reg_internal_h": "Ichki indeks",
        "reg_internal_text": "Jamoangiz tomonidan yig'ilgan va CI dan e'lon qilingan.",
        "reg_public_h": "Ommaviy oyna",
        "reg_public_text": "Uchinchi tomon paketlari, tashqi indeksdan "
                           "o'zgartirilmasdan o'tkaziladi.",
        "col_pkg": "Paket", "col_version": "Versiya", "col_kind": "Format",
        "col_size": "Hajm", "col_sum": "SHA-256", "col_publisher": "Nashriyotchi",
        "kind_wheel": "wheel", "kind_sdist": "sdist",
        "badge_pinned": "qat'iy belgilangan",
        "install_h": "Paketni o'rnatish",
        "install_text": "Yig'ish paytida nomni hal qilish: versiyasiz nom eng "
                        "yangi mavjud versiyani oladi.",
        "f_pkg_name": "Paket nomi", "f_pkg_version": "Versiya (ixtiyoriy)",
        "f_submit_install": "Hal qilish va o'rnatish",
        "reg_hint_h": "Xeshlar nega kerak",
        "reg_hint": "Loyihaning lock fayli har bir bog'liqlikning xeshini "
                    "qat'iy belgilaydi. Usiz hal qilish indeks qaytargan "
                    "narsaga ishonadi.",

        "err_404_t": "Sahifa topilmadi",
        "err_404_m": "Manzilni tekshiring yoki bosh sahifaga qayting.",
        "err_500_t": "Server ichki xatosi",
        "err_500_m": "Nimadir xato ketdi. Keyinroq qayta urinib ko'ring.",
        "go_home": "Bosh sahifaga",

        "vuln": "Zaif versiya", "fixed": "Tuzatilgan versiya",
        "foot_about": "Kichik jamoalar uchun uzluksiz yetkazish: quvurlar, "
                      "imzolangan artefaktlar va o'z bog'liqlik reyestri.",
        "foot_product": "Mahsulot", "foot_dev": "Dasturchilar uchun",
        "foot_console": "Laboratoriya konsoli /ui",
        "foot_deps": "Paket versiyalari /deps",
        "foot_note": "A03 (Software Supply Chain Failures) laboratoriyasi uchun "
                     "o'quv sayti. Faqat lokal ishga tushiring.",
    },
}

# ------------------------------------------------------------ тексты ответов
# Каждый код: ok — считает ли сервер запрос успешным, title/text — по языкам.
RESULT = {
    "release_accepted": {
        "ok": True,
        "title": {"en": "Release published", "ru": "Релиз опубликован",
                  "uz": "Reliz e'lon qilindi"},
        "text": {"en": "The artifact is in the registry under the digest you "
                       "sent.",
                 "ru": "Артефакт лежит в реестре под тем хешем, который вы "
                       "прислали.",
                 "uz": "Artefakt siz yuborgan xesh ostida reyestrda."},
    },
    "release_no_signature": {
        "ok": True,
        "title": {"en": "Release published without a signature",
                  "ru": "Релиз опубликован без подписи",
                  "uz": "Reliz imzosiz e'lon qilindi"},
        "text": {"en": "The digest was taken from the request as is and the "
                       "artifact was never verified: Kestrel recorded what the "
                       "build sent it. Two runs of the same commit can now "
                       "produce two different digests.",
                 "ru": "Хеш взят из запроса как есть, а сам артефакт сервер не "
                       "проверял: Kestrel записал то, что ему прислала сборка. "
                       "Теперь два запуска одного коммита могут дать два разных "
                       "хеша, и никто этого не заметит.",
                 "uz": "Xesh so'rovdan o'zgartirilmasdan olindi, artefakt esa "
                       "tekshirilmadi: Kestrel yig'ish yuborgan narsani yozdi. "
                       "Endi bitta kommitning ikki ishga tushishi ikki xil xesh "
                       "berishi mumkin."},
    },
    "release_unverified": {
        "ok": True,
        "title": {"en": "Release published, signature ignored",
                  "ru": "Релиз опубликован, подпись проигнорирована",
                  "uz": "Reliz e'lon qilindi, imzo e'tiborsiz qoldirildi"},
        "text": {"en": "A signature arrived, but the server never recomputed the "
                       "digest and never compared the value with it. A string in "
                       "this field proves nothing.",
                 "ru": "Подпись пришла, но сервер не пересчитал хеш и не сравнил с "
                       "ним присланное значение. Строка в этом поле ничего не "
                       "доказывает.",
                 "uz": "Imzo keldi, lekin server xeshni qayta hisoblamadi va "
                       "yuborilgan qiymatni u bilan solishtirmadi. Bu maydondagi "
                       "satr hech narsani isbotlamaydi."},
    },
    "release_bad_digest": {
        "ok": False,
        "title": {"en": "Digest mismatch", "ru": "Хеш не совпал",
                  "uz": "Xesh mos kelmadi"},
        "text": {"en": "The SHA-256 of the artifact body does not match the "
                       "digest in the request. The release was rejected.",
                 "ru": "SHA-256 от содержимого артефакта не совпал с хешем в "
                       "запросе. Релиз отклонён.",
                 "uz": "Artefakt mazmunining SHA-256 xeshi so'rovdagi xeshga "
                       "mos kelmadi. Reliz rad etildi."},
    },
    "release_bad_signature": {
        "ok": False,
        "title": {"en": "Signature missing or invalid",
                  "ru": "Подпись отсутствует или неверна",
                  "uz": "Imzo yo'q yoki noto'g'ri"},
        "text": {"en": "The signature is the HMAC-SHA256 of the digest with the "
                       "project key. Without a matching signature the release "
                       "is not published.",
                 "ru": "Подпись — это HMAC-SHA256 от хеша ключом проекта. Без "
                       "совпадающей подписи релиз не публикуется.",
                 "uz": "Imzo — xeshning loyiha kaliti bilan HMAC-SHA256 qiymati. "
                       "Mos imzosiz reliz e'lon qilinmaydi."},
    },
    "build_ok": {
        "ok": True,
        "title": {"en": "Build finished", "ru": "Сборка завершена",
                  "uz": "Yig'ish tugadi"},
        "text": {"en": "The profile was applied: cache policy, environment and "
                       "stage overrides.",
                 "ru": "Профиль применён: политика кэша, окружение и "
                       "переопределения стадий.",
                 "uz": "Profil qo'llanildi: kesh siyosati, muhit va bosqichlar "
                       "almashtirildi."},
    },
    "build_pickle": {
        "ok": True,
        "title": {"en": "Build finished from a serialized profile",
                  "ru": "Сборка выполнена по сериализованному профилю",
                  "uz": "Yig'ish seriyalangan profil bo'yicha bajarildi"},
        "text": {"en": "The server deserialized the blob with pickle before "
                       "reading a single field. A profile is data, not code: "
                       "whatever was inside the object was already executed by "
                       "the time Kestrel looked at it.",
                 "ru": "Сервер десериализовал блоб через pickle ещё до того, как "
                       "прочитал первое поле. Профиль — это данные, а не код: "
                       "что было внутри объекта, уже выполнилось к моменту, "
                       "когда Kestrel на него посмотрел.",
                 "uz": "Server bitta maydonni o'qishdan oldin blobni pickle "
                       "orqali deserializatsiya qildi. Profil — bu kod emas, "
                       "ma'lumot: obyekt ichidagi narsa Kestrel unga qarashidan "
                       "oldin bajarilgan edi."},
    },
    "build_bad_format": {
        "ok": False,
        "title": {"en": "Profile not accepted", "ru": "Профиль не принят",
                  "uz": "Profil qabul qilinmadi"},
        "text": {"en": "A profile must be plain JSON. Serialized objects are "
                       "not read: they can carry code.",
                 "ru": "Профиль должен быть обычным JSON. Сериализованные "
                       "объекты не читаются: они могут нести в себе код.",
                 "uz": "Profil oddiy JSON bo'lishi kerak. Seriyalangan "
                       "obyektlar o'qilmaydi: ular kod olib kelishi mumkin."},
    },
    "webhook_accepted": {
        "ok": True,
        "title": {"en": "Build promoted to production",
                  "ru": "Сборка переведена в продакшен",
                  "uz": "Yig'ish prodakshnga o'tkazildi"},
        "text": {"en": "The webhook asked to promote the build and the server "
                       "did it without checking where the request came from. "
                       "Any client that knows the URL can release to production.",
                 "ru": "Вебхук попросил перевести сборку в прод, и сервер это "
                       "сделал, не проверив, откуда пришёл запрос. Любой, кто "
                       "знает адрес, может выпустить релиз в продакшен.",
                 "uz": "Vebhuk yig'ishni prodga o'tkazishni so'radi va server "
                       "so'rov qayerdan kelganini tekshirmasdan bajarildi. "
                       "Manzilni bilgan har kim prodga reliz chiqara oladi."},
    },
    "webhook_verified": {
        "ok": True,
        "title": {"en": "Signature verified", "ru": "Подпись проверена",
                  "uz": "Imzo tekshirildi"},
        "text": {"en": "The HMAC of the request body matched the header, so the "
                       "build was promoted.",
                 "ru": "HMAC тела запроса совпал с заголовком, поэтому сборка "
                       "переведена в прод.",
                 "uz": "So'rov tanasining HMAC'i sarlavhaga mos keldi, shuning "
                       "uchun yig'ish prodga o'tkazildi."},
    },
    "webhook_rejected": {
        "ok": False,
        "title": {"en": "Signature required", "ru": "Нужна подпись",
                  "uz": "Imzo talab qilinadi"},
        "text": {"en": "The X-Kestrel-Signature header is missing or does not "
                       "match the body. The build was not promoted.",
                 "ru": "Заголовок X-Kestrel-Signature отсутствует или не "
                       "совпадает с телом запроса. Сборка не переведена в прод.",
                 "uz": "X-Kestrel-Signature sarlavhasi yo'q yoki so'rov "
                       "tanasiga mos kelmadi. Yig'ish prodga o'tkazilmadi."},
    },
    "install_internal": {
        "ok": True,
        "title": {"en": "Package installed from the internal index",
                  "ru": "Пакет установлен из внутреннего индекса",
                  "uz": "Paket ichki indeksdan o'rnatildi"},
        "text": {"en": "The version and the digest come from your own index.",
                 "ru": "Версия и хеш — из вашего собственного индекса.",
                 "uz": "Versiya va xesh — o'z indeksingizdan."},
    },
    "install_confusion": {
        "ok": True,
        "title": {"en": "Package resolved from the public mirror",
                  "ru": "Пакет разрешён через публичное зеркало",
                  "uz": "Paket ommaviy oyna orqali hal qilindi"},
        "text": {"en": "The build took the newest version of the name without "
                       "asking which index it came from and without comparing "
                       "the digest. A public package with the same name "
                       "outranked your own one.",
                 "ru": "Сборка взяла самую новую версию имени, не спросив, из "
                       "какого индекса она пришла, и не сверив хеш. Публичный "
                       "пакет с тем же именем оказался «новее» вашего.",
                 "uz": "Yig'ish nomning eng yangi versiyasini, qaysi indeksdan "
                       "kelganini so'ramasdan va xeshni solishtirmasdan oldi. "
                       "Xuddi shu nomdagi ommaviy paket siznikidan «yangi» "
                       "bo'lib chiqdi."},
    },
    "install_unknown": {
        "ok": False,
        "title": {"en": "Package not found", "ru": "Пакет не найден",
                  "uz": "Paket topilmadi"},
        "text": {"en": "There is no package with that name in any index this "
                       "instance knows about.",
                 "ru": "Пакета с таким именем нет ни в одном индексе, который "
                       "знает этот экземпляр.",
                 "uz": "Bu nusxa bilgan hech bir indeksda bunday nomdagi paket "
                       "yo'q."},
    },
    "install_public_blocked": {
        "ok": False,
        "title": {"en": "Public index refused", "ru": "Публичный индекс отклонён",
                  "uz": "Ommaviy indeks rad etildi"},
        "text": {"en": "The name exists only in the public mirror, and a build "
                       "is not allowed to reach the external index.",
                 "ru": "Имя есть только в публичном зеркале, а сборке запрещено "
                       "ходить во внешний индекс.",
                 "uz": "Nom faqat ommaviy oynada bor, yig'ishga esa tashqi "
                       "indeksga murojaat qilish taqiqlangan."},
    },
    "install_unpinned": {
        "ok": False,
        "title": {"en": "Version not pinned", "ru": "Версия не закреплена",
                  "uz": "Versiya qat'iy belgilanmagan"},
        "text": {"en": "The request came without a version. The lock file pins "
                       "an exact version and digest for every dependency, so the "
                       "build refuses to guess.",
                 "ru": "Запрос пришёл без версии. Lock-файл закрепляет точную "
                       "версию и хеш каждой зависимости, поэтому сборка "
                       "отказывается угадывать.",
                 "uz": "So'rov versiyasiz keldi. Lock fayli har bir "
                       "bog'liqlikning aniq versiyasi va xeshini qat'iy "
                       "belgilaydi, shuning uchun yig'ish taxmin qilishdan bosh "
                       "tortadi."},
    },
    "install_hash_mismatch": {
        "ok": False,
        "title": {"en": "Hash mismatch", "ru": "Хеш не совпал",
                  "uz": "Xesh mos kelmadi"},
        "text": {"en": "The digest of the package does not match the one pinned "
                       "in the lock file. The install was stopped.",
                 "ru": "Хеш пакета не совпал с закреплённым в lock-файле. "
                       "Установка остановлена.",
                 "uz": "Paket xeshi lock faylida qat'iy belgilangan xeshga mos "
                       "kelmadi. O'rnatish to'xtatildi."},
    },
}

# ------------------------------------------------------------------ контент
FEATURES = [
    dict(icon="flow",
         title={"en": "Pipeline as code", "ru": "Пайплайн как код",
                "uz": "Quvur kod sifatida"},
         text={"en": "Stages, cache rules and secrets live in kestrel.yml next "
                     "to the code they build.",
               "ru": "Стадии, правила кэша и секреты — в kestrel.yml рядом с "
                     "кодом, который они собирают.",
               "uz": "Bosqichlar, kesh qoidalari va sirlar kestrel.yml ichida, "
                     "yig'iladigan kod yonida."}),
    dict(icon="shield",
         title={"en": "Signed artifacts", "ru": "Подписанные артефакты",
                "uz": "Imzolangan artefaktlar"},
         text={"en": "Every build gets a SHA-256 digest and an HMAC signature "
                     "you can verify before deploying.",
               "ru": "Каждая сборка получает SHA-256 и HMAC-подпись, которую "
                     "можно проверить до деплоя.",
               "uz": "Har bir yig'ish SHA-256 xesh va joylashtirishdan oldin "
                     "tekshiriladigan HMAC imzo oladi."}),
    dict(icon="box",
         title={"en": "Dependency cache", "ru": "Кэш зависимостей",
                "uz": "Bog'liqlik keshi"},
         text={"en": "A private mirror of your internal index. Names resolve "
                     "from it first, hashes come from the lock file.",
               "ru": "Приватное зеркало вашего внутреннего индекса. Имена "
                     "разрешаются через него первым, хеши берутся из lock-файла.",
               "uz": "Ichki indeksingizning yopiq oynasi. Nomlar avval undan "
                     "hal qilinadi, xeshlar lock faylidan olinadi."}),
    dict(icon="bolt",
         title={"en": "Webhooks that keep up", "ru": "Вебхуки без потерь",
                "uz": "Yo'qolmaydigan vebhuklar"},
         text={"en": "CI events are signed, delivered in order and retried for "
                     "up to six hours.",
               "ru": "События CI подписаны, доставляются по порядку и "
                     "повторяются в течение шести часов.",
               "uz": "CI hodisalari imzolangan, tartib bilan yetkaziladi va olti "
                     "soat davomida qayta uriniladi."}),
]

STEPS = [
    dict(no="1",
         title={"en": "Connect the repository", "ru": "Подключите репозиторий",
                "uz": "Repozitoriyni ulang"},
         text={"en": "Read-only access to the code and permission to write to "
                     "the registry. The first build starts on the next push.",
               "ru": "Доступ на чтение кода и право писать в реестр. Первая "
                     "сборка стартует на следующем пуше.",
               "uz": "Kodga faqat o'qish huquqi va reyestrga yozish ruxsati. "
                     "Birinchi yig'ish keyingi pushda boshlanadi."}),
    dict(no="2",
         title={"en": "Describe the stages", "ru": "Опишите стадии",
                "uz": "Bosqichlarni ta'riflang"},
         text={"en": "Tests, build, sign, push. Stages run in order, and any of "
                     "them can be skipped for a branch.",
               "ru": "Тесты, сборка, подпись, отправка. Стадии идут по порядку, "
                     "любую из них можно отключить для ветки.",
               "uz": "Testlar, yig'ish, imzo, yuborish. Bosqichlar tartib bilan "
                     "ishlaydi, istalganini tarmoq uchun o'chirish mumkin."}),
    dict(no="3",
         title={"en": "Release and verify", "ru": "Релиз и проверка",
                "uz": "Reliz va tekshiruv"},
         text={"en": "kestrel release writes the artifact and its digest. The "
                     "deploy side verifies the signature before rolling out.",
               "ru": "kestrel release записывает артефакт и его хеш. Сторона "
                     "деплоя проверяет подпись перед выкаткой.",
               "uz": "kestrel release artefakt va uning xeshini yozadi. "
                     "Joylashtirish tomoni chiqarishdan oldin imzoni tekshiradi."}),
]

STATS = [
    dict(value="3 min", key="stat_build"),
    dict(value="1 240", key="stat_teams"),
    dict(value="99,95 %", key="stat_uptime"),
    dict(value="38", key="stat_reviews"),
]

# Строки «терминала» в hero-блоке: ключ подписи + время.
TERMINAL = [("term_deps", "1.2 s"), ("term_tests", "38 s"),
            ("term_build", "54 s"), ("term_sign", "0.4 s"),
            ("term_push", "2.1 s")]

PLANS = [
    dict(key="free", name="plan_free_name", price="plan_free_price",
         text="plan_free_text", cta="plan_cta_free", highlight=False,
         list_key="plan_free_f"),
    dict(key="team", name="plan_team_name", price="plan_team_price",
         text="plan_team_text", cta="plan_cta_paid", highlight=True,
         list_key="plan_team_f"),
    dict(key="biz", name="plan_biz_name", price="plan_biz_price",
         text="plan_biz_text", cta="plan_cta_paid", highlight=False,
         list_key="plan_biz_f"),
]

# Код в документации: одинаков для всех языков.
SNIPPETS = {
    "install": "$ pip install kestrel-cli\n"
               "$ export KESTREL_URL=http://127.0.0.1:5000\n"
               "$ kestrel login --token $KESTREL_TOKEN",
    "pipeline": "# kestrel.yml\n"
                "stages:\n"
                "  - name: deps\n"
                "    cache: pip\n"
                "  - name: test\n"
                "    run: pytest -q\n"
                "  - name: build\n"
                "    run: python -m build\n"
                "  - name: sign\n"
                "    uses: kestrel/sign@v2",
    "sign": ("import hashlib, hmac, requests\n\n"
             "KEY = 'kestrel-lab-project-key'\n"
             "URL = 'http://127.0.0.1:5000'\n\n"
             "body = open('dist/app-2.14.0.tar.gz', 'rb').read()\n"
             "digest = hashlib.sha256(body).hexdigest()\n"
             "signature = hmac.new(KEY.encode(), digest.encode(), 'sha256')\n\n"
             "payload = {'name': 'app', 'version': '2.14.0',\n"
             "           'digest': digest, 'signature': signature.hexdigest()}\n"
             "requests.post(URL + '/api/releases', json=payload)"),
    "webhook": "curl -X POST $KESTREL_URL/webhooks/ci \\\n"
               "  -H 'Content-Type: application/json' \\\n"
               "  -H 'X-Kestrel-Signature: sha256=<hmac of the body>' \\\n"
               "  -d '{\"event\":\"release.approve\",\"build\":\"#4821\","
               "\"env\":\"production\"}'",
}

ENDPOINTS = [
    dict(method="GET", path="/builds",
         desc={"en": "Runs, durations and artifact digests",
               "ru": "Запуски, длительности и хеши артефактов",
               "uz": "Ishga tushishlar, davomiylik va artefakt xeshlari"}),
    dict(method="GET", path="/registry",
         desc={"en": "Internal packages and the public mirror",
               "ru": "Внутренние пакеты и публичное зеркало",
               "uz": "Ichki paketlar va ommaviy oyna"}),
    dict(method="POST", path="/api/releases",
         desc={"en": "Publish an artifact with its digest and signature",
               "ru": "Опубликовать артефакт с хешем и подписью",
               "uz": "Artefaktni xesh va imzo bilan e'lon qilish"}),
    dict(method="POST", path="/api/builds/run",
         desc={"en": "Run a build from a profile blob",
               "ru": "Запустить сборку по блобу профиля",
               "uz": "Profil blob'i bo'yicha yig'ishni boshlash"}),
    dict(method="POST", path="/webhooks/ci",
         desc={"en": "CI event, signed with the project key",
               "ru": "Событие CI, подписанное ключом проекта",
               "uz": "Loyiha kaliti bilan imzolangan CI hodisasi"}),
    dict(method="POST", path="/api/registry/install",
         desc={"en": "Resolve a name and install the package",
               "ru": "Разрешить имя и установить пакет",
               "uz": "Nomni hal qilish va paketni o'rnatish"}),
    dict(method="GET", path="/deps",
         desc={"en": "Versions of the packages installed in this instance",
               "ru": "Версии пакетов, установленных в этом экземпляре",
               "uz": "Shu nusxada o'rnatilgan paketlar versiyalari"}),
]

# Запуски сборок (вымышленные данные для лабы).
RUNS = [
    dict(no="#4824", branch="main", commit="9f2c1ad", state="run_ok",
         time="1 min 42 s", digest="9f2c1ad4e7b8…a41d"),
    dict(no="#4823", branch="release/2.14", commit="c04e77b", state="run_ok",
         time="1 min 51 s", digest="c04e77b2ff90…7e13"),
    dict(no="#4822", branch="main", commit="41b9e05", state="run_failed",
         time="22 s", digest="—"),
    dict(no="#4821", branch="feature/signing", commit="77d1c40", state="run_running",
         time="48 s", digest="—"),
    dict(no="#4820", branch="main", commit="a6f3d92", state="run_ok",
         time="1 min 38 s", digest="a6f3d9210c4b…55aa"),
    dict(no="#4819", branch="chore/ci-cache", commit="2e5b813", state="run_queued",
         time="—", digest="—"),
]

BUILD_STATS = {"median": "1 min 44 s", "today": "26", "failed": "2"}

# Внутренний индекс: то, что команда собрала сама.
PACKAGES = [
    dict(name="kestrel-utils", version="1.4.2", kind="kind_sdist",
         size="86 KB", digest="a41d0f7c2b91…c8e2", downloads="1 208",
         pinned=True),
    dict(name="kestrel-report", version="0.9.7", kind="kind_wheel",
         size="412 KB", digest="5e1f9c33ab70…19d4", downloads="744",
         pinned=True),
    dict(name="acme-billing", version="2.3.0", kind="kind_wheel",
         size="1.1 MB", digest="77b0aa51cd32…e610", downloads="2 931",
         pinned=True),
    dict(name="acme-auth", version="1.8.1", kind="kind_sdist",
         size="204 KB", digest="0c93dbe4701f…3a77", downloads="1 566",
         pinned=True),
]

# Публичное зеркало (вымышленный внешний индекс).
PUBLIC_MIRROR = [
    dict(name="kestrel-utils", version="9.9.9", kind="kind_wheel",
         size="1.8 MB", digest="b17ce412ff09…0d55", downloads="14 302",
         publisher="kestrel-utils (unofficial)"),
    dict(name="kestrel-utils", version="1.4.2", kind="kind_wheel",
         size="1.7 MB", digest="e0a7c19b3d54…aa12", downloads="2 044",
         publisher="kestrel-utils (unofficial)"),
    dict(name="requests", version="2.33.0", kind="kind_wheel",
         size="64 KB", digest="64261c2b4a3f…9bd1", downloads="8 912 400",
         publisher="requests maintainers"),
    dict(name="urllib3", version="2.5.0", kind="kind_wheel",
         size="129 KB", digest="f1d2c4b7aa6e…2c08", downloads="7 401 220",
         publisher="urllib3 maintainers"),
    dict(name="pytest", version="8.4.2", kind="kind_wheel",
         size="341 KB", digest="3ba7f0d91c55…7ee2", downloads="5 188 733",
         publisher="pytest maintainers"),
]

# Хеши, которые отдаёт внутренний индекс.
INDEX_DIGESTS = {
    ("kestrel-utils", "1.4.2"): "a41d0f7c2b91c8e2",
    ("kestrel-report", "0.9.7"): "5e1f9c33ab7019d4",
    ("acme-billing", "2.3.0"): "77b0aa51cd32e610",
    ("acme-auth", "1.8.1"): "0c93dbe4701f3a77",
}

# Хеши, закреплённые в lock-файле проекта. У acme-auth 1.8.1 хеш в лабе
# специально не совпадает с индексом: так видно, что проверка работает.
LOCKED_DIGESTS = {
    ("kestrel-utils", "1.4.2"): "a41d0f7c2b91c8e2",
    ("kestrel-report", "0.9.7"): "5e1f9c33ab7019d4",
    ("acme-billing", "2.3.0"): "77b0aa51cd32e610",
    ("acme-auth", "1.8.1"): "0c93dbe4701f3a99",
}


def _version_key(value):
    """Версия как кортеж чисел: «1.4.2» → (1, 4, 2)."""
    parts = []
    for chunk in str(value).split("."):
        parts.append(int(chunk) if chunk.isdigit() else 0)
    return tuple(parts)


# ------------------------------------------------------- выбор языка и данные

def register_lang(app):
    """Определяет язык запроса и запоминает выбор в cookie.

    Вызывается в начале app.py — ДО хука, который отдаёт главную страницу,
    и до register_ui: иначе g.lang не будет готово.
    """

    @app.before_request
    def _resolve_lang():
        wanted = request.args.get("lang")
        if wanted not in LANGS:
            wanted = request.cookies.get(LANG_COOKIE)
        if wanted not in LANGS:
            # Accept-Language: берём первый тег и его основную часть (ru, uz)
            accepted = [str(code).lower() for code, _ in request.accept_languages]
            wanted = accepted[0][:2] if accepted else ""
        g.lang = wanted if wanted in LANGS else DEFAULT_LANG

    @app.after_request
    def _remember_lang(resp):
        if request.args.get("lang") in LANGS:
            resp.set_cookie(LANG_COOKIE, request.args["lang"], samesite="Lax")
        return resp


def lang():
    return getattr(g, "lang", DEFAULT_LANG)


def t(lang_code=None):
    """Плоский словарь переводов для страницы."""
    return T[lang_code or lang()]


def _tr(field, lang_code):
    return field[lang_code]


def _labels(items, code, *fields):
    """Список словарей с подставленными переводами выбранных полей."""
    out = []
    for item in items:
        row = dict(item)
        for field in fields:
            row[field] = _tr(item[field], code)
        out.append(row)
    return out


def make_result(code, flag=None):
    """Ответ сервера для страниц сборок и реестра."""
    item = RESULT[code]
    code_lang = lang()
    return {"ok": item["ok"], "title": item["title"][code_lang],
            "text": item["text"][code_lang], "flag": flag}


def home_data():
    code = lang()
    tt = t(code)
    return {
        "features": _labels(FEATURES, code, "title", "text"),
        "steps": _labels(STEPS, code, "title", "text"),
        "stats": [dict(value=s["value"], label=tt[s["key"]]) for s in STATS],
        "terminal": [dict(text=tt[key], time=when) for key, when in TERMINAL],
    }


def pricing_data():
    tt = t()
    plans = [dict(name=tt[p["name"]], price=tt[p["price"]], text=tt[p["text"]],
                  cta=tt[p["cta"]], features=tt[p["list_key"]],
                  highlight=p["highlight"], period=tt["per_month"])
             for p in PLANS]
    included = dict(title=tt["included_h"], features=tt["included"],
                    note_title=tt["pricing_note_h"], note=tt["pricing_note"])
    return {"plans": plans, "included": included}


def docs_data():
    code = lang()
    tt = t(code)
    sections = [("qs", tt["docs_nav_qs"]),
                ("pipeline", tt["docs_nav_pipeline"]),
                ("signing", tt["docs_nav_signing"]),
                ("api", tt["docs_nav_api"]),
                ("console", tt["docs_nav_console"])]
    return {"code": SNIPPETS, "sections": sections,
            "endpoints": _labels(ENDPOINTS, code, "desc"),
            "project_key": PROJECT_KEY}


def builds_data(result=None):
    code = lang()
    tt = t(code)
    runs = [dict(run, status=tt[run["state"]],
                 state=run["state"].replace("run_", "")) for run in RUNS]
    stats = [dict(label=tt["builds_stat_median"], value=BUILD_STATS["median"]),
             dict(label=tt["builds_stat_today"], value=BUILD_STATS["today"]),
             dict(label=tt["builds_stat_failed"], value=BUILD_STATS["failed"])]
    return {"runs": runs, "stats": stats,
            "webhook": SNIPPETS["webhook"], "result": result,
            "endpoints": _labels(ENDPOINTS, code, "desc")}


def registry_data(result=None):
    tt = t()

    def rows(items):
        return [dict(pkg, kind=tt[pkg["kind"]]) for pkg in items]

    return {"internal": rows(PACKAGES), "public": rows(PUBLIC_MIRROR),
            "result": result}


def pick_newest(name, version=None):
    """Разрешение имени по обоим индексам сразу — так работает vulnerable.

    Указанная версия соблюдается, но индекс не проверяется: если во
    внутреннем и публичном индексах есть пакет с одним и тем же именем и
    номером версии, побеждает публичный. Именно так и выглядит подмена
    внутреннего пакета публичным при extra-index-url.
    """
    found = None
    for source, items in (("internal", PACKAGES), ("public", PUBLIC_MIRROR)):
        for item in items:
            if item["name"] != name:
                continue
            if version and item["version"] != version:
                continue
            candidate = dict(item, source=source)
            if found is None or (
                    _version_key(candidate["version"]) >=
                    _version_key(found["version"])):
                found = candidate
    return found


def find_internal(name, version=None):
    """Пакет из внутреннего индекса: имя плюс, если задана, версия."""
    for item in PACKAGES:
        if item["name"] == name and (version in (None, "", item["version"])):
            return dict(item, source="internal")
    return None
