🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A10 — Yechim tahlili (spoylerlar)

Misollar: `http://127.0.0.1:8091` (vulnerable) va `http://127.0.0.1:8092` (fixed) ga `curl`. Windows'da Git Bash yoki WSL qulayroq (yoki PowerShell'da `curl.exe`).

## 1-nuqson — javobdagi batafsil xatolar

Raqam boʻlmagan `month` qayta ishlanmagan istisnoga olib keladi. «Nosozliklarni tuzatish» xato ishlovchisi mijozga hamma narsani beradi:

```bash
curl -s "http://127.0.0.1:8091/report?month=abc"
# {"config": {"database": "sqlite:///:memory:", "env": "production",
#             "internal_api_key": "FLAG{a10_verbose_errors}"},
#  "error": "invalid literal for int() with base 10: 'abc'",
#  "trace": ["Traceback (most recent call last):",
#            "  File \"/usr/local/lib/python3.12/site-packages/flask/app.py\", line 917, in full_dispatch_request", ...]}
```

Javobda til va freymvork versiyasi, fayl yoʻllari va kod qatorlari, yana kalitli ichki konfiguratsiya bor. Hujumchi uchun bu ilovaning tayyor xaritasi.

**Qoida:** mijozga: qisqa neytral xabar va `error_id`. Trassirovka, konfiguratsiya va tafsilotlar server logida qoladi, nosozliklarni tuzatish rejimlari prodakshenda oʻchirilgan.

**Fix:** yagona ishlovchi `{"error": "внутренняя ошибка сервера", "error_id": "..."}` qaytaradi, trassirovka esa shu `error_id` boʻyicha logga yoziladi (`# FIX 1`). Kutilgan kiritish xatosini (`month` son emas) ilova oʻzi qayta ishlaydi va 400 bilan javob beradi.

## 2-nuqson — kirish tekshiruvida fail-open

`3` hujjat «buzilgan»: `level` da son emas, `TOP` matni yotibdi. Kirish tekshiruvi har qanday xatoni ushlaydi va bu holda kirishga ruxsat beradi:

```bash
curl -s -c a.txt -X POST http://127.0.0.1:8091/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
for i in 1 2 3 4; do curl -s -b a.txt http://127.0.0.1:8091/documents/$i; echo; done
# 1: {"content": "Сегодня: борщ и плов.", ...}
# 2: {"error": "недостаточно прав"}
# 3: {"content": "FLAG{a10_fail_open} — бюджет на следующий год", ...}   <- yopiq boʻlishi kerak edi!
# 4: {"error": "недостаточно прав"}
```

Bu yerda `int("TOP")` `ValueError` ni chiqaradi, `except Exception: return True` esa nosozlikni ruxsatga aylantiradi. Haqiqiy tizimlarda bunday xato buzilgan maʼlumotlar, siyosatlar servisi mavjud emasligi, taym-aut yoki kutilmagan kiritishda yuzaga keladi.

**Qoida:** kirish tekshiruvi ishdan chiqsa, standart javob «yoʻq» (fail-closed). Bunda xatoni loglaymiz, sababi topilib tuzatilishi uchun.

**Fix:** `except` `False` qaytaradi va qaysi tekshiruv bajarilmaganini logga yozadi (`# FIX 2`). fixed da `3` hujjat maʼlumotlar tuzatilmaguncha hamma uchun yopiq.

## 3-nuqson — qisman bajarilgan amal

Uchta krujkadan iborat buyurtma: omborda ular ikkita. Ilova avval pulni yechadi va faqat keyin omborga qaraydi:

```bash
curl -s -b a.txt http://127.0.0.1:8091/me
# {"balance": 100, ...}
curl -s -b a.txt -X POST http://127.0.0.1:8091/orders -H 'Content-Type: application/json' -d '{"item_id":1,"qty":3}'
# {"error": "на складе осталось 2, а нужно 3", "type": "RuntimeError", "trace": [...], "config": {...}}   (500)
curl -s -b a.txt http://127.0.0.1:8091/me
# {"balance": 40, ...}
curl -s http://127.0.0.1:8091/_lab/consistency
# {"flag": "FLAG{a10_partial_operation}", "money_lost": {"alice": 60}, "note": "деньги списаны, а заказов на эти суммы нет"}
```

60 yechib olindi, buyurtma yoʻq. Har bir SQL-soʻrov darhol saqlandi (avtokommit), amalning «yarmini» qaytarishga esa hech narsa yoʻq.

**Qoida:** bir necha qadamdan iborat amal atomar bajariladi: yo hammasi, yo hech narsa. Bu tranzaksiya, taqsimlangan tizimlarda esa kompensatsiya qiluvchi amallar (saga) va idempotentlik.

**Fix:** butun amal `BEGIN IMMEDIATE` … `COMMIT` ichida, har qanday xatoda `ROLLBACK` (`# FIX 3`). Qadamlar tartibi vulnerable dagidek qoldirilgan, gap aynan tranzaksiyada ekani koʻrinishi uchun. fixed da xuddi shu buyurtma 409 beradi, balans 100 boʻlib qoladi, `/_lab/consistency` esa `{"money_lost": {}}` koʻrsatadi.

## 4-nuqson — limitlar yoʻq

Oddiy soʻrov: 800×600 rasm. Ammo yuqori chegara yoʻq:

```bash
curl -s -X POST http://127.0.0.1:8091/thumbnail -H 'Content-Type: application/json' -d '{"width":800,"height":600}'
# {"estimated_mb": 1.83, "ok": true}
curl -s -X POST http://127.0.0.1:8091/thumbnail -H 'Content-Type: application/json' -d '{"width":20000,"height":20000}'
# {"error": "сервис упал: не хватило памяти"}   (500)
curl -s -b a.txt http://127.0.0.1:8091/me
# {"error": "сервис недоступен"}   (503)
curl -s http://127.0.0.1:8091/health
# {"flag": "FLAG{a10_no_limits}", "status": "crashed", ...}   (503)
curl -s -X POST http://127.0.0.1:8091/reset-lab
```

20000×20000 piksel — har bir piksel uchun 4 bayt hisobida deyarli 1,5 GB. Laboratoriyada yiqilish taqlid qilinadi, hayotda esa bu OOM-killer, qotib qolgan jarayon va hamma uchun mavjud boʻlmagan servis. Alohida: soʻrovning oʻzi hajmi cheklanmagan va uzoq ishlash uchun taym-autlar yoʻq.

**Qoida:** kiruvchi maʼlumotlar chegaralarini resurs sarflashdan **oldin** tekshiramiz: soʻrov tanasi hajmi, elementlar oʻlchami va soni, ichma-ichlik chuqurligi, bajarilish vaqti (taym-autlar), soʻrovlar chastotasi (rate limit).

**Fix:** `MAX_CONTENT_LENGTH` (8 KB, Flask 413 ni oʻzi qaytaradi), ruxsat etilgan tomon 1–2048 piksel va qayta ishlashdan oldin xotira bahosini tekshirish (`# FIX 4`). Xuddi shu soʻrov 413 oladi, servis ishlashda davom etadi.

## 5-nuqson — javobdagi xom istisno matni

`q2` hisoboti yoʻq, `archive` esa «buzilgan» (fayl oʻrnida katalog). Ilova `str(e)` ni qaytaradi:

```bash
curl -s http://127.0.0.1:8091/reports/q1
# {"name": "q1", "text": "Отчёт за 1 квартал: выручка выросла на 4%.\n"}
curl -s http://127.0.0.1:8091/reports/q2
# {"error": "[Errno 2] No such file or directory: '/tmp/a10v_v0oz0vii/q2.txt'"}
curl -s http://127.0.0.1:8091/reports/archive
# {"error": "[Errno 21] Is a directory: '/tmp/a10v_v0oz0vii/archive.txt'"}
```

Xato matnlaridan operatsion tizim (`/tmp/...` yoʻli yoki Windows'da `C:\Users\<ism>\AppData\...`), maʼlumotlar yotgan katalog va ilova mantiqi koʻrinadi.

**Qoida:** istisno xabari dasturchi uchun moʻljallangan, foydalanuvchi uchun emas. Kutilgan vaziyatlarni («fayl yoʻq») maʼnoli javob bilan qayta ishlaymiz, kutilmaganlarini yagona ishlovchiga beramiz.

**Fix:** `FileNotFoundError` alohida qayta ishlanadi va neytral «отчёт не найден» beradi (`# FIX 5`), qolgan hamma narsa yagona ishlovchiga tushadi va `error_id` bilan qaytariladi.

## fixed ni tekshirish

```bash
curl -s "http://127.0.0.1:8092/report?month=abc"
# {"error": "month должен быть числом от 1 до 12"}   (400)
curl -s http://127.0.0.1:8092/reports/archive
# {"error": "внутренняя ошибка сервера", "error_id": "1d6406c3"}   (500; trassirovka faqat server konsolida)
curl -s -c b.txt -X POST http://127.0.0.1:8092/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
curl -s -b b.txt http://127.0.0.1:8092/documents/3
# {"error": "недостаточно прав"}   (403)
curl -s -b b.txt -X POST http://127.0.0.1:8092/orders -H 'Content-Type: application/json' -d '{"item_id":1,"qty":3}'
# {"error": "недостаточно товара на складе"}   (409)
curl -s -b b.txt http://127.0.0.1:8092/me
# {"balance": 100, ...}
curl -s -X POST http://127.0.0.1:8092/thumbnail -H 'Content-Type: application/json' -d '{"width":20000,"height":20000}'
# {"error": "допустимая сторона: от 1 до 2048 пикселей"}   (413)
curl -s http://127.0.0.1:8092/reports/q2
# {"error": "отчёт не найден"}   (404)
```

Qonuniy stsenariylar avvalgidek ishlaydi: `alice` `1` hujjatni oʻqiydi, `bob` `2` hujjatni oʻqiydi, bitta krujkaga oddiy buyurtma oʻtadi, 800×600 rasm qayta ishlanadi. Har bir yashirilgan xatoning tafsilotlarini server konsolidan `error_id` boʻyicha qidiring.

## Xulosa

| № | Nuqson | Qanday koʻrsatilgan | fixed da nima |
|---|--------|---------------------|---------------|
| 1 | Batafsil xatolar | `?month=abc` javobida trassirovka va kalitli konfiguratsiya | Yagona ishlovchi: mijozga `error_id`, tafsilotlar logga |
| 2 | Fail-open | Buzilgan `level` maxfiy hujjatni ochdi | Fail-closed: tekshiruv nosozligi rad etish va logga yozishni anglatadi |
| 3 | Orqaga qaytarish yoʻq | 60 yechildi, buyurtma yoʻq | Tranzaksiya: xatoda `ROLLBACK`, balans oʻzgarmaydi |
| 4 | Limitlar yoʻq | Bitta 20000×20000 soʻrov servisni «yiqitadi» | Soʻrov tanasi va oʻlchamlar limiti, resurs ajratishdan oldin 413 |
| 5 | Xom istisno matni | Javobda serverdagi fayl yoʻli | Neytral xabarlar, tafsilotlar faqat logda |
