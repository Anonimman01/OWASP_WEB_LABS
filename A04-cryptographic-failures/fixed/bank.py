"""Сайт ATLAS Bank — переводы, данные страниц и помощники.

Файл одинаковый в vulnerable/ и fixed/ (побайтно), как portal.py в A01 и
cafe.py в A02: содержимое сайта от версии не зависит, все отличия — в app.py.

Язык интерфейса: EN / RU / UZ. Выбор хранится в cookie `site_lang`
и задаётся ссылкой `?lang=xx` (переключатель в шапке сайта).
"""
from flask import g, request

LANGS = ["en", "ru", "uz"]
DEFAULT_LANG = "en"
LANG_COOKIE = "site_lang"

BRAND = {"name": "ATLAS", "sub": "BANK"}

# ------------------------------------------------------------------ переводы
T = {
    "en": {
        "nav_accounts": "Accounts", "nav_cards": "Cards", "nav_rates": "Rates",
        "nav_security": "Security", "nav_support": "Support",
        "nav_label": "Main navigation", "lang_label": "Language",
        "signin": "Sign in", "open_acct": "Open an account",

        "hero_eyebrow": "Licensed bank · deposits protected",
        "hero_l1": "Everyday banking,",
        "hero_l2": "done properly",
        "hero_text": "Accounts, cards and savings in one place: clear rates, "
                     "no hidden fees and transfers that arrive in seconds.",
        "hero_cta1": "Open an account", "hero_cta2": "Sign in",
        "hero_mock_label": "Total balance", "hero_mock_name": "Everyday account",
        "hero_mock_row1": "Savings transfer", "hero_mock_row2": "Coffee House",
        "hero_mock_row3": "Cashback",
        "stat1_v": "0.00", "stat1_l": "monthly account fee",
        "stat2_v": "4.5%", "stat2_l": "on savings, per year",
        "stat3_v": "12 sec", "stat3_l": "average transfer time",

        "prod_eyebrow": "Products", "prod_title": "Three things, done well",
        "p1_t": "Everyday account",
        "p1_d": "Free checking with a card, instant transfers between your "
                "own accounts and 1% cashback on purchases.",
        "p1_f1": "No monthly fee", "p1_f2": "1% cashback",
        "p1_f3": "Free ATM network",
        "p2_t": "Savings",
        "p2_d": "Interest on every cent, paid monthly. Withdraw whenever you "
                "want — the rate does not fall.",
        "p2_f1": "4.5% a year", "p2_f2": "Interest paid monthly",
        "p2_f3": "Withdraw any time",
        "p3_t": "Cards",
        "p3_d": "A virtual card in a minute, a plastic one by post. "
                "Contactless and ready for mobile wallets.",
        "p3_f1": "Issued instantly", "p3_f2": "Contactless",
        "p3_f3": "3-D Secure",

        "rates_eyebrow": "Rates", "rates_title": "Today's rates",
        "rates_lead": "Demonstration rates for the laboratory. Updated every "
                      "business day at 09:00.",
        "r_h_pair": "Currency", "r_h_buy": "Buy", "r_h_sell": "Sell",
        "r_eur": "EUR", "r_gbp": "GBP", "r_chf": "CHF",
        "r_eur_b": "1.0842", "r_eur_s": "1.0855",
        "r_gbp_b": "1.2690", "r_gbp_s": "1.2704",
        "r_chf_b": "1.1275", "r_chf_s": "1.1290",
        "dep_h": "Deposits", "dep_1": "On demand", "dep_1_v": "1.0%",
        "dep_2": "Savings", "dep_2_v": "4.5%", "dep_3": "12 months",
        "dep_3_v": "5.2%",

        "steps_eyebrow": "How it works",
        "steps_title": "An account in three steps",
        "s1_t": "Sign up",
        "s1_d": "A name, a username and a password — that is all we ask for "
                "on this site.",
        "s2_t": "Confirm",
        "s2_d": "Identity check takes a couple of minutes in the mobile app.",
        "s3_t": "Use it",
        "s3_d": "The card, transfers and savings start working right away.",

        "sec_eyebrow": "Security", "sec_title": "Access to your money is guarded",
        "sec_p": "Sign-in alerts, transaction notifications, round-the-clock "
                 "fraud monitoring and instant card blocking from the app.",
        "sec_1": "Login alerts", "sec_2": "Instant card freeze",
        "sec_3": "24/7 fraud monitor",

        "foot_about": "ATLAS Bank is a training site for lab A04 "
                      "(Cryptographic Failures). All data is fictional.",
        "foot_products": "Products", "foot_company": "Company",
        "foot_support": "Support", "foot_explore": "Explore",
        "foot_rates": "Rates", "foot_security": "Security",
        "foot_help": "Help centre", "foot_contact": "Contact us",
        "foot_console": "Lab console /ui",
        "foot_note": "Training lab A04. Run it locally only.",
        "foot_legal": "ATLAS Bank · demo license #A04-2026 · accounts, cards "
                      "and rates on this site are fictional.",

        "login_t": "Sign in", "login_sub": "Access your accounts and cards.",
        "login_mock": "Your money stays where you left it.",
        "reg_sub": "An account in a couple of minutes: a name, a username "
                   "and a password.",
        "forgot_sub": "Enter your username and we will send a reset link to "
                      "it.",
        "reset_sub": "Choose a new password. The old one stops working.",
        "f_user": "Username", "f_pass": "Password", "f_full": "Full name",
        "f_pass2": "Repeat password", "f_from": "From", "f_to": "To",
        "f_amount": "Amount", "f_note": "Note (optional)",
        "f_number": "Card number", "f_exp": "Expiry (MM/YY)",
        "f_holder": "Cardholder",
        "btn_signin": "Sign in", "btn_register": "Create account",
        "btn_send_link": "Send the link", "btn_save_pass": "Save password",
        "btn_transfer": "Send transfer", "btn_add_card": "Add card",
        "btn_back": "Back",
        "forgot_link": "Forgot your password?", "no_acct": "No account yet?",
        "open_link": "Open an account", "have_acct": "Already registered?",
        "sign_in_link": "Sign in", "back_login": "Back to sign in",
        "pass_hint": "At least 8 characters.",

        "err_cred": "Incorrect username or password.",
        "err_exists": "That username is already taken.",
        "err_pass": "The passwords do not match.",
        "err_pass_len": "The password must be at least 8 characters.",
        "err_input": "Check the fields and try again.",
        "err_token": "This reset link is invalid or has expired.",
        "err_card": "Enter a card number of 13 to 19 digits.",
        "err_exp": "The expiry date must look like 09/29.",
        "err_funds": "Not enough funds on the source account.",
        "err_same": "Choose two different accounts.",
        "err_amount": "Enter an amount greater than zero.",
        "err_own": "Choose one of your own accounts.",
        "err_admin": "Administrator access required.",
        "err_auth": "Sign in to continue.",
        "ok_registered": "Account created. Sign in to continue.",
        "ok_reset": "Password changed. Sign in with the new one.",
        "ok_sent": "If that username exists, a reset link has been sent.",
        "ok_transfer": "Transfer completed.",
        "ok_card": "Card added.",
        "lab_mail": "Lab note: outgoing letters are shown at /_lab/outbox.",

        "dash_t": "Overview", "welcome": "Welcome back",
        "total_label": "Total balance across accounts",
        "accounts_h": "Your accounts", "txns_h": "Recent activity",
        "quick_h": "Quick actions", "qa_transfer": "Make a transfer",
        "qa_cards": "Manage cards", "empty_txns": "No transactions yet.",
        "col_date": "Date", "col_desc": "Description", "col_account": "Account",
        "col_amount": "Amount", "acc_everyday": "Everyday",
        "acc_savings": "Savings", "acc_new": "Everyday account",
        "more": "All transfers", "acct_no": "Account",
        "empty_cards": "No cards yet — add the first one below.",

        "cards_t": "Cards", "cards_sub": "Cards linked to your accounts.",
        "add_h": "Add a card", "expires": "Expires", "holder": "Cardholder",
        "status_active": "Active",
        "note_lost": "Lost or stolen? Block the card in the app or call "
                     "+1 800 555 0100.",

        "tr_t": "Transfers", "tr_sub": "Move money between your own accounts.",
        "history_h": "Transfer history",

        "admin_t": "Administration", "admin_sub": "Employees and customers of "
                                                  "the bank.",
        "users_h": "Users", "col_username": "Username", "col_name": "Name",
        "col_role": "Role", "col_accounts": "Accounts",
        "col_balance": "Balance", "role_admin": "admin",
        "role_customer": "customer", "flag_h": "Laboratory flag",
        "flag_p": "You are signed in as an administrator. This is what the "
                  "lab is about:",

        "err_404_t": "Page Not Found",
        "err_404_m": "Check the address or go back to the home page.",
        "err_403_t": "Access Denied",
        "err_403_m": "This page is only available to bank administrators.",
        "err_500_t": "Internal Server Error",
        "err_500_m": "Something went wrong. Please try again later.",
        "go_home": "Go to the homepage",

        "side_overview": "Overview", "side_cards": "Cards",
        "side_transfers": "Transfers", "side_admin": "Administration",
        "sign_out": "Sign out", "app_lang": "Language",
        "vuln": "Vulnerable version", "fixed": "Fixed version",
    },
    "ru": {
        "nav_accounts": "Счета", "nav_cards": "Карты", "nav_rates": "Курсы",
        "nav_security": "Безопасность", "nav_support": "Поддержка",
        "nav_label": "Главное меню", "lang_label": "Язык",
        "signin": "Войти", "open_acct": "Открыть счёт",

        "hero_eyebrow": "Лицензированный банк · вклады защищены",
        "hero_l1": "Банковские услуги —",
        "hero_l2": "без лишнего",
        "hero_text": "Счета, карты и накопления в одном месте: понятные "
                     "ставки, без скрытых комиссий и переводы, которые "
                     "доходят за секунды.",
        "hero_cta1": "Открыть счёт", "hero_cta2": "Войти",
        "hero_mock_label": "Общий баланс", "hero_mock_name": "Текущий счёт",
        "hero_mock_row1": "Перевод на накопительный",
        "hero_mock_row2": "Кофейня", "hero_mock_row3": "Кэшбэк",
        "stat1_v": "0.00", "stat1_l": "обслуживание счёта в месяц",
        "stat2_v": "4,5%", "stat2_l": "на накопления, в год",
        "stat3_v": "12 сек", "stat3_l": "средний перевод",

        "prod_eyebrow": "Продукты", "prod_title": "Три вещи, сделанные хорошо",
        "p1_t": "Текущий счёт",
        "p1_d": "Бесплатное обслуживание с картой, мгновенные переводы между "
                "своими счетами и 1% кэшбэка с покупок.",
        "p1_f1": "Без платы за месяц", "p1_f2": "1% кэшбэк",
        "p1_f3": "Бесплатные банкоматы",
        "p2_t": "Накопления",
        "p2_d": "Проценты на каждую копейку, начисляются ежемесячно. "
                "Снимайте когда угодно — ставка не падает.",
        "p2_f1": "4,5% годовых", "p2_f2": "Начисления каждый месяц",
        "p2_f3": "Снятие в любое время",
        "p3_t": "Карты",
        "p3_d": "Виртуальная карта за минуту, пластиковая — по почте. "
                "Бесконтактная и готова к мобильным кошелькам.",
        "p3_f1": "Выпуск сразу", "p3_f2": "Бесконтактная оплата",
        "p3_f3": "3-D Secure",

        "rates_eyebrow": "Курсы", "rates_title": "Курсы на сегодня",
        "rates_lead": "Демонстрационные курсы для лаборатории. Обновление "
                      "каждый рабочий день в 09:00.",
        "r_h_pair": "Валюта", "r_h_buy": "Покупка", "r_h_sell": "Продажа",
        "r_eur": "EUR", "r_gbp": "GBP", "r_chf": "CHF",
        "r_eur_b": "1,0842", "r_eur_s": "1,0855",
        "r_gbp_b": "1,2690", "r_gbp_s": "1,2704",
        "r_chf_b": "1,1275", "r_chf_s": "1,1290",
        "dep_h": "Вклады", "dep_1": "Сберегательный", "dep_1_v": "1,0%",
        "dep_2": "Накопительный", "dep_2_v": "4,5%", "dep_3": "На 12 месяцев",
        "dep_3_v": "5,2%",

        "steps_eyebrow": "Как это работает",
        "steps_title": "Счёт за три шага",
        "s1_t": "Регистрация",
        "s1_d": "Имя, имя пользователя и пароль — больше на этом сайте "
                "ничего не требуется.",
        "s2_t": "Подтверждение",
        "s2_d": "Проверка занимает пару минут в мобильном приложении.",
        "s3_t": "Пользуйтесь",
        "s3_d": "Карта, переводы и накопления начинают работать сразу.",

        "sec_eyebrow": "Безопасность",
        "sec_title": "Доступ к вашим деньгам под контролем",
        "sec_p": "Уведомления о входе и операциях, круглосуточный мониторинг "
                 "мошенничества и мгновенная блокировка карты в приложении.",
        "sec_1": "Оповещения о входе", "sec_2": "Мгновенная блокировка",
        "sec_3": "Мониторинг 24/7",

        "foot_about": "ATLAS Bank — учебный сайт лаборатории A04 "
                      "(криптографические сбои). Все данные вымышленные.",
        "foot_products": "Продукты", "foot_company": "Банк",
        "foot_support": "Поддержка", "foot_explore": "Разделы",
        "foot_rates": "Курсы", "foot_security": "Безопасность",
        "foot_help": "Центр помощи", "foot_contact": "Связаться с нами",
        "foot_console": "Консоль лабы /ui",
        "foot_note": "Учебная лаборатория A04. Запускайте только локально.",
        "foot_legal": "ATLAS Bank · демо-лицензия № A04-2026 · счета, карты "
                      "и курсы на сайте вымышленные.",

        "login_t": "Вход", "login_sub": "Доступ к счетам и картам.",
        "login_mock": "Ваши деньги остались там, где вы их оставили.",
        "reg_sub": "Счёт за пару минут: имя, имя пользователя и пароль.",
        "forgot_sub": "Введите имя пользователя — мы отправим ему ссылку для "
                      "сброса.",
        "reset_sub": "Придумайте новый пароль. Старый перестанет работать.",
        "f_user": "Имя пользователя", "f_pass": "Пароль",
        "f_full": "Имя и фамилия", "f_pass2": "Повторите пароль",
        "f_from": "С какого счёта", "f_to": "На какой счёт",
        "f_amount": "Сумма", "f_note": "Комментарий (необязательно)",
        "f_number": "Номер карты", "f_exp": "Срок действия (ММ/ГГ)",
        "f_holder": "Держатель карты",
        "btn_signin": "Войти", "btn_register": "Создать счёт",
        "btn_send_link": "Отправить ссылку", "btn_save_pass": "Сохранить пароль",
        "btn_transfer": "Отправить перевод", "btn_add_card": "Добавить карту",
        "btn_back": "Назад",
        "forgot_link": "Забыли пароль?", "no_acct": "Ещё нет счёта?",
        "open_link": "Открыть счёт", "have_acct": "Уже зарегистрированы?",
        "sign_in_link": "Войти", "back_login": "Вернуться ко входу",
        "pass_hint": "Не короче 8 символов.",

        "err_cred": "Неверное имя пользователя или пароль.",
        "err_exists": "Такое имя пользователя уже занято.",
        "err_pass": "Пароли не совпадают.",
        "err_pass_len": "Пароль должен быть не короче 8 символов.",
        "err_input": "Проверьте поля и попробуйте ещё раз.",
        "err_token": "Эта ссылка недействительна или устарела.",
        "err_card": "Введите номер карты из 13–19 цифр.",
        "err_exp": "Срок действия должен выглядеть как 09/29.",
        "err_funds": "Недостаточно средств на счёте-отправителе.",
        "err_same": "Выберите два разных счёта.",
        "err_amount": "Введите сумму больше нуля.",
        "err_own": "Выберите один из своих счетов.",
        "err_admin": "Требуются права администратора.",
        "err_auth": "Войдите, чтобы продолжить.",
        "ok_registered": "Счёт создан. Войдите, чтобы продолжить.",
        "ok_reset": "Пароль изменён. Войдите с новым паролем.",
        "ok_sent": "Если такое имя пользователя есть, ссылка отправлена.",
        "ok_transfer": "Перевод выполнен.",
        "ok_card": "Карта добавлена.",
        "lab_mail": "Подсказка лабы: исходящие письма видны на /_lab/outbox.",

        "dash_t": "Обзор", "welcome": "С возвращением",
        "total_label": "Всего на всех счетах",
        "accounts_h": "Ваши счета", "txns_h": "Последние операции",
        "quick_h": "Быстрые действия", "qa_transfer": "Сделать перевод",
        "qa_cards": "Управлять картами", "empty_txns": "Операций пока нет.",
        "col_date": "Дата", "col_desc": "Описание", "col_account": "Счёт",
        "col_amount": "Сумма", "acc_everyday": "Текущий",
        "acc_savings": "Накопительный", "acc_new": "Текущий счёт",
        "more": "Все переводы", "acct_no": "Счёт",
        "empty_cards": "Карт пока нет — добавьте первую ниже.",

        "cards_t": "Карты", "cards_sub": "Карты, привязанные к вашим счетам.",
        "add_h": "Добавить карту", "expires": "Действует до",
        "holder": "Держатель", "status_active": "Активна",
        "note_lost": "Потеряли карту? Заблокируйте её в приложении или "
                     "позвоните +1 800 555 0100.",

        "tr_t": "Переводы", "tr_sub": "Переводите деньги между своими счетами.",
        "history_h": "История переводов",

        "admin_t": "Администрирование",
        "admin_sub": "Сотрудники и клиенты банка.",
        "users_h": "Пользователи", "col_username": "Логин",
        "col_name": "Имя", "col_role": "Роль", "col_accounts": "Счетов",
        "col_balance": "Баланс", "role_admin": "администратор",
        "role_customer": "клиент", "flag_h": "Флаг лаборатории",
        "flag_p": "Вы вошли как администратор. Ради этого лаборатория и "
                  "существует:",

        "err_404_t": "Страница не найдена",
        "err_404_m": "Проверьте адрес или вернитесь на главную страницу.",
        "err_403_t": "Доступ запрещён",
        "err_403_m": "Эта страница доступна только администраторам банка.",
        "err_500_t": "Внутренняя ошибка сервера",
        "err_500_m": "Что-то пошло не так. Попробуйте позже.",
        "go_home": "На главную",

        "side_overview": "Обзор", "side_cards": "Карты",
        "side_transfers": "Переводы", "side_admin": "Администрирование",
        "sign_out": "Выйти", "app_lang": "Язык",
        "vuln": "Уязвимая версия", "fixed": "Исправленная версия",
    },
    "uz": {
        "nav_accounts": "Hisoblar", "nav_cards": "Kartalar",
        "nav_rates": "Kurslar", "nav_security": "Xavfsizlik",
        "nav_support": "Qo‘llab-quvvatlash",
        "nav_label": "Asosiy menyu", "lang_label": "Til",
        "signin": "Kirish", "open_acct": "Hisob ochish",
        "hero_eyebrow": "Litsenziyalangan bank · omonat himoyalangan",
        "hero_l1": "Bank xizmatlari —",
        "hero_l2": "ortiqchasiz",
        "hero_text": "Hisoblar, kartalar va jamg‘armalar bitta joyda: aniq "
                     "foizlar, yashirin komissiyasiz va soniyalarda yetib "
                     "boradigan o‘tkazmalar.",
        "hero_cta1": "Hisob ochish", "hero_cta2": "Kirish",
        "hero_mock_label": "Umumiy balans", "hero_mock_name": "Asosiy hisob",
        "hero_mock_row1": "Jamg‘arma hisobiga o‘tkazma",
        "hero_mock_row2": "Qahvaxona", "hero_mock_row3": "Keshbek",
        "stat1_v": "0.00", "stat1_l": "oylik hisob xizmati",
        "stat2_v": "4,5%", "stat2_l": "jamg‘armaga, yillik",
        "stat3_v": "12 soniya", "stat3_l": "o‘rtacha o‘tkazma",

        "prod_eyebrow": "Mahsulotlar", "prod_title": "Uchta ish — yaxshi bajarilgan",
        "p1_t": "Asosiy hisob",
        "p1_d": "Karta bilan bepul xizmat, o‘z hisoblari orasidagi zudlik "
                "o‘tkazmalar va xaridlardan 1% keshbek.",
        "p1_f1": "Oylik to‘lov yo‘q", "p1_f2": "1% keshbek",
        "p1_f3": "Bepul bankomatlar",
        "p2_t": "Jamg‘arma",
        "p2_d": "Har bir tiyinga foiz, oyiga bir marta hisoblanadi. "
                "Istalgan vaqtda oling — foiz tushmaydi.",
        "p2_f1": "Yillik 4,5%", "p2_f2": "Oylik hisoblash",
        "p2_f3": "Istalgan vaqtda yechish",
        "p3_t": "Kartalar",
        "p3_d": "Virtual karta bir daqiqada, plastik karta pochta orqali. "
                "To‘lov terminallariga tayyor.",
        "p3_f1": "Darhol chiqariladi", "p3_f2": "To‘lqinsiz to‘lov",
        "p3_f3": "3-D Secure",

        "rates_eyebrow": "Kurslar", "rates_title": "Bugungi kurslar",
        "rates_lead": "Laboratoriya uchun namoyish kurslari. Har ish "
                      "kuni 09:00 da yangilanadi.",
        "r_h_pair": "Valyuta", "r_h_buy": "Sotib olish", "r_h_sell": "Sotish",
        "r_eur": "EUR", "r_gbp": "GBP", "r_chf": "CHF",
        "r_eur_b": "1,0842", "r_eur_s": "1,0855",
        "r_gbp_b": "1,2690", "r_gbp_s": "1,2704",
        "r_chf_b": "1,1275", "r_chf_s": "1,1290",
        "dep_h": "Omonatlar", "dep_1": "Talab qilinadigan", "dep_1_v": "1,0%",
        "dep_2": "Jamg‘arma", "dep_2_v": "4,5%", "dep_3": "12 oyga",
        "dep_3_v": "5,2%",

        "steps_eyebrow": "Qanday ishlaydi",
        "steps_title": "Uch qadamda hisob",
        "s1_t": "Ro‘yxatdan o‘tish",
        "s1_d": "Ism, foydalanuvchi nomi va parol — shu saytda boshqa "
                "hech narsa so‘ralmaydi.",
        "s2_t": "Tasdiqlash",
        "s2_d": "Shaxsni tasdiqlash ilovada bir necha daqiqa davom etadi.",
        "s3_t": "Foydalanish",
        "s3_d": "Karta, o‘tkazmalar va jamg‘arma darhol ishlaydi.",

        "sec_eyebrow": "Xavfsizlik",
        "sec_title": "Pulingizga kirish nazorat ostida",
        "sec_p": "Kirish va amallar haqida ogohlantirishlar, kechayu kunduz "
                 "firibgarlikni kuzatish va ilovada bir zumda karta blokirovkasi.",
        "sec_1": "Kirish ogohlantirishi", "sec_2": "Bir zumda blokirovka",
        "sec_3": "24/7 kuzatuv",

        "foot_about": "ATLAS Bank — A04 laboratoriyasi (kriptografik "
                      "nosozliklar) uchun o‘quv sayti. Barcha ma’lumotlar "
                      "tasodifiy.",
        "foot_products": "Mahsulotlar", "foot_company": "Bank",
        "foot_support": "Qo‘llab-quvvatlash", "foot_explore": "Bo‘limlar",
        "foot_rates": "Kurslar", "foot_security": "Xavfsizlik",
        "foot_help": "Yordam markazi", "foot_contact": "Bog‘lanish",
        "foot_console": "Laboratoriya konsoli /ui",
        "foot_note": "A04 o‘quv laboratoriyasi. Faqat lokal ishating.",
        "foot_legal": "ATLAS Bank · demo litsenziya #A04-2026 · saytdagi "
                      "hisoblar, kartalar va kurslar tasodifiy.",

        "login_t": "Kirish", "login_sub": "Hisoblarga va kartalarga kirish.",
        "login_mock": "Pulingiz qoldirgan joyingizda turibdi.",
        "reg_sub": "Bir necha daqiqada hisob: ism, foydalanuvchi nomi va "
                   "parol.",
        "forgot_sub": "Foydalanuvchi nomini kiriting — biz unga tiklash "
                      "havolasini yuboramiz.",
        "reset_sub": "Yangi parol o‘ring. Eski parol ishlamay qoladi.",
        "f_user": "Foydalanuvchi nomi", "f_pass": "Parol",
        "f_full": "Ism va familiya", "f_pass2": "Parolni takrorlang",
        "f_from": "Qaysi hisobdan", "f_to": "Qaysi hisobga",
        "f_amount": "Summa", "f_note": "Izoh (ixtiyoriy)",
        "f_number": "Karta raqami", "f_exp": "Amal qilish muddati (OO/YY)",
        "f_holder": "Karta egasi",
        "btn_signin": "Kirish", "btn_register": "Hisob yaratish",
        "btn_send_link": "Havolani yuborish", "btn_save_pass": "Parolni saqlash",
        "btn_transfer": "O‘tkazmani yuborish", "btn_add_card": "Karta qo‘shish",
        "btn_back": "Orqaga",
        "forgot_link": "Parolni unutdingizmi?", "no_acct": "Hali hisob yo‘qmi?",
        "open_link": "Hisob ochish", "have_acct": "Avval ro‘yxatdan o‘tgansizmi?",
        "sign_in_link": "Kirish", "back_login": "Qaytadan kirish",
        "pass_hint": "Kamida 8 ta belgi.",

        "err_cred": "Foydalanuvchi nomi yoki parol noto‘g‘ri.",
        "err_exists": "Bunday foydalanuvchi nomi allaqachon band.",
        "err_pass": "Parollar mos kelmadi.",
        "err_pass_len": "Parol kamida 8 ta belgidan iborat bo‘lishi kerak.",
        "err_input": "Maydonlarni tekshirib, qayta urinib ko‘ring.",
        "err_token": "Bu havola yaroqsiz yoki muddati o‘tgan.",
        "err_card": "13–19 raqamli karta raqamini kiriting.",
        "err_exp": "Muddat 09/29 ko‘rinishida bo‘lishi kerak.",
        "err_funds": "Yuboruvchi hisobda mablag‘ yetarli emas.",
        "err_same": "Ikkita xisobni tanlang.",
        "err_amount": "Noldan katta summani kiriting.",
        "err_own": "O‘z hisoblarinizdan birini tanlang.",
        "err_admin": "Administrator huquqlari talab qilinadi.",
        "err_auth": "Davom etish uchun kiring.",
        "ok_registered": "Hisob yaratildi. Davom etish uchun kiring.",
        "ok_reset": "Parol o‘zgartirildi. Yangi parol bilan kiring.",
        "ok_sent": "Bunday foydalanuvchi bo‘lsa, havola yuborildi.",
        "ok_transfer": "O‘tkazma bajarildi.",
        "ok_card": "Karta qo‘shildi.",
        "lab_mail": "Laboratoriya eslatmasi: chiqayotgan xatlar /_lab/outbox "
                    "da ko‘rinadi.",

        "dash_t": "Umumiy", "welcome": "Xush kelibsiz",
        "total_label": "Barcha hisoblar bo‘yicha umumiy balans",
        "accounts_h": "Sizning hisoblaringiz", "txns_h": "So‘nggi amallar",
        "quick_h": "Tezkor amallar", "qa_transfer": "O‘tkazma qilish",
        "qa_cards": "Kartalarni boshqarish", "empty_txns": "Hali amallar yo‘q.",
        "col_date": "Sana", "col_desc": "Tavsif", "col_account": "Hisob",
        "col_amount": "Summa", "acc_everyday": "Asosiy",
        "acc_savings": "Jamg‘arma", "acc_new": "Asosiy hisob",
        "more": "Barcha o‘tkazmalar", "acct_no": "Hisob raqami",
        "empty_cards": "Hali karta yo‘q — pastdan birinchisini qo‘shing.",

        "cards_t": "Kartalar", "cards_sub": "Hisoblaringizga biriktirilgan kartalar.",
        "add_h": "Karta qo‘shish", "expires": "Amal qiladi",
        "holder": "Egasi", "status_active": "Faol",
        "note_lost": "Karta yo‘qoldimi? Ilovada bloklang yoki +1 800 555 0100 "
                     "raqamiga qo‘ng‘iroq qiling.",

        "tr_t": "O‘tkazmalar", "tr_sub": "Pulni o‘z hisoblaringiz orasida "
                                         "harakatlantiring.",
        "history_h": "O‘tkazmalar tarixi",

        "admin_t": "Boshqaruv",
        "admin_sub": "Bank xodimlari va mijozlari.",
        "users_h": "Foydalanuvchilar", "col_username": "Login", "col_name": "Ism",
        "col_role": "Rol", "col_accounts": "Hisoblar", "col_balance": "Balans",
        "role_admin": "administrator", "role_customer": "mijoz",
        "flag_h": "Laboratoriya bayrog‘i",
        "flag_p": "Siz administrator sifatida kirdingiz. Laboratoriya "
                  "shu maqsadda yaratilgan:",

        "err_404_t": "Sahifa topilmadi",
        "err_404_m": "Manzilni tekshiring yoki bosh sahifaga qayting.",
        "err_403_t": "Ruxsat yo‘q",
        "err_403_m": "Bu sahifa faqat bank administratorlari uchun.",
        "err_500_t": "Serverda ichki xato",
        "err_500_m": "Nimadir xato ketdi. Keyinroq urinib ko‘ring.",
        "go_home": "Bosh sahifaga",

        "side_overview": "Umumiy", "side_cards": "Kartalar",
        "side_transfers": "O‘tkazmalar", "side_admin": "Boshqaruv",
        "sign_out": "Chiqish", "app_lang": "Til",
        "vuln": "Zaif versiya", "fixed": "Tuzatilgan versiya",
    },
}


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
            accepted = [str(code).lower() for code, _ in request.accept_languages]
            wanted = accepted[0][:2] if accepted else ""
        g.lang = wanted if wanted in LANGS else DEFAULT_LANG

    @app.after_request
    def _remember_lang(resp):
        if request.args.get("lang") in LANGS:
            resp.set_cookie(LANG_COOKIE, request.args["lang"], samesite="Lax")
        return resp


def lang():
    """Язык текущего запроса (после register_lang)."""
    return getattr(g, "lang", DEFAULT_LANG)


def t(lang_code=None):
    """Плоский словарь переводов для страницы."""
    return T[lang_code or lang()]


# --------------------------------------------------------------- оформление
def money(value):
    """1250.4 -> '$1 250.40' — одинаково смотрится на трёх языках."""
    whole, _, frac = f"{value:,.2f}".partition(".")
    return "$" + whole.replace(",", " ") + "." + frac


def signed(value):
    """Сумма операции со знаком: '-$40.00' / '+$1 200.00'."""
    return ("-" if value < 0 else "+") + money(abs(value))


def mask(number):
    """4111111111111111 -> '**** **** **** 1111'."""
    tail = number[-4:] if len(number) >= 4 else number
    return "**** **** **** " + tail


def group(number, size=4):
    """Группирует цифры карты для показа: 4111 1111 1111 1111."""
    return " ".join(number[i:i + size] for i in range(0, len(number), size))
