🌐 [English](./README.md) · [Русский](./README.ru.md) · **Oʻzbekcha**

# A06 — Insecure Design (xavfsiz boʻlmagan arxitektura)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Kodi toza, ammo biznes-mantiqi buzilgan mini-doʻkon (JSON API): narx mijozdan keladi, miqdor va kuponlar cheklanmagan, buyurtma bosqichlarini oʻtkazib yuborish mumkin, parolni tiklash kodi esa saralab topiladi. Bu yerda «bitta xavfli satr» yoʻq: buni faqat dizaynni oʻzgartirib tuzatish mumkin.

## Nimalarni oʻrganasiz
- Skaner topa olmaydigan biznes-mantiq zaifliklarini koʻra bilish
- Pul va jarayon holatiga mijozning oʻziga ishonmaslik
- Jarayonni chekli avtomat sifatida, tahdidlarni esa suiisteʼmol holatlari (abuse cases) sifatida modellashtirish
- Bir martalik kodlarni himoyalash: urinishlar chegarasi, amal qilish muddati, kriptografik bardoshli tasodifiylik

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8051 |
| fixed (tuzatilgan) | http://127.0.0.1:8052 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** `/ui` sahifasi odatda inglizcha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8051/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8051` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8051/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8052/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
PORT=8051 python vulnerable/app.py   # http://127.0.0.1:8051
```

> ⚠️ Ilova ataylab zaif qilingan. Uni faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
Test akkauntlari: `alice` / `alice123` (balans $100) va `bob` / `S3cr3t-b0b-pass` (balans $10 000). `curl`, Postman yoki Burp (JSON) orqali ishlash qulay. `POST /reset-lab` laboratoriya maʼlumotlarini asl holatiga qaytaradi.

1. «Подарочный набор» (sovgʻa toʻplami, `product_id: 3`, $5000) ni $1 dan kam toʻlab buyurtma qiling va bayroqni `/orders/<id>/ship` dan oling.
2. Hech narsa sotmasdan alice balansini oshiring.
3. Buyurtma uchun **toʻlamasdan** yuborishni (ship) oling.
4. `bob` akkauntini parolni tiklash orqali egallang (kod logga «keladi»: `docker compose logs vulnerable`) va server nima uchun saralashdan himoyalanmaganini tushuntiring.
5. Topilgan har bir nuqson uchun buzilgan *arxitektura* qoidasini ifodalang, soʻng `fixed/` bilan solishtiring (`# FIX N` izohlari).

## Endpointlar

```
POST /login                  {"username","password"}
GET  /me
GET  /products
POST /orders                 {"items":[{"product_id","quantity"}],"coupons":[...]}
GET  /orders/<id>
POST /orders/<id>/pay
POST /orders/<id>/ship
POST /password-reset/request {"username"}
POST /password-reset/confirm {"username","otp","new_password"}
POST /reset-lab
```

## Maslahatlar

<details>
<summary>1-maslahat — narx</summary>

Mijoz buyurtma tovarlari bilan JSON yuboradi. `POST /orders` har bir pozitsiya uchun qaysi maydonlarni qabul qilishiga diqqat bilan qarang: odatda nimani server hal qiladi (katalog), nimani mijoz (miqdor) — bu maʼnoga mos keladimi?
</details>

<details>
<summary>2-maslahat — miqdor</summary>

`quantity` manfiy boʻlsa, buyurtma summasiga nima boʻladi? Juda katta boʻlsa-chi?
</details>

<details>
<summary>3-maslahat — kuponlar</summary>

`coupons` maydoni roʻyxat. Unga bir xil kodni bir necha marta yuborsangiz nima boʻladi?
</details>

<details>
<summary>4-maslahat — bosqichlar tartibi</summary>

`/pay` va `/ship` endpointlari alohida, bir-biriga bogʻliq boʻlmagan chaqiruvlar. Ularni aynan shu tartibda chaqirish majburiymi?
</details>

<details>
<summary>5-maslahat — qayta toʻlov</summary>

Bitta buyurtma uchun `/orders/<id>/pay` ni ikki marta chaqirish mumkinmi? Buyurtma summasi manfiy boʻlsa-chi (2-maslahatga qarang)?
</details>

<details>
<summary>6-maslahat — parolni tiklash</summary>

`POST /password-reset/request` kodni «yuboradi»: server logiga qarang (`docker compose logs vulnerable`), unda nechta raqam bor. Barcha variantlarni saralab chiqish uchun `/password-reset/confirm` ga nechta soʻrov yuborish kerak va server ularning sonini cheklaydimi?
</details>

## Tuzilishi
- `vulnerable/` — zaif versiya
- `fixed/` — tuzatilgan versiya
- `SOLUTION.uz.md` — yechim tahlili (spoylerlar bilan)
- `docker-compose.yml` — ikkala versiyani ishga tushirish

## Keyingi qadamlar
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — V1 boʻlimi: arxitektura, dizayn va tahdidlarni modellashtirish
