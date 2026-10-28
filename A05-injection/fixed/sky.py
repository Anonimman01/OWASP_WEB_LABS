"""Сайт авиакомпании Skyline — переводы, данные страниц и помощники.

Файл одинаковый в vulnerable/ и fixed/ (побайтно), как portal.py в A01,
cafe.py в A02 и bank.py в A04: содержимое сайта от версии не зависит,
все отличия — в app.py.

Язык интерфейса: EN / RU / UZ. Выбор хранится в cookie `site_lang`
и задаётся ссылкой `?lang=xx` (переключатель в шапке сайта).
"""
from datetime import datetime

from flask import g, request

LANGS = ["en", "ru", "uz"]
DEFAULT_LANG = "en"
LANG_COOKIE = "site_lang"

BRAND = {"name": "SKYLINE", "sub": "AIR"}

# Аэропорты: код IATA -> название на трёх языках
CITIES = {
    "TAS": {"en": "Tashkent", "ru": "Ташкент", "uz": "Toshkent"},
    "IST": {"en": "Istanbul", "ru": "Стамбул", "uz": "Stambul"},
    "DXB": {"en": "Dubai", "ru": "Дубай", "uz": "Dubay"},
    "LHR": {"en": "London", "ru": "Лондон", "uz": "London"},
    "BER": {"en": "Berlin", "ru": "Берлин", "uz": "Berlin"},
    "FCO": {"en": "Rome", "ru": "Рим", "uz": "Rim"},
    "ALA": {"en": "Almaty", "ru": "Алматы", "uz": "Almatо"},
}

MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "ru": ["янв", "фев", "мар", "апр", "мая", "июн",
           "июл", "авг", "сен", "окт", "ноя", "дек"],
    "uz": ["yanv", "fev", "mar", "apr", "may", "iyn",
           "iyl", "avg", "sen", "okt", "noy", "dek"],
}

# ------------------------------------------------------------------ переводы
T = {
    "en": {
        "nav_label": "Main navigation", "lang_label": "Language",
        "nav_routes": "Destinations", "nav_why": "Why Skyline",
        "nav_trips": "My trips", "nav_admin": "Admin",
        "signin": "Sign in", "register": "Register", "sign_out": "Sign out",

        "hero_eyebrow": "7 destinations · direct flights daily",
        "hero_l1": "Fly somewhere warm,",
        "hero_l2": "land on time",
        "hero_text": "Search flights across our network, book a seat in a "
                     "couple of clicks and manage your trips in one place.",
        "hero_cta1": "Search flights", "hero_cta2": "Sign in",
        "f_from": "From", "f_to": "To", "f_date": "Date",
        "f_any": "Any date", "btn_search": "Search",
        "stat1_v": "7", "stat1_l": "destinations",
        "stat2_v": "24/7", "stat2_l": "support in chat",
        "stat3_v": "$132", "stat3_l": "cheapest ticket",

        "routes_eyebrow": "Destinations", "routes_title": "Popular routes",
        "routes_lead": "Tickets for these flights are on sale right now. "
                       "Prices are per person, taxes included.",
        "view_all": "All flights", "seats_left": "{n} seats left",
        "direct": "Direct", "one_stop": "1 stop",

        "why_eyebrow": "Why Skyline", "why_title": "Travel without the friction",
        "w1_t": "Honest prices",
        "w1_d": "The price you see is the price you pay: baggage and seat "
                "selection are already included.",
        "w2_t": "On-time flights",
        "w2_d": "94% of our flights arrive on schedule. If we are late, you "
                "get a voucher without asking.",
        "w3_t": "One account for everything",
        "w3_d": "Search, booking and your trips live in the same cabinet — "
                "no paper tickets.",

        "foot_about": "Skyline is a training site for lab A05 (Injection). "
                      "All flights and prices are fictional.",
        "foot_travel": "Travel", "foot_lab": "Lab",
        "foot_search": "Search flights", "foot_console": "Lab console /ui",
        "foot_note": "Training lab A05. Run it locally only.",
        "foot_legal": "Skyline · demo certificate #A05-2026 · flights and "
                      "prices on this site are fictional.",

        "res_found": "{n} flights found", "res_none": "No flights found",
        "res_none_hint": "Try a different city code or clear the date and "
                         "price filters.",
        "filters_h": "Refine search", "f_max": "Max price, $",
        "btn_filter": "Apply", "err_query": "Search error",
        "col_price": "Price", "col_seats": "Seats", "details": "Details",
        "book": "Book",

        "back_results": "Back to results",
        "lbl_departure": "Departure", "lbl_arrival": "Arrival",
        "lbl_duration": "Duration", "lbl_price": "Price",
        "lbl_seats": "Seats left", "lbl_note": "Note",
        "passengers": "Passengers", "btn_book": "Book now",
        "need_login": "Sign in to book a seat.",
        "booked_ok": "Seat booked. It is waiting for you in My trips.",
        "no_seats": "There are no seats left on this flight.",
        "tag_charter": "Charter",

        "trips_t": "My trips", "trips_sub": "Flights you have booked.",
        "trips_empty": "No trips yet — find a flight on the home page.",
        "col_flight": "Flight", "col_route": "Route", "col_date": "Date",
        "col_passengers": "Passengers", "col_status": "Status",
        "status_ok": "Confirmed",

        "login_t": "Sign in", "login_sub": "Access your trips and bookings.",
        "reg_sub": "An account in a couple of minutes: a username and a "
                   "password.",
        "f_user": "Username", "f_full": "Full name",
        "f_pass": "Password", "f_pass2": "Repeat password",
        "btn_signin": "Sign in", "btn_register": "Create account",
        "no_acct": "No account yet?", "open_link": "Register",
        "have_acct": "Already registered?", "sign_in_link": "Sign in",
        "pass_hint": "At least 8 characters.",
        "err_cred": "Incorrect username or password.",
        "err_exists": "That username is already taken.",
        "err_pass": "The passwords do not match.",
        "err_pass_len": "The password must be at least 8 characters.",
        "err_input": "Check the fields and try again.",
        "err_auth": "Sign in to continue.",
        "err_admin": "Administrator access required.",
        "ok_registered": "Account created. Sign in to continue.",

        "admin_t": "Administration", "admin_sub": "Fleet, users and service "
                                                  "tools.",
        "tool_h": "Airport node check",
        "tool_sub": "Resolves the address of an airport server. Only "
                    "administrators can run it.",
        "f_host": "Host", "btn_check": "Run check", "out_h": "Output",
        "table_h": "All flights", "col_no": "Flight", "col_from": "From",
        "col_to": "To",
        "users_h": "Users", "col_username": "Username", "col_name": "Name",
        "col_role": "Role", "role_admin": "admin", "role_user": "customer",
        "flag_h": "Laboratory flag",
        "flag_p": "You are signed in as an administrator. This is what the "
                  "lab is about:",

        "err_404_t": "Page Not Found",
        "err_404_m": "Check the address or go back to the home page.",
        "err_403_t": "Access Denied",
        "err_403_m": "This page is only available to Skyline administrators.",
        "err_500_t": "Internal Server Error",
        "err_500_m": "Something went wrong. Please try again later.",
        "go_home": "Go to the homepage",

        "vuln": "Vulnerable version", "fixed": "Fixed version",
    },
    "ru": {
        "nav_label": "Главное меню", "lang_label": "Язык",
        "nav_routes": "Направления", "nav_why": "Почему Skyline",
        "nav_trips": "Мои поездки", "nav_admin": "Админ",
        "signin": "Войти", "register": "Регистрация", "sign_out": "Выйти",

        "hero_eyebrow": "7 направлений · прямые рейсы каждый день",
        "hero_l1": "Летите туда, где тепло, —",
        "hero_l2": "прилетайте вовремя",
        "hero_text": "Ищите рейсы по нашей сети, бронируйте место в пару "
                     "кликов и управляйте поездками в одном кабинете.",
        "hero_cta1": "Найти рейс", "hero_cta2": "Войти",
        "f_from": "Откуда", "f_to": "Куда", "f_date": "Дата",
        "f_any": "Любая дата", "btn_search": "Искать",
        "stat1_v": "7", "stat1_l": "направлений",
        "stat2_v": "24/7", "stat2_l": "поддержка в чате",
        "stat3_v": "$132", "stat3_l": "самый дешёвый билет",

        "routes_eyebrow": "Направления", "routes_title": "Популярные рейсы",
        "routes_lead": "Билеты на эти рейсы уже в продаже. Цена указана за "
                       "пассажира, налоги включены.",
        "view_all": "Все рейсы", "seats_left": "осталось мест: {n}",
        "direct": "Прямой", "one_stop": "1 пересадка",

        "why_eyebrow": "Почему Skyline", "why_title": "Путешествие без лишнего",
        "w1_t": "Честные цены",
        "w1_d": "Цена в поиске — это цена в чеке: багаж и выбор места уже "
                "включены.",
        "w2_t": "Вовремя",
        "w2_d": "94% наших рейсов прибывают по расписанию. Опоздали — "
                "получите ваучер без вопросов.",
        "w3_t": "Один аккаунт на всё",
        "w3_d": "Поиск, бронирование и поездки живут в одном кабинете — "
                "бумажных билетов нет.",

        "foot_about": "Skyline — учебный сайт лаборатории A05 (инъекции). "
                      "Все рейсы и цены вымышленные.",
        "foot_travel": "Путешествия", "foot_lab": "Лаборатория",
        "foot_search": "Найти рейс", "foot_console": "Консоль лабы /ui",
        "foot_note": "Учебная лаборатория A05. Запускайте только локально.",
        "foot_legal": "Skyline · демо-сертификат № A05-2026 · рейсы и цены "
                      "на сайте вымышленные.",

        "res_found": "Найдено рейсов: {n}", "res_none": "Рейсы не найдены",
        "res_none_hint": "Попробуйте другой код города или сбросьте фильтры "
                         "по дате и цене.",
        "filters_h": "Уточнить поиск", "f_max": "Цена до, $",
        "btn_filter": "Применить", "err_query": "Ошибка поиска",
        "col_price": "Цена", "col_seats": "Места", "details": "Подробнее",
        "book": "Бронировать",

        "back_results": "К результатам",
        "lbl_departure": "Вылет", "lbl_arrival": "Прилёт",
        "lbl_duration": "В пути", "lbl_price": "Цена",
        "lbl_seats": "Осталось мест", "lbl_note": "Примечание",
        "passengers": "Пассажиров", "btn_book": "Забронировать",
        "need_login": "Войдите, чтобы забронировать место.",
        "booked_ok": "Место забронировано — оно ждёт вас в разделе «Мои "
                     "поездки».",
        "no_seats": "На этом рейсе не осталось мест.",
        "tag_charter": "Чартер",

        "trips_t": "Мои поездки", "trips_sub": "Рейсы, которые вы забронировали.",
        "trips_empty": "Поездок пока нет — найдите рейс на главной.",
        "col_flight": "Рейс", "col_route": "Маршрут", "col_date": "Дата",
        "col_passengers": "Пассажиров", "col_status": "Статус",
        "status_ok": "Подтверждено",

        "login_t": "Вход", "login_sub": "Доступ к поездкам и бронированиям.",
        "reg_sub": "Аккаунт за пару минут: имя пользователя и пароль.",
        "f_user": "Имя пользователя", "f_full": "Имя и фамилия",
        "f_pass": "Пароль", "f_pass2": "Повторите пароль",
        "btn_signin": "Войти", "btn_register": "Создать аккаунт",
        "no_acct": "Ещё нет аккаунта?", "open_link": "Регистрация",
        "have_acct": "Уже зарегистрированы?", "sign_in_link": "Войти",
        "pass_hint": "Не короче 8 символов.",
        "err_cred": "Неверное имя пользователя или пароль.",
        "err_exists": "Такое имя пользователя уже занято.",
        "err_pass": "Пароли не совпадают.",
        "err_pass_len": "Пароль должен быть не короче 8 символов.",
        "err_input": "Проверьте поля и попробуйте ещё раз.",
        "err_auth": "Войдите, чтобы продолжить.",
        "err_admin": "Требуются права администратора.",
        "ok_registered": "Аккаунт создан. Войдите, чтобы продолжить.",

        "admin_t": "Администрирование", "admin_sub": "Флот, пользователи и "
                                                      "служебные инструменты.",
        "tool_h": "Проверка узла аэропорта",
        "tool_sub": "Резолвит адрес сервера аэрпорта. Доступно только "
                    "администраторам.",
        "f_host": "Хост", "btn_check": "Запустить", "out_h": "Вывод",
        "table_h": "Все рейсы", "col_no": "Рейс", "col_from": "Откуда",
        "col_to": "Куда",
        "users_h": "Пользователи", "col_username": "Логин", "col_name": "Имя",
        "col_role": "Роль", "role_admin": "администратор",
        "role_user": "клиент",
        "flag_h": "Флаг лаборатории",
        "flag_p": "Вы вошли как администратор. Ради этого лаборатория и "
                  "существует:",

        "err_404_t": "Страница не найдена",
        "err_404_m": "Проверьте адрес или вернитесь на главную страницу.",
        "err_403_t": "Доступ запрещён",
        "err_403_m": "Эта страница доступна только администраторам Skyline.",
        "err_500_t": "Внутренняя ошибка сервера",
        "err_500_m": "Что-то пошло не так. Попробуйте позже.",
        "go_home": "На главную",

        "vuln": "Уязвимая версия", "fixed": "Исправленная версия",
    },
    "uz": {
        "nav_label": "Asosiy menyu", "lang_label": "Til",
        "nav_routes": "Yoʻnalishlar", "nav_why": "Nega Skyline",
        "nav_trips": "Sayohatlarim", "nav_admin": "Admin",
        "signin": "Kirish", "register": "Roʻyxatdan oʻtish",
        "sign_out": "Chiqish",

        "hero_eyebrow": "7 yoʻnalish · har kuni toʻgʻridan-toʻgʻri reyslar",
        "hero_l1": "Issiq joyga uching, —",
        "hero_l2": "oʻz vaqtida qoʻning",
        "hero_text": "Tarmoq boʻylab reyslarni qidiring, bir necha bosishda "
                     "oʻrinni band qiling va sayohatlaringizni bitta "
                     "kabinetdan boshqaring.",
        "hero_cta1": "Reys qidirish", "hero_cta2": "Kirish",
        "f_from": "Qayerdan", "f_to": "Qayerga", "f_date": "Sana",
        "f_any": "Istalgan sana", "btn_search": "Qidirish",
        "stat1_v": "7", "stat1_l": "yoʻnalish",
        "stat2_v": "24/7", "stat2_l": "chatda qoʻllab-quvvatlash",
        "stat3_v": "$132", "stat3_l": "eng arzon chipta",

        "routes_eyebrow": "Yoʻnalishlar", "routes_title": "Ommabop reyslar",
        "routes_lead": "Bu reyslar chiptalari sotuvda. Narx bir yoʻlovchi "
                       "uchun, soliq kiritilgan.",
        "view_all": "Barcha reyslar", "seats_left": "qolgan oʻrinlar: {n}",
        "direct": "Toʻgʻridan-toʻgʻri", "one_stop": "1 ta qoʻnish",

        "why_eyebrow": "Nega Skyline", "why_title": "Ortiqchasiz sayohat",
        "w1_t": "Halol narxlar",
        "w1_d": "Qidiruvda koʻrgan narx — toʻlov narxi: yuk va oʻrin "
                "tanlash allaqachon kiritilgan.",
        "w2_t": "Oʻz vaqtida",
        "w2_d": "Reyslarimizning 94%i jadval boʻyicha uchadi. Kechiksak — "
                "soʻramasdan voucher olasiz.",
        "w3_t": "Hammasi uchun bitta hisob",
        "w3_d": "Qidiruv, bron va sayohatlar bitta kabinetda — qogʻoz "
                "chiptalar yoʻq.",

        "foot_about": "Skyline — A05 laboratoriyasi (inyeksiyalar) uchun "
                      "oʻquv sayti. Barcha reyslar va narxlar tasodifiy.",
        "foot_travel": "Sayohat", "foot_lab": "Laboratoriya",
        "foot_search": "Reys qidirish", "foot_console": "Laboratoriya konsoli /ui",
        "foot_note": "A05 oʻquv laboratoriyasi. Faqat lokal ishating.",
        "foot_legal": "Skyline · demo sertifikat #A05-2026 · saytdagi "
                      "reyslar va narxlar tasodifiy.",

        "res_found": "Topilgan reyslar: {n}", "res_none": "Reyslar topilmadi",
        "res_none_hint": "Boshqa shahar kodini koʻring yoki sana va narx "
                         "filtrini tozalang.",
        "filters_h": "Qidiruvni aniqlashtirish", "f_max": "Narx gacha, $",
        "btn_filter": "Qoʻllash", "err_query": "Qidiruv xatosi",
        "col_price": "Narx", "col_seats": "Oʻrinlar", "details": "Batafsil",
        "book": "Bron qilish",

        "back_results": "Natijalarga qaytish",
        "lbl_departure": "Joʻnash", "lbl_arrival": "Kelish",
        "lbl_duration": "Yoʻlda", "lbl_price": "Narx",
        "lbl_seats": "Qolgan oʻrinlar", "lbl_note": "Izoh",
        "passengers": "Yoʻlovchilar", "btn_book": "Bron qilish",
        "need_login": "Oʻrin bron qilish uchun kiring.",
        "booked_ok": "Oʻrin bron qilindi — u «Sayohatlarim» boʻlimida "
                     "sizni kutmoqda.",
        "no_seats": "Bu reysda oʻrin qolmadi.",
        "tag_charter": "Charter",

        "trips_t": "Sayohatlarim", "trips_sub": "Bron qilgan reyslaringiz.",
        "trips_empty": "Hali sayohat yoʻq — bosh sahifada reys toping.",
        "col_flight": "Reys", "col_route": "Yoʻnalish", "col_date": "Sana",
        "col_passengers": "Yoʻlovchilar", "col_status": "Holat",
        "status_ok": "Tasdiqlangan",

        "login_t": "Kirish", "login_sub": "Sayohatlarga va bronga kirish.",
        "reg_sub": "Bir necha daqiqada hisob: foydalanuvchi nomi va parol.",
        "f_user": "Foydalanuvchi nomi", "f_full": "Ism va familiya",
        "f_pass": "Parol", "f_pass2": "Parolni takrorlang",
        "btn_signin": "Kirish", "btn_register": "Hisob yaratish",
        "no_acct": "Hali hisob yoʻqmi?", "open_link": "Roʻyxatdan oʻtish",
        "have_acct": "Avval roʻyxatdan oʻtgansizmi?", "sign_in_link": "Kirish",
        "pass_hint": "Kamida 8 ta belgi.",
        "err_cred": "Foydalanuvchi nomi yoki parol notoʻgʻri.",
        "err_exists": "Bunday foydalanuvchi nomi allaqachon band.",
        "err_pass": "Parollar mos kelmadi.",
        "err_pass_len": "Parol kamida 8 ta belgidan iborat boʻlishi kerak.",
        "err_input": "Maydonlarni tekshirib, qayta urinib koʻring.",
        "err_auth": "Davom etish uchun kiring.",
        "err_admin": "Administrator huquqlari talab qilinadi.",
        "ok_registered": "Hisob yaratildi. Davom etish uchun kiring.",

        "admin_t": "Boshqaruv", "admin_sub": "Flot, foydalanuvchilar va "
                                              "xizmat vositalari.",
        "tool_h": "Aeroport tuguni tekshiruvi",
        "tool_sub": "Aeroport serverining manzilini aniqlaydi. Faqat "
                    "administratorlar uchun.",
        "f_host": "Host", "btn_check": "Ishga tushirish", "out_h": "Chiqish",
        "table_h": "Barcha reyslar", "col_no": "Reys", "col_from": "Qayerdan",
        "col_to": "Qayerga",
        "users_h": "Foydalanuvchilar", "col_username": "Login", "col_name": "Ism",
        "col_role": "Rol", "role_admin": "administrator",
        "role_user": "mijoz",
        "flag_h": "Laboratoriya bayrogʻi",
        "flag_p": "Siz administrator sifatida kirdingiz. Laboratoriya "
                  "shu maqsadda yaratilgan:",

        "err_404_t": "Sahifa topilmadi",
        "err_404_m": "Manzilni tekshiring yoki bosh sahifaga qayting.",
        "err_403_t": "Ruxsat yoʻq",
        "err_403_m": "Bu sahifa faqat Skyline administratorlari uchun.",
        "err_500_t": "Serverda ichki xato",
        "err_500_m": "Nimadir xato ketdi. Keyinroq urinib koʻring.",
        "go_home": "Bosh sahifaga",

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
def price(value):
    """214 -> '$214' — одинаково смотрится на трёх языках."""
    return f"${value}"


def date_fmt(iso, lang_code=None):
    """'2026-11-14' -> '14 Nov 2026' / '14 ноя 2026' / '14 noy 2026'."""
    code = lang_code or lang()
    try:
        day = datetime.strptime(iso, "%Y-%m-%d")
    except (TypeError, ValueError):
        return iso or ""
    return f"{day.day} {MONTHS[code][day.month - 1]} {day.year}"


def dur(minutes):
    """255 -> '4 h 15 m' / '4 ч 15 мин' / '4 soat 15 daq'."""
    code = lang()
    units = {"en": ("h", "m"), "ru": ("ч", "мин"), "uz": ("soat", "daq")}
    h, m = divmod(int(minutes), 60)
    return f"{h} {units[code][0]} {m} {units[code][1]}"


def city(code, lang_code=None):
    """Код IATA -> название города (или сам код, если аэропорт не найден)."""
    entry = CITIES.get(code)
    return entry[lang_code or lang()] if entry else (code or "—")
