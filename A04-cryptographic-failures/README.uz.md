🌐 [English](./README.md) · [Русский](./README.ru.md) · **Oʻzbekcha**

# A04 — Cryptographic Failures (kriptografik nosozliklar)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Akkauntlar va bogʻlangan bank kartalari bor servis (barcha maʼlumotlar xayoliy, karta raqamlari test uchun). Xavfsizlik kriptografiyaga qurilgan, lekin xatolar bilan bajarilgan: parollarning zaif saqlanishi, oldindan aytib boʻladigan tokenlar, sessiyaning zaif kaliti, shifrlanmagan karta maʼlumotlari.

## Nimalarni oʻrganasiz
- Parollarning xavfsiz saqlanishini (tuzli scrypt, bcrypt, Argon2) xavfsiz boʻlmagan saqlanishdan (tuzsiz MD5) farqlash
- Oldindan aytib boʻladigan tokenlar va zaif maxfiy kalitlar nega xavfli ekanini tushunish
- Sezgir maʼlumotlarni shifrlash va keraksiz ravishda tashqariga bermaslik
- Sirlarni manba kodidan tashqarida saqlash

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8031 |
| fixed (tuzatilgan) | http://127.0.0.1:8032 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** `/ui` sahifasi odatda inglizcha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8031/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8031` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8031/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8032/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt   # fixed uchun: fixed/requirements.txt
python vulnerable/app.py                     # http://127.0.0.1:5000
```

> ⚠️ Ilova ataylab zaif qilingan. Faqat lokal ishga tushiring va internetga chiqarmang.
> Laboratoriyada ishga tushirishni murakkablashtirmaslik uchun HTTPS yoʻq. Real tizimda butun trafik TLS orqali oʻtishi, cookie larda esa `Secure` bayrogʻi boʻlishi kerak.

## Topshiriq
Test akkauntlari: `alice` / `sunshine`, `bob` / `qwerty`. Har birida bogʻlangan karta bor.

`GET /_lab/dump` (bazaning sizib chiqishini imitatsiya qiladi) va `GET /_lab/outbox` (pochta qutisini imitatsiya qiladi) xizmat endpointlari faqat oʻqitish uchun kerak.

1. Baza sizib chiqdi deb tasavvur qiling: `/_lab/dump` ni oching. Parollar va karta raqamlari qanday koʻrinishda saqlanyapti?
2. `wordlist.txt` lugʻatidan foydalaning va `alice` hamda `bob` parollarini ularning xeshlaridan tiklang. `admin` bilan bu chiqadimi?
3. Administrator huquqlarini (adminning `/me` sida flag bor) **ikki usulda** oling:
   - parolni tiklash orqali (`POST /reset-request`, `POST /reset/<token>`);
   - sessiya cookie si orqali.
4. Barcha qadamlarni **fixed** versiyada takrorlang va ular nega ishlamasligini tushuntiring.
5. `vulnerable/app.py` va `fixed/app.py` ni solishtiring: tuzatilgan joylar `FIX` bilan belgilangan.

## Maslahatlar
1. Parol xeshida nechta belgi bor va bu qanday algoritm? Unda «tuz» bormi?
2. Oʻzingiz uchun parolni tiklashni soʻrang va `/_lab/outbox` dagi havolani koʻring. Token sizning ismingiz bilan qanday bogʻliq?
3. Sessiya cookie si maxfiy kalit bilan imzolanadi. Kalit juda oddiy boʻlsa-chi?
4. `GET /cards` nima qaytaradi?

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- Parollar: unikal tuzli scrypt, bcrypt yoki Argon2, hech qachon MD5 yoki SHA-1 emas
- Tokenlar: faqat kriptografik jihatdan puxta generator (`secrets`), xeshni saqlash, amal qilish muddatini cheklash, bir martalik qilish
- Maxfiy kalitlar: muhitdan yoki sirlar menejeridan olingan uzun tasodifiy qiymatlar
- Sezgir maʼlumotlar: saqlashda shifrlash, maskalangan holda koʻrsatish, ortiqchasini bermaslik
- Butun trafik faqat HTTPS orqali
