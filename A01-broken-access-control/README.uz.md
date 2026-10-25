🌐 [Русский](./README.md) · **Oʻzbekcha**

# A01 — Broken Access Control (kirish nazoratining buzilishi)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Uchta foydalanuvchisi (`alice`, `bob`, `admin`) bor qaydlar ilovasi. Tizimga kirish mavjud, ammo server hamma joyda ham resurs **kimga tegishli** ekanini va foydalanuvchining **roli qanday** ekanini tekshirmaydi.

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

> 🌐 **Interfeysni oʻzbek tilida ochish.** Brauzeringiz tili, masalan, rus tilida boʻlsa, `/ui` sahifasi avval ruscha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8001/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8001` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8001/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8002/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ Ilova ataylab zaif qilingan. Faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
Test akkaunti: `alice` / `alice123`.

1. `alice` sifatida kiring (`POST /login`, `username` va `password` bilan JSON).
2. **Admin**ga tegishli qaydni oʻqing (unda `FLAG{...}` flagi yashirilgan).
3. Admin boʻlmagan holda `/admin/users` administrator boʻlimini oching.
4. Xuddi shu soʻrovlarni **fixed** versiyada takrorlang va kirish yopilganiga ishonch hosil qiling.
5. `vulnerable/app.py` va `fixed/app.py` ni solishtiring: tuzatilgan joylar `FIX` bilan belgilangan.

## Maslahatlar
1. `GET /api/notes` ni oching: qaydlaringizning `id` qiymatlari qanday?
2. Begona `id` qoʻyilsa, `GET /api/notes/<id>` nima qaytaradi?
3. `GET /admin/users` dan oldin server qanday tekshiruvlarni bajaradi?

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- Resurs egasini va foydalanuvchi rolini **serverda**, har bir soʻrov uchun tekshirish
- Sukut boʻyicha taqiq: kirish faqat aniq ruxsat berilgan joyda
- «Foydalanuvchi URL ni bilmaydi» degan taxminga tayanmaslik
