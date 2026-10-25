🌐 [English](./README.md) · [Русский](./README.ru.md) · **Oʻzbekcha**

# A01 — Broken Access Control (kirish nazoratining buzilishi)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Uchta foydalanuvchisi (`alice`, `bob`, `admin`) bor korporativ HR-portal (**TestLab HR**): xodimlar HRga arizalar yuboradi va hamkasblar roʻyxatini koʻradi, administratorda esa alohida boʻlim bor. Tizimga kirish mavjud, ammo server hamma joyda ham resurs **kimga tegishli** ekanini va foydalanuvchining **roli qanday** ekanini tekshirmaydi.

## Nimalarni oʻrganasiz
- IDOR ni topish (soʻrovdagi resurs identifikatorini almashtirish)
- Autentifikatsiya («siz kimsiz») va avtorizatsiyani («sizga nima mumkin») farqlash
- Huquqlarni har bir soʻrovda serverda tekshirish, «sukut boʻyicha taqiqlangan» tamoyili asosida

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8001 |
| fixed (tuzatilgan) | http://127.0.0.1:8002 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** Portal odatda inglizcha ochiladi. Oʻzbekchaga oʻtish uchun sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi. Yoki manzil qatoriga `http://127.0.0.1:8001/?lang=uz` (vulnerable) yoki `http://127.0.0.1:8002/?lang=uz` (fixed) yozing. API konsoli (`/ui`) uchun ham xuddi shunday: `http://127.0.0.1:8001/ui?lang=uz`.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ Ilova ataylab zaif qilingan. Faqat lokal ishga tushiring va internetga chiqarmang.

Manzilni brauzerda oching: TestLab HR portali ochiladi. Pastki oʻngdagi **Lab** tugmasi laboratoriya panelini ochadi: oʻzi belgilanadigan topshiriqlar, maslahatlar va portal soʻrovlari jurnali. Raw API konsoli `/ui` da; `curl` va Postman `/` dan avvalgidek JSON oladi.

## Topshiriq
Test akkaunti: `alice` / `alice123`.

1. `alice` sifatida kiring (`POST /login`, `username` va `password` bilan JSON).
2. **Admin**ga tegishli arizani oʻqing (unda `FLAG{...}` flagi yashirilgan; portalda arizalar `#/requests/<id>` manzilida ochiladi).
3. Admin boʻlmagan holda `/admin/users` administrator boʻlimini oching (portalda: `#/admin`).
4. Xuddi shu soʻrovlarni **fixed** versiyada takrorlang va kirish yopilganiga ishonch hosil qiling.
5. `vulnerable/app.py` va `fixed/app.py` ni solishtiring: tuzatilgan joylar `FIX` bilan belgilangan.

## Maslahatlar
1. `GET /api/notes` ni oching: arizalaringizning `id` qiymatlari qanday?
2. Begona `id` qoʻyilsa, `GET /api/notes/<id>` nima qaytaradi?
3. `GET /admin/users` dan oldin server qanday tekshiruvlarni bajaradi? Portal menyu bandini sizdan yashiradi, lekin bu serverni toʻxtatadimi?

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- Resurs egasini va foydalanuvchi rolini **serverda**, har bir soʻrov uchun tekshirish
- Sukut boʻyicha taqiq: kirish faqat aniq ruxsat berilgan joyda
- «Foydalanuvchi URL ni bilmaydi» degan taxminga tayanmaslik
