🌐 [Русский](./README.md) · **Oʻzbekcha**

# A05 — Injection (inyeksiyalar)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Tizimga kirish, mahsulotlarni qidirish, qidiruv natijalari sahifasi va mehmonlar kitobi bor mini-doʻkon. Foydalanuvchi kiritgan maʼlumot SQL-soʻrovlarga va HTML ga ishlovsiz tushadi, shuning uchun uni kodga aylantirish mumkin: **SQL-inyeksiyalar** va **XSS** (qaytarilgan va saqlanuvchi).

## Nimalarni oʻrganasiz
- Foydalanuvchi maʼlumotlari SQL-soʻrov maʼnosini qanday oʻzgartirishini tushunish
- SQL-inyeksiya orqali kirishni aylanib oʻtish va begona maʼlumotlarni olish (oʻquv ilovasida)
- Qaytarilgan va saqlanuvchi XSS oʻrtasidagi farqni koʻrish
- Himoyalanish: parametrlangan soʻrovlar, chiqarishni ekranlash, CSP

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8041 |
| fixed (tuzatilgan) | http://127.0.0.1:8042 |

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ Ilova ataylab zaif qilingan. Faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
Test akkaunti: `alice` / `alice123`. `/search` va `/guestbook` sahifalarini brauzerda ochish qulayroq.

1. `admin` sifatida **parolni bilmasdan** kiring (`POST /login`).
2. Mahsulotlarni qidirish (`GET /products?q=...`) orqali oddiy xaridorlardan yashirilgan mahsulotni koʻrsating.
3. Xuddi shu qidiruv orqali `users` jadvalidan administratorning sirini (`FLAG{...}` flagi) oling.
4. `/search?q=...` sahifasi skriptingizni bajarishiga erishing (qaytarilgan XSS), soʻng xuddi shuni mehmonlar kitobi orqali qiling (saqlanuvchi XSS). Tekshirish uchun `alert(1)` yetarli.
5. Hammasini **fixed** versiyada takrorlang va nega ishlamasligini tushuntiring.
6. `vulnerable/app.py` va `fixed/app.py` ni solishtiring: tuzatilgan joylar `FIX` bilan belgilangan.

## Maslahatlar
1. Foydalanuvchi nomiga bitta tirnoq `'` qoʻyilsa nima boʻladi? SQL xatosi koʻrinadimi?
2. SQL da `--` izohni boshlaydi. Kirish soʻrovida nimani izohga olish mumkin?
3. Qidiruv soʻrovida `hidden = 0` sharti bor. Uni qanday zararsizlantirish mumkin?
4. `UNION SELECT` boshqa jadvaldan qatorlar qoʻshadi, lekin ustunlar soni dastlabki soʻrovnikiga mos kelishi kerak.
5. XSS uchun xabar HTML-sahifaga qanday tushishiga qarang.

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- **SQL:** qatorlarni yopishtirish emas, parametrlangan soʻrovlar (`?` va qiymatlarni alohida uzatish)
- **XSS:** maʼlumotlarni HTML ga chiqarishda ekranlash, avtomatik ekranlashli shablonizatorlar
- **Chuqurlashtirilgan himoya:** `Content-Security-Policy` sarlavhasi, kiritish uzunligi va formatini cheklash, BD hisob yozuvida minimal huquqlar
- Foydalanuvchiga BD xatolari matnini koʻrsatmaslik
