"""Сайт Lumière Café — данные, переводы и помощники страниц.

Файл одинаковый в vulnerable/ и fixed/ (побайтно), как portal.py в A01:
содержимое сайта от версии не зависит, все отличия — в app.py.

Язык интерфейса: EN / RU / UZ. Выбор хранится в cookie `site_lang`
и задаётся ссылкой `?lang=xx` (переключатель в шапке сайта).
"""
from flask import g, request

LANGS = ["en", "ru", "uz"]
DEFAULT_LANG = "en"
LANG_COOKIE = "site_lang"

# ------------------------------------------------------------------ переводы
T = {
    "en": {
        "nav_home": "Home", "nav_menu": "Menu", "nav_about": "About",
        "nav_gallery": "Gallery", "nav_contact": "Contact",
        "nav_label": "Main navigation", "book": "Book a Table",
        "lang_label": "Language",

        "hero_l1": "Good Food", "hero_l2": "Better Moments",
        "hero_text": "Lumière Café — a place where great coffee, delicious "
                     "food and cozy atmosphere come together.",
        "hero_btn": "View Menu", "hero_li1": "Great coffee",
        "hero_li2": "Fresh food", "hero_li3": "Cozy atmosphere",

        "why_eyebrow": "Why us", "why_l1": "More Than Just",
        "why_l2": "A Coffee Shop",
        "why1_t": "Premium Quality",
        "why1_d": "We use only the best ingredients for your perfect taste.",
        "why2_t": "Cozy Atmosphere",
        "why2_d": "A comfortable space to relax, work or meet with friends.",
        "why3_t": "Friendly Service",
        "why3_d": "Our team is always happy to make your day better.",

        "menu_eyebrow": "Our menu", "popular": "Popular Dishes",
        "view_full": "View Full Menu",

        "about_eyebrow": "About us", "about_l1": "A Cafe Built",
        "about_l2": "For Slow Mornings",
        "about_p1": "Lumière Café is a small roastery and kitchen in the city "
                    "centre. We roast beans in small batches every morning, "
                    "bake our own pastries and serve breakfast all day long.",
        "about_p2": "The menu follows the season: cold drinks in summer, "
                    "spiced teas and cinnamon bakes in winter.",
        "about_f1": "Since 2019", "about_f2": "Roasted daily",
        "about_f3": "4.9 guest rating",

        "gallery_eyebrow": "Gallery", "gallery_title": "Inside Lumière",
        "gallery_text": "A few frames from our hall, the counter and the "
                        "morning pastry.",

        "contact_eyebrow": "Contact", "contact_title": "Visit Us",
        "contact_text": "Five minutes from the metro, entrance from the "
                        "courtyard. Tables for groups can be reserved by phone.",
        "c_address_h": "Address", "c_address": "12 Coffee Street",
        "c_hours_h": "Opening hours",
        "c_hours_wd": "Mon–Fri  07:30 – 22:00",
        "c_hours_we": "Sat–Sun  09:00 – 23:00",
        "c_phone_h": "Phone", "c_phone": "+7 (900) 000-00-00",
        "c_mail_h": "Email", "c_mail": "hello@lumiere.test",

        "menu_title": "Menu",
        "menu_lead": "Prices are per serving in the café. Takeaway costs the "
                     "same. Seasonal dishes may change.",
        "back_menu": "Back to Menu", "ingredients": "Ingredients",
        "allergens": "Allergens", "allergens_note": "Allergen information is "
        "indicative — ask the staff for the current recipe.",
        "related": "You May Also Like",
        "crumb_home": "Home",

        "login_eyebrow": "Lumière Café", "login_title": "Staff Sign In",
        "login_sub": "A closed area: orders, shifts and reports.",
        "f_user": "Login", "f_pass": "Password", "sign_in": "Sign In",
        "forgot": "Forgot your password? Ask the shift manager.",
        "back_site": "Back to the site",
        "err_cred": "Invalid username or password.",

        "dash_title": "Staff Dashboard",
        "dash_sub": "The shift opened at 07:30. Data refreshed just now.",
        "st_orders": "orders today", "st_revenue": "revenue",
        "st_avg": "average bill", "st_guests": "guests",
        "flag_h": "Lab flag",
        "flag_p": "You signed in to the accounting system. The default "
                  "account is still in production — here is its result:",
        "last_orders": "Last orders",
        "shift": "shift #1042",
        "col_order": "Order", "col_items": "Items", "col_time": "Time",
        "col_total": "Total", "col_status": "Status",
        "st_prep": "Preparing", "st_served": "Served", "st_paid": "Paid",
        "st_refund": "Refunded",

        "err_404_t": "Page Not Found",
        "err_404_m": "Check the address or go back to the home page.",
        "err_400_t": "Invalid Request",
        "err_400_m": "The dish id must be a number.",
        "err_generic_m": "Check the address and try again.",
        "err_500_t": "Internal Server Error",
        "err_500_m": "Something went wrong. Please try again later.",
        "err_500_id": "Something went wrong. Please try again later. "
                      "(Reference: {error_id})",
        "trace_h": "Stack trace",
        "config_h": "Application configuration",
        "go_home": "Go to the homepage", "open_menu": "Open the menu",

        "vuln": "Vulnerable version", "fixed": "Fixed version",
        "foot_about": "A small roastery and kitchen: coffee, pastry and "
                      "breakfast all day.",
        "foot_explore": "Explore", "foot_visit": "Visit", "foot_hours": "Hours",
        "foot_dev": "For developers",
        "foot_console": "Lab console /ui",
        "foot_note": "Training site for lab A02 (Security Misconfiguration). "
                     "Run it locally only.",
    },
    "ru": {
        "nav_home": "Главная", "nav_menu": "Меню", "nav_about": "О нас",
        "nav_gallery": "Галерея", "nav_contact": "Контакты",
        "nav_label": "Главное меню", "book": "Забронировать стол",
        "lang_label": "Язык",

        "hero_l1": "Вкусная еда —", "hero_l2": "прекрасные моменты",
        "hero_text": "Lumière Café — место, где отличный кофе, вкусная еда "
                     "и уютная атмосфера становятся одним целым.",
        "hero_btn": "Смотреть меню", "hero_li1": "Отличный кофе",
        "hero_li2": "Всегда свежие блюда", "hero_li3": "Уютная атмосфера",

        "why_eyebrow": "Почему мы", "why_l1": "Больше, чем",
        "why_l2": "просто кофейня",
        "why1_t": "Премиальное качество",
        "why1_d": "Используем только лучшие ингредиенты, чтобы вкус был "
                  "безупречным.",
        "why2_t": "Уютная атмосфера",
        "why2_d": "Удобное место, чтобы отдохнуть, поработать или "
                  "встретиться с друзьями.",
        "why3_t": "Дружелюбный сервис",
        "why3_d": "Наша команда всегда рада сделать ваш день лучше.",

        "menu_eyebrow": "Наше меню", "popular": "Популярные блюда",
        "view_full": "Всё меню",

        "about_eyebrow": "О нас", "about_l1": "Кофейня для",
        "about_l2": "неспешных утр",
        "about_p1": "Lumière Café — небольшая обжарочная и кухня в центре "
                    "города. Каждое утро обжариваем зерно небольшими "
                    "партиями, печём свою выпечку и подаём завтраки весь день.",
        "about_p2": "Меню живёт по сезону: летом — холодные напитки, зимой — "
                    "прятные чаи и выпечка с корицей.",
        "about_f1": "С 2019 года", "about_f2": "Обжарка каждый день",
        "about_f3": "4,9 — рейтинг гостей",

        "gallery_eyebrow": "Галерея", "gallery_title": "Внутри Lumière",
        "gallery_text": "Несколько кадров из зала, стойки и утренней выпечки.",

        "contact_eyebrow": "Контакты", "contact_title": "Как нас найти",
        "contact_text": "5 минут от метро, вход со двора. Столы для компаний "
                        "можно забронировать по телефону.",
        "c_address_h": "Адрес", "c_address": "ул. Кофейная, 12",
        "c_hours_h": "Часы работы",
        "c_hours_wd": "Пн–Пт  07:30 – 22:00",
        "c_hours_we": "Сб–Вс  09:00 – 23:00",
        "c_phone_h": "Телефон", "c_phone": "+7 (900) 000-00-00",
        "c_mail_h": "Почта", "c_mail": "hello@lumiere.test",

        "menu_title": "Меню",
        "menu_lead": "Цены указаны за порцию в кофейне, навынос — те же цены. "
                     "Сезонные позиции могут меняться.",
        "back_menu": "Назад к меню", "ingredients": "Состав",
        "allergens": "Аллергены",
        "allergens_note": "Состав аллергенов ориентировочный — уточняйте "
                          "актуальный рецепт у персонала.",
        "related": "Вам может понравиться",
        "crumb_home": "Главная",

        "login_eyebrow": "Lumière Café", "login_title": "Вход для персонала",
        "login_sub": "Закрытая зона: заказы, смены и отчётность.",
        "f_user": "Логин", "f_pass": "Пароль", "sign_in": "Войти",
        "forgot": "Забыли пароль? Обратитесь к администратору смены.",
        "back_site": "На сайт кофейни",
        "err_cred": "Неверный логин или пароль.",

        "dash_title": "Панель персонала",
        "dash_sub": "Смена открыта в 07:30. Данные обновлены только что.",
        "st_orders": "заказов сегодня", "st_revenue": "выручка",
        "st_avg": "средний чек", "st_guests": "гостей",
        "flag_h": "Флаг лабы",
        "flag_p": "Вы вошли в систему учёта. Учётная запись по умолчанию так "
                  "и осталась в проде — вот её результат:",
        "last_orders": "Последние заказы",
        "shift": "смена #1042",
        "col_order": "Заказ", "col_items": "Позиции", "col_time": "Время",
        "col_total": "Сумма", "col_status": "Статус",
        "st_prep": "Готовится", "st_served": "Выдан", "st_paid": "Оплачен",
        "st_refund": "Возврат",

        "err_404_t": "Страница не найдена",
        "err_404_m": "Проверьте адрес или вернитесь на главную.",
        "err_400_t": "Некорректный запрос",
        "err_400_m": "Номер блюда должен быть числом.",
        "err_generic_m": "Проверьте адрес и повторите попытку.",
        "err_500_t": "Внутренняя ошибка сервера",
        "err_500_m": "Что-то пошло не так. Попробуйте позже.",
        "err_500_id": "Что-то пошло не так. Попробуйте позже. "
                      "(Код обращения: {error_id})",
        "trace_h": "Трассировка выполнения",
        "config_h": "Конфигурация приложения",
        "go_home": "На главную", "open_menu": "Открыть меню",

        "vuln": "Уязвимая версия", "fixed": "Исправленная версия",
        "foot_about": "Небольшая обжарочная и кухня: кофе, выпечка и завтраки "
                      "весь день.",
        "foot_explore": "Разделы", "foot_visit": "Адрес", "foot_hours": "Часы",
        "foot_dev": "Разработчикам",
        "foot_console": "Консоль лабы /ui",
        "foot_note": "Учебный сайт лабы A02 (Security Misconfiguration). "
                     "Запускайте только локально.",
    },
    "uz": {
        "nav_home": "Bosh sahifa", "nav_menu": "Menyu", "nav_about": "Biz haqimizda",
        "nav_gallery": "Galereya", "nav_contact": "Aloqa",
        "nav_label": "Asosiy menyu", "book": "Stolni band qilish",
        "lang_label": "Til",

        "hero_l1": "Mazali taom —", "hero_l2": "go'zal lahza",
        "hero_text": "Lumière Café — ajoyib kafir, mazali taom va shinam "
                     "muhit birlashgan joy.",
        "hero_btn": "Menyuni ko'rish", "hero_li1": "Ajoyib kafir",
        "hero_li2": "Doimo yangi taomlar", "hero_li3": "Shinam muhit",

        "why_eyebrow": "Nima uchun biz", "why_l1": "Faqat kafedan",
        "why_l2": "boshqasi",
        "why1_t": "Yuqori sifat",
        "why1_d": "Mazali taom uchun faqat eng yaxshi masalliqdan "
                  "foydalanamiz.",
        "why2_t": "Shinam muhit",
        "why2_d": "Dam olish, ishlash yoki do'stlar bilan uchrashish uchun "
                  "qulay joy.",
        "why3_t": "Do'stona xizmat",
        "why3_d": "Jamoamiz har doim kuningizni yaxshiroq qilishga tayyor.",

        "menu_eyebrow": "Bizning menyu", "popular": "Ommabop taomlar",
        "view_full": "To'liq menyu",

        "about_eyebrow": "Biz haqimizda", "about_l1": "Sekin uchun",
        "about_l2": "turgan kafe",
        "about_p1": "Lumière Café — markazdagi kichik kavurxona va oshxona. "
                    "Har kuni ertalab donni kichik partiyalarda kavuramiz, "
                    "o'z pechimizdan nonvoy pishiramiz va butun kun nonushta "
                    "beramiz.",
        "about_p2": "Menyu mavsumga qarab o'zgaradi: yozda — sovuq ichimliklar, "
                    "qishda — ziravorli choylar va darçinli pechva.",
        "about_f1": "2019-yildan beri", "about_f2": "Har kuni kavuriladi",
        "about_f3": "4,9 — mehmonlar reytingi",

        "gallery_eyebrow": "Galereya", "gallery_title": "Lumiero ichida",
        "gallery_text": "Zal, stol va ertalabki pechdan bir necha kadr.",

        "contact_eyebrow": "Aloqa", "contact_title": "Bizni toping",
        "contact_text": "Metrodan 5 daqiqa, hovlidan kirish. Kompaniyalar "
                        "uchun stollarni telefon orqali band qilish mumkin.",
        "c_address_h": "Manzil", "c_address": "Qahva ko'chasi, 12",
        "c_hours_h": "Ish vaqti",
        "c_hours_wd": "Du–Ju  07:30 – 22:00",
        "c_hours_we": "Ya–Ya  09:00 – 23:00",
        "c_phone_h": "Telefon", "c_phone": "+7 (900) 000-00-00",
        "c_mail_h": "Pochta", "c_mail": "hello@lumiere.test",

        "menu_title": "Menyu",
        "menu_lead": "Narxlar kafedagi bir porsiya uchun, olib ketish ham "
                     "shunday. mavsumiy taomlar o'zgarishi mumkin.",
        "back_menu": "Menyuga qaytish", "ingredients": "Tarkibi",
        "allergens": "Allergenlar",
        "allergens_note": "Allergenlar ma'lumotni taxminiy — aktual retseptni "
                          "xodimlardan so'rang.",
        "related": "Sizga yoqishi mumkin",
        "crumb_home": "Bosh sahifa",

        "login_eyebrow": "Lumière Café", "login_title": "Xodimlar kirishi",
        "login_sub": "Yopiq hudud: buyurtmalar, smenalar va hisobotlar.",
        "f_user": "Foydalanuvchi", "f_pass": "Parol", "sign_in": "Kirish",
        "forgot": "Parolni unutdingizmi? Smena menejeriga murojaat qiling.",
        "back_site": "Saytga qaytish",
        "err_cred": "Foydalanuvchi nomi yoki parol noto'g'ri.",

        "dash_title": "Xodimlar paneli",
        "dash_sub": "Smena 07:30 da ochildi. Ma'lumotlar hozir yangilandi.",
        "st_orders": "bugungi buyurtmalar", "st_revenue": "tushum",
        "st_avg": "o'rtacha chek", "st_guests": "mehmonlar",
        "flag_h": "Laboratoriya flagi",
        "flag_p": "Hisob tizimiga kirdingiz. Standart akkaunt hali ham "
                  "ishlab chiqarishda qolgan — natija shu:",
        "last_orders": "Oxirgi buyurtmalar",
        "shift": "smena #1042",
        "col_order": "Buyurtma", "col_items": "Taomlar", "col_time": "Vaqt",
        "col_total": "Jami", "col_status": "Holat",
        "st_prep": "Tayyorlanmoqda", "st_served": "Berildi", "st_paid": "To'langan",
        "st_refund": "Qaytarildi",

        "err_404_t": "Sahifa topilmadi",
        "err_404_m": "Manzilni tekshiring yoki bosh sahifaga qayting.",
        "err_400_t": "Noto'g'ri so'rov",
        "err_400_m": "Taom raqami son bo'lishi kerak.",
        "err_generic_m": "Manzilni tekshiring va qayta urinib ko'ring.",
        "err_500_t": "Server ichki xatosi",
        "err_500_m": "Nimadir xato ketdi. Keyinroq qayta urinib ko'ring.",
        "err_500_id": "Nimadir xato ketdi. Keyinroq qayta urinib ko'ring. "
                      "(Murojaat kodi: {error_id})",
        "trace_h": "Trassirovka",
        "config_h": "Ilova konfiguratsiyasi",
        "go_home": "Bosh sahifaga", "open_menu": "Menyuni ochish",

        "vuln": "Zaif versiya", "fixed": "Tuzatilgan versiya",
        "foot_about": "Kichik kavurxona va oshxona: kafir, pechva va butun "
                      "kun nonushta.",
        "foot_explore": "Bo'limlar", "foot_visit": "Manzil", "foot_hours": "Vaqt",
        "foot_dev": "Dasturchilar uchun",
        "foot_console": "Laboratoriya konsoli /ui",
        "foot_note": "A02 (Security Misconfiguration) laboratoriyasi uchun "
                     "o'quv sayti. Faqat lokal ishga tushiring.",
    },
}

# ------------------------------------------------------------------ контент
CATEGORY_LABELS = {
    "coffee": {"en": "Coffee", "ru": "Кофе", "uz": "Kafir"},
    "tea": {"en": "Tea", "ru": "Чай", "uz": "Choy"},
    "dessert": {"en": "Desserts", "ru": "Десерты", "uz": "Shirinliklar"},
    "breakfast": {"en": "Breakfast", "ru": "Завтраки", "uz": "Nonushtalar"},
}
CATEGORY_ORDER = ["coffee", "tea", "dessert", "breakfast"]

# Все поля контента — словари по языкам: {"en": ..., "ru": ..., "uz": ...}
MENU = [
    dict(id=1, cat="coffee", price="2.50",
         name={"en": "Espresso", "ru": "Эспрессо", "uz": "Espresso"},
         short={"en": "Classic in a 60 ml cup.",
                "ru": "Классика в чашке 60 мл.",
                "uz": "60 ml finjandagi klassika."},
         desc={"en": "A single shot from today's roast: full body, chocolate "
                     "aftertaste and a thick crema.",
               "ru": "Одинарный эспрессо из сегодняшней обжарки: плотный, с "
                     "шоколадным послевкусием и плотной кремой.",
               "uz": "Bugungi kavuruvdan bitta shot: to'yingan ta'm, shokolad "
                     "keyingi ta'mi va zich krem."},
         ing={"en": "Beans (Ethiopia, Colombia), water",
              "ru": "Зерно (Эфиопия, Колумбия), вода",
              "uz": "Don (Efiopiya, Kolumbiya), suv"},
         alg={"en": "None", "ru": "Не содержит", "uz": "Yo'q"}),
    dict(id=2, cat="coffee", price="3.00",
         name={"en": "Americano", "ru": "Американо", "uz": "Americano"},
         short={"en": "Espresso with hot water.",
                "ru": "Эспрессо с горячей водой.",
                "uz": "Issiq suvli espresso."},
         desc={"en": "A lighter everyday option: a double espresso and hot "
                     "water, milk on the side if you like.",
               "ru": "Более лёгкий вариант на каждый день: двойной эспрессо и "
                     "горячая вода, можно взять с молоком на стороне.",
               "uz": "Kun uchun yengil variant: ikki espresso va issiq suv, "
                     "istasangiz alohida sut."},
         ing={"en": "Espresso, hot water", "ru": "Эспрессо, горячая вода",
              "uz": "Espresso, issiq suv"},
         alg={"en": "None", "ru": "Не содержит", "uz": "Yo'q"}),
    dict(id=3, cat="coffee", price="3.80",
         name={"en": "Cappuccino", "ru": "Капучино", "uz": "Kapuchino"},
         short={"en": "Espresso with milk foam.",
                "ru": "Эспрессо с молочной пеной.",
                "uz": "Sut ko'pigi bilan espresso."},
         desc={"en": "Equal parts espresso, milk and dense foam. Cocoa on "
                     "top on request.",
               "ru": "Равные части эспрессо, молока и плотной пены. Подаём с "
                     "щепоткой какао по желанию.",
               "uz": "Espresso, sut zich fo'zi teng qismda. Istasangiz "
                     "kakao sepib beramiz."},
         ing={"en": "Espresso, milk 3.2%", "ru": "Эспрессо, молоко 3,2%",
              "uz": "Espresso, sut 3,2%"},
         alg={"en": "Milk", "ru": "Молоко", "uz": "Sut"}),
    dict(id=4, cat="coffee", price="4.20",
         name={"en": "Latte", "ru": "Латте", "uz": "Latte"},
         short={"en": "Mild coffee with plenty of milk.",
                "ru": "Мягкий кофе с объёмным молоком.",
                "uz": "Ko'p sutli yumshoq kafir."},
         desc={"en": "Our most ordered drink: lots of milk, a delicate coffee "
                     "note and vanilla syrup free on request.",
               "ru": "Наш самый заказываемый напиток: много молока, тонкий "
                     "кофейный вкус и ванильный сироп — по желанию, бесплатно.",
               "uz": "Eng ko'p buyurtma qilinadigan ichimlik: ko'p sut, "
                     "nozik kafir ta'mi va bepul vanil siropi."},
         ing={"en": "Espresso, milk 3.2%", "ru": "Эспрессо, молоко 3,2%",
              "uz": "Espresso, sut 3,2%"},
         alg={"en": "Milk", "ru": "Молоко", "uz": "Sut"}),
    dict(id=5, cat="coffee", price="4.50",
         name={"en": "Flat White", "ru": "Флэт-уайт", "uz": "Flat White"},
         short={"en": "Double espresso and micro-foam.",
                "ru": "Двойной эспрессо и микро-пена.",
                "uz": "Ikki espresso va mikro-fo'z."},
         desc={"en": "For those who like their coffee brighter: two shots of "
                     "espresso and a thin velvety foam.",
               "ru": "Для тех, кто любит кофе ярче: две порции эспрессо и "
                     "тонкая бархатная пена без большого объёма.",
               "uz": "Kafirni yorqinroq yaxshi ko'rganlar uchun: ikki espresso "
                     "shooti va yupqa aksincha ko'pik."},
         ing={"en": "Double espresso, milk 3.2%",
              "ru": "Двойной эспрессо, молоко 3,2%",
              "uz": "Ikki espresso, sut 3,2%"},
         alg={"en": "Milk", "ru": "Молоко", "uz": "Sut"}),
    dict(id=6, cat="coffee", price="4.80",
         name={"en": "Mocha", "ru": "Мокко", "uz": "Mokka"},
         short={"en": "Coffee, chocolate and milk.",
                "ru": "Кофе, шоколад и молоко.",
                "uz": "Kafir, shokolad va sut."},
         desc={"en": "Dark chocolate syrup, espresso and milk — almost a "
                     "dessert, but with caffeine.",
               "ru": "Тёмный шоколадный сироп, эспрессо и молоко — почти "
                     "десерт, но с кофеином.",
               "uz": "Qora shokolad siropi, espresso va sut — deyarli "
                     "shirinlik, lekin kafein bilan."},
         ing={"en": "Espresso, milk 3.2%, chocolate syrup",
              "ru": "Эспрессо, молоко 3,2%, шоколадный сироп",
              "uz": "Espresso, sut 3,2%, shokolad siropi"},
         alg={"en": "Milk", "ru": "Молоко", "uz": "Sut"}),
    dict(id=7, cat="tea", price="3.00",
         name={"en": "Assam", "ru": "Ассам", "uz": "Assam"},
         short={"en": "Strong black tea.",
                "ru": "Крепкий чёрный чай.",
                "uz": "Kuchli qora choy."},
         desc={"en": "A rich malty tea — with breakfast and after a meal. "
                     "Served in a 400 ml pot.",
               "ru": "Насыщенный чай с маллиновым вкусом — к завтраку и после "
                     "еды. Подаём в чайнике на 400 мл.",
               "uz": "Boy, malt ta'mli choy — nonushta va ovqatdan keyin. "
                     "400 ml choynakda beriladi."},
         ing={"en": "Assam black tea, water", "ru": "Чёрный чай Ассам, вода",
              "uz": "Assam qora choyi, suv"},
         alg={"en": "None", "ru": "Не содержит", "uz": "Yo'q"}),
    dict(id=8, cat="tea", price="3.20",
         name={"en": "Sencha", "ru": "Сенча", "uz": "Sencha"},
         short={"en": "Fresh green tea.",
                "ru": "Свежий зелёный чай.",
                "uz": "Yangi yashil choy."},
         desc={"en": "Japanese sencha with a grassy aroma. Brewed at 80 °C "
                     "so it never turns bitter.",
               "ru": "Японская сенча с травянистым ароматом. Завариваем при "
                     "80 °C, чтобы не горчил.",
               "uz": "O't hidi bilan yapon senchasi. Archishmasin uchun 80 °C "
                     "da damlanadi."},
         ing={"en": "Sencha green tea, water", "ru": "Зелёный чай Сенча, вода",
              "uz": "Sencha yashil choyi, suv"},
         alg={"en": "None", "ru": "Не содержит", "uz": "Yo'q"}),
    dict(id=9, cat="tea", price="3.50",
         name={"en": "Herbal Tea", "ru": "Травяной сбор", "uz": "O't choyi"},
         short={"en": "Mint, lemon balm and linden.",
                "ru": "Мята, мелисса и липа.",
                "uz": "Yalpiz, melissa va chinnigullar."},
         desc={"en": "Our own sugar-free blend: calming in the evening and "
                     "good with desserts.",
               "ru": "Домашний сбор без сахара: успокаивает вечером и хорошо "
                     "идёт с десертами.",
               "uz": "Uy aralishmasi, shakarsiz: kechqurun tinchlantiradi va "
                     "shirinliklar bilan yaxshi ketadi."},
         ing={"en": "Mint, lemon balm, linden, water",
              "ru": "Мята, мелисса, липа, вода",
              "uz": "Yalpiz, melissa, chinnigul, suv"},
         alg={"en": "None", "ru": "Не содержит", "uz": "Yo'q"}),
    dict(id=10, cat="dessert", price="5.50",
         name={"en": "New York Cheesecake", "ru": "Чизкейк «Нью-Йорк»",
               "uz": "New York cheesecake"},
         short={"en": "Classic, cream-cheese based.",
                "ru": "Классика на сливочном сыре.",
                "uz": "Pishloq asosidagi klassika."},
         desc={"en": "Baked every day: a dense cream-cheese filling on a "
                     "shortcrust base, served with berry sauce.",
               "ru": "Печём каждый день: плотный крем-чиз на песочной основе, "
                     "подаём с ягодным соусом.",
               "uz": "Har kuni pishiramiz: qisqa pishloqli to'ldirgich, "
                     "mevali sous bilan beriladi."},
         ing={"en": "Cream cheese, eggs, sugar, cream, shortcrust",
              "ru": "Сливочный сыр, яйца, сахар, сливки, песочная основа",
              "uz": "Krem pishloq, tuxum, shakar, krem, qisqa pishiriq"},
         alg={"en": "Milk, eggs, gluten", "ru": "Молоко, яйца, глютен",
              "uz": "Sut, tuxum, gluten"}),
    dict(id=11, cat="dessert", price="4.50",
         name={"en": "Cinnamon Roll", "ru": "Булочка с корицей",
               "uz": "Darçinli bulochka"},
         short={"en": "Warm, with glaze.",
                "ru": "Тёплая, с глазурью.",
                "uz": "Issiq, glazur bilan."},
         desc={"en": "Straight from the oven with cinnamon and a light sugar "
                     "glaze. Reheated before serving.",
               "ru": "Свежая из печи, с корицей и лёгкой сахарной глазурью. "
                     "Разогреваем перед подачей.",
               "uz": "Pechdan yangi, darçin va yengil shakar glazur bilan. "
                     "Berishdan oldin qizdiriladi."},
         ing={"en": "Flour, butter, cinnamon, sugar, yeast",
              "ru": "Мука, сливочное масло, корица, сахар, дрожжи",
              "uz": "Un, sariyog', darçin, shakar, xamirturush"},
         alg={"en": "Gluten, milk, eggs", "ru": "Глютен, молоко, яйца",
              "uz": "Gluten, sut, tuxum"}),
    dict(id=12, cat="dessert", price="5.00",
         name={"en": "Carrot Cake", "ru": "Морковный торт", "uz": "Ko'k tort"},
         short={"en": "With cream cheese and nuts.",
                "ru": "С крем-чизом и орехами.",
                "uz": "Krem pishloq va yong'oq bilan."},
         desc={"en": "A classic carrot cake with a cream-cheese frosting and "
                     "walnuts on top.",
               "ru": "Классический морковный с кремом из сливочного сыра и "
                     "грецким орехом сверху.",
               "uz": "Klassik ko'k tort, krem pishloqli krem va yuqorida "
                     "yong'oqlar."},
         ing={"en": "Carrot, flour, cream cheese, sugar, walnuts",
              "ru": "Морковь, мука, крем-чиз, сахар, грецкий орех",
              "uz": "Ko'k, un, krem pishloq, shakar, yong'oq"},
         alg={"en": "Milk, eggs, gluten, nuts", "ru": "Молоко, яйца, глютен, орехи",
              "uz": "Sut, tuxum, gluten, yong'oq"}),
    dict(id=13, cat="breakfast", price="6.50",
         name={"en": "Avocado Toast", "ru": "Тост с авокадо",
               "uz": "Avokadoli tost"},
         short={"en": "Avocado, poached egg and greens.",
                "ru": "Авокадо, яйцо пашот и зелень.",
                "uz": "Avokado, poched tuxum va ko'katlar."},
         desc={"en": "Wholegrain bread, hand-mashed avocado, a poached egg "
                     "and seasonal greens. Cooked to order.",
               "ru": "Цельнозерновой хлеб, авокадо вручную, яйцо пашот и "
                     "сезонная зелень. Готовим по заказу.",
               "uz": "Butun donali non, qo'lda ezilgan avokado, poched tuxum "
                     "va mavsumiy ko'katlar. Buyurtma bo'yicha tayyorlanadi."},
         ing={"en": "Wholegrain bread, avocado, egg, lemon, microgreens",
              "ru": "Хлеб цельнозерновой, авокадо, яйцо, лимон, микрозелень",
              "uz": "Butun donali non, avokado, tuxum, limon, mikroko'katlar"},
         alg={"en": "Gluten, eggs", "ru": "Глютен, яйца",
              "uz": "Gluten, tuxum"}),
    dict(id=14, cat="breakfast", price="5.20",
         name={"en": "Granola & Yogurt", "ru": "Гранола с йогуртом",
               "uz": "Granola bilan yogurt"},
         short={"en": "House granola and berries.",
                "ru": "Домашняя гранола и ягоды.",
                "uz": "Uy granolasi va mevalar."},
         desc={"en": "We bake our own granola: oats, honey and nuts, served "
                     "with Greek yogurt and seasonal berries.",
               "ru": "Запекаем гранолу сами: овсянка, мёд и орехи. Подаём с "
                     "греческим йогуртом и сезонными ягодами.",
               "uz": "Granolani o'zimiz pishiramiz: yulaf, asal va yong'oq. "
                     "Yunon yogurti va mavsumiy mevalar bilan beriladi."},
         ing={"en": "Oats, yogurt, honey, nuts, berries",
              "ru": "Овсяные хлопья, йогурт, мёд, орехи, ягоды",
              "uz": "Yulaf, yogurt, asal, yong'oq, mevalar"},
         alg={"en": "Milk, nuts", "ru": "Молоко, орехи",
              "uz": "Sut, yong'oq"}),
    dict(id=15, cat="breakfast", price="7.00",
         name={"en": "Herb Omelette", "ru": "Омлет с зеленью",
               "uz": "O'tli omlet"},
         short={"en": "Three eggs, spinach and tomatoes.",
                "ru": "Три яйца, шпинат и томаты.",
                "uz": "Uch tuxum, ismaloq va pomidorlar."},
         desc={"en": "A soft pan omelette with spinach and roasted tomatoes. "
                     "Good for a late breakfast.",
               "ru": "Нежный омлет на сковороде с шпинатом и печёными "
                     "томатами. Подходит для позднего завтрака.",
               "uz": "Ismaloq va pishirilgan pomidor bilan yumshoq omlet. "
                     "Kech nonushtasi uchun mos."},
         ing={"en": "Eggs, spinach, tomatoes, cream, herbs",
              "ru": "Яйца, шпинат, томаты, сливки, зелень",
              "uz": "Tuxum, ismaloq, pomidor, krem, o'tlar"},
         alg={"en": "Eggs, milk", "ru": "Яйца, молоко",
              "uz": "Tuxum, sut"}),
    dict(id=16, cat="breakfast", price="7.50",
         name={"en": "Buddha Bowl", "ru": "Будда-боул", "uz": "Buddha bowl"},
         short={"en": "Fresh vegetables, quinoa, healthy and tasty.",
                "ru": "Свежие овощи, киноа, полезно и вкусно.",
                "uz": "Yangi sabzavotlar, kinva, foydali va mazali."},
         desc={"en": "Roasted vegetables, quinoa, avocado and greens with a "
                     "light tahini dressing.",
               "ru": "Запечённые овощи, киноа, авокадо и зелень с лёгкой "
                     "заправкой из тахини.",
               "uz": "Pishirilgan sabzavotlar, kinva, avokado va ko'katlar "
                     "yengil tahini sous bilan."},
         ing={"en": "Quinoa, seasonal vegetables, avocado, tahini",
              "ru": "Киноа, овощи сезона, авокадо, тахини",
              "uz": "Kinva, mavsumiy sabzavotlar, avokado, tahini"},
         alg={"en": "Sesame", "ru": "Кунжут", "uz": "Kunjut"}),
]

FEATURED_IDS = (4, 11, 13, 16)

# Иллюстрация к каждому блюду (файлы в static/img/)
IMG = {
    1: "dish-latte.svg", 2: "dish-latte.svg", 3: "dish-latte.svg",
    4: "dish-latte.svg", 5: "dish-latte.svg", 6: "dish-latte.svg",
    7: "dish-tea.svg", 8: "dish-tea.svg", 9: "dish-tea.svg",
    10: "dish-cake.svg", 11: "dish-roll.svg", 12: "dish-cake.svg",
    13: "dish-toast.svg", 14: "dish-bowl.svg", 15: "dish-toast.svg",
    16: "dish-bowl.svg",
}

# Заказы для панели персонала (вымышленные данные для лабы)
ORDERS = [
    dict(no=1042, time="10:42", total="16.40", state="wait", status="st_prep",
         items={"en": "Latte ×2, Cinnamon Roll",
                "ru": "Латте ×2, Булочка с корицей",
                "uz": "Latte ×2, Darçinli bulochka"}),
    dict(no=1041, time="10:38", total="8.30", state="ok", status="st_served",
         items={"en": "Cappuccino, Cheesecake",
                "ru": "Капучино, Чизкейк «Нью-Йорк»",
                "uz": "Kapuchino, New York cheesecake"}),
    dict(no=1040, time="10:31", total="14.20", state="ok", status="st_served",
         items={"en": "Americano ×3, Granola & Yogurt",
                "ru": "Американо ×3, Гранола с йогуртом",
                "uz": "Americano ×3, Granola bilan yogurt"}),
    dict(no=1039, time="10:24", total="9.70", state="ok", status="st_paid",
         items={"en": "Avocado Toast, Sencha",
                "ru": "Тост с авокадо, Сенча",
                "uz": "Avokadoli tost, Sencha"}),
    dict(no=1038, time="10:15", total="9.80", state="bad", status="st_refund",
         items={"en": "Mocha, Carrot Cake",
                "ru": "Мокко, Морковный торт",
                "uz": "Mokka, Ko'k tort"}),
]

STATS = {"orders": "148", "revenue": "742.30", "avg": "5.02", "guests": "96"}

GALLERY = ["img/hero.svg", "img/dish-latte.svg", "img/dish-roll.svg",
           "img/dish-toast.svg", "img/dish-bowl.svg", "img/about.svg"]

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
            resp.set_cookie(LANG_COOKIE, request.args["lang"],
                            samesite="Lax")
        return resp


def lang():
    return getattr(g, "lang", DEFAULT_LANG)


def t(lang_code=None):
    """Плоский словарь переводов для страницы."""
    return T[lang_code or lang()]


def _tr(field, lang_code):
    return field[lang_code]


def menu_for(lang_code=None):
    """Меню с уже подставленными переводами."""
    code = lang_code or lang()
    return [dict(id=m["id"], cat=m["cat"], price=m["price"],
                 img=IMG[m["id"]],
                 tag=CATEGORY_LABELS[m["cat"]][code],
                 name=_tr(m["name"], code), short=_tr(m["short"], code),
                 desc=_tr(m["desc"], code),
                 ingredients=_tr(m["ing"], code),
                 allergens=_tr(m["alg"], code))
            for m in MENU]


def get_item(number):
    """Позиция меню по её номеру или None (с переводами текущего языка)."""
    return next((m for m in menu_for() if m["id"] == number), None)


def home_data():
    return {"featured": [m for m in menu_for() if m["id"] in FEATURED_IDS],
            "gallery": GALLERY}


def menu_data():
    return {"categories": [
        {"code": code, "label": CATEGORY_LABELS[code][lang()],
         "dishes": [m for m in menu_for() if m["cat"] == code]}
        for code in CATEGORY_ORDER
    ]}


def item_data(item):
    related = [m for m in menu_for()
               if m["cat"] == item["cat"] and m["id"] != item["id"]][:4]
    for m in menu_for():
        if len(related) >= 4:
            break
        if m["id"] != item["id"] and m not in related:
            related.append(m)
    return {"item": item, "related": related}


def dashboard_data(flag=None):
    code = lang()
    return {"orders": [dict(o, items=o["items"][code],
                            status=T[code][o["status"]]) for o in ORDERS],
            "stats": STATS, "flag": flag}
