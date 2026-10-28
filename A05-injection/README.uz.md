🌐 [English](./README.md) · [Русский](./README.ru.md) · **Oʻzbekcha**

# A05 — Injection (inyeksiyalar)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Tasodifiy **Skyline** aviakompaniyasining sayti: reys qidiruvi, natijalar, bronlashli reys sahifasi, «Sayohatlarim», kirish/roʻyxatdan oʻtish va aeroport tugunini tekshiruvchi vositasiga ega boshqaruv paneli. Interfeys koʻp tilli (EN / RU / UZ, sarlavhadagi almashtirgich). Foydalanuvchi kiritgan maʼlumot SQL-soʻrovlarga va buyruq satriga tushadi, shuning uni kodga aylantirish mumkin: **SQL-inyeksiya** va **command injection**.

## Nimalarni oʻrganasiz
- Foydalanuvchi maʼlumotlari SQL-soʻrov maʼnosini qanday oʻzgartirishini tushunish
- Kirishni aylanib oʻtish, yashirin maʼlumotni ochish va begona yozuvlarni SQL-inyeksiya orqali olish (oʻquv ilovasida)
- `os.popen` yonidagi satr yopishtirish nima uchun xavfli ekanini koʻrish
- Himoyalanish: parametrlangan soʻrovlar, kiritish oq roʻyxatlari, shellsiz ishlash

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
pip install -r vulnerable/requirements.txt   # fixed uchun: fixed/requirements.txt
python vulnerable/app.py                     # http://127.0.0.1:5000
```

> ⚠️ Ilova ataylab zaif qilingan. Faqat lokal ishga tushiring va internetga chiqarmang.
> Tugun tekshiruvi `ping` dan foydalanadi (Linux/macOS/Docker) — Windows da oddiy tekshiruv xato koʻrsatadi, lekin command injection mashqi u yerda ham ishlaydi: `;` oʻrnida `&` ishlating.

## Topshiriq
Test akkaunti: `alice` / `alice123`. Sayt sahifalarini brauzerda ochish qulayroq: laboratoriya konsoli `/ui` da.

1. `admin` sifatida **parolni bilmasdan** kiring (`POST /login`). Adminning `/me` da flag bor.
2. Reys qidiruvi (`GET /flights?from=...&to=...`) orqali oddiy yoʻlovchilardan **charter reysni** koʻrsating, oching va flagni toping.
3. Xuddi shu qidiruv orqali `users` jadvalidan administratorning sirini (`FLAG{...}` flagi) oling.
4. Administrator huquqlarini oling (1-bosqich) va aeroport tuguni tekshiruvi (`POST /admin/check`) orqali oʻz buyrugʻingizni ishga tushirib, server muhitidan flagni oʻqing.
5. Hammasini **fixed** versiyada takrorlang va nega ishlamasligini tushuntiring.
6. `vulnerable/app.py` va `fixed/app.py` ni solishtiring: tuzatilgan joylar `FIX` bilan belgilangan.

## Maslahatlar
1. Foydalanuvchi nomiga bitta tirnoq `'` qoʻyilsa nima boʻladi? SQL xatosi koʻrinadimi?
2. SQL da `--` izohni boshlaydi. Kirish soʻrovida nimani izohga olish mumkin?
3. Qidiruv soʻrovida `hidden = 0` sharti bor. Uni qanday zararsizlantirish mumkin?
4. `UNION SELECT` boshqa jadvaldan qatorlar qoʻshadi, lekin ustunlar soni dastlabki soʻrovnikiga mos kelishi kerak (SELECT dagi ustunlarni sanang).
5. Tugun tekshiruvi host maydonidan buyruq yigʻadi. Qaysi ajratuvchi (`;` Linux/macOS da, `&` Windows da) qoʻshimcha buyruq bajarishga imkon beradi va flag jarayonning qayerida turadi?

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- **SQL:** qatorlarni yopishtirish emas, parametrlangan soʻrovlar (`?` va qiymatlarni alohida uzatish)
- **Buyruqlar:** foydalanuvchi kiritganidan shell buyruqi yigʻilmaydi — argumentsiz roʻyxat, shellsiz va oq roʻyxat tekshiruvi (masalan `^[A-Za-z0-9.-]+$`)
- **Chuqurlashtirilgan himoya:** BD xatolari matnini koʻrsatmaslik, kiritish uzunligi va formatini cheklash, BD hisob yozuvida minimal huquqlar
- Har bir kiritishni (HTTP parametrlari, sarlavhalar, fayl nomlari) ishonchsiz maʼlumot deb bilish, kod emas
