🌐 [Русский](./README.md) · **Oʻzbekcha**

# A07 — Authentication Failures (autentifikatsiya nosozliklari)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Roʻyxatdan oʻtish, kirish, «meni eslab qol» va parolni almashtirish bor mini-servis.
Kodda SQL-inyeksiya yoki XSS yoʻq: bu laboratoriyaning barcha yettita nuqsoni autentifikatsiyada sessiyalar, tokenlar va tekshiruvlar qanday tuzilganida: zaif parol siyosati, foydalanuvchilarni sanab chiqish, saralashdan himoyaning yoʻqligi, sessiyani qotirish (fixation), faqat koʻrinish uchun qilingan logout, oldindan aytib boʻladigan «meni eslab qol» tokeni va joriy parolni qayta kiritmasdan parolni almashtirish.

## Nimalarni oʻrganasiz
- Autentifikatsiya (sen kimsan) va avtorizatsiyani (senga nima mumkin) farqlash
- Kirishda sessiya nima uchun qayta chiqarilishi kerakligini koʻrish (session fixation)
- Logout faqat brauzerda cookie'ni oʻchirish emas, serverdagi amal boʻlishi kerakligini tushunish
- «Meni eslab qol» tokenlarining entropiyasi va oldindan aytib boʻlmasligini baholash
- Sezgir amallardan oldin shaxsni qayta tasdiqlashni talab qilish

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8061 |
| fixed (tuzatilgan) | http://127.0.0.1:8062 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** Brauzeringiz tili, masalan, rus tilida boʻlsa, `/ui` sahifasi avval ruscha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8061/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8061` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8061/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8062/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
PORT=8061 python vulnerable/app.py   # http://127.0.0.1:8061
```

> ⚠️ Ilova ataylab zaif qilingan. Uni faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq

Test akkauntlari: `alice` / `alice-Good-Pass1`, `bob` / `123456` (parol ataylab zaif: u roʻyxatdan oʻtishdan oʻtdi, chunki parol siyosati bunga yoʻl qoʻygan), `admin` / `Adm1n-Str0ng-Pass!2025` (parol ataylab mustahkam: bu akkauntni saralab ochib boʻlmaydi). Cookie'larni saqlab (`-c cookies.txt -b cookies.txt`) `curl` orqali ishlash qulay. `POST /reset-lab` laboratoriya maʼlumotlarini asl holatiga qaytaradi.

1. **«Meni eslab qol» tokeni.** `admin` parolini bilmasdan, faqat `remember_token` cookie'sidan foydalanib `GET /admin` ga (va bayroqqa) kiring.
2. **Session fixation.** Xuddi shu kirishni boshqa yoʻl bilan qoʻlga kiriting: `admin` nomidan kimdir kirishidan oldin qoʻlga kiritgan sid orqali.
3. **Logout.** Kiring, `sid` cookie qiymatini eslab qoling, chiqing — va shu qiymatdan hamon foydalanish mumkinligini koʻrsating.
4. **Sanab chiqish + saralash.** `POST /login` javobiga qarab qaysi loginlar umuman mavjudligini aniqlang, soʻng `bob` parolini hech qanday kechiktirish yoki bloklashsiz qisqa lugʻat bilan saralab toping.
5. **Akkauntni egallash.** Boshqa birovning har qanday faol sessiyasi boʻlsa (masalan, 1–3-bandlardan), qurbonning joriy parolini bilmasdan `POST /change-password` orqali uning parolini almashtiring.

## Endpointlar

```
POST /register           {"username","password"}
POST /login               {"username","password","remember":true|false}
POST /logout
GET  /auto-login          remember_token cookie orqali kirish
GET  /me
GET  /admin
POST /change-password     {"new_password"}   (fixed da yana "current_password")
POST /reset-lab
```

## Maslahatlar

<details>
<summary>1-maslahat — remember_token</summary>

`POST /login` da `"remember": true` boʻlsa, server `remember_token` cookie'sini oʻrnatadi. U nima bilan hisoblanadi: tasodifiy sir bilanmi yoki faqat loginni bilib oʻzingiz hisoblay oladigan narsa bilanmi?
</details>

<details>
<summary>2-maslahat — session fixation</summary>

`GET /` ni oching. Server sizga tizimga kirmasdan oldinoq `sid` cookie'sini beradi. Endi boshqa foydalanuvchi nomidan `POST /login` qilsangiz, aynan shu `sid` qiymatiga nima boʻladi?
</details>

<details>
<summary>3-maslahat — logout</summary>

`POST /logout` `{"ok": true}` javobini beradi va javobda cookie'larni ochiq oʻchiradi. Ammo brauzerda cookie'ni oʻchirish serverdagi sessiya yozuvini yoʻq qilish bilan bir narsa emas. `sid` qiymatini chiqishdan oldin alohida saqlab qoʻying va chiqqandan keyin ishlatib koʻring.
</details>

<details>
<summary>4-maslahat — sanab chiqish va saralash</summary>

Mavjud boʻlmagan login va mavjud login, ammo notoʻgʻri parol uchun `POST /login` javobining kodi va matnini solishtiring. Soʻng: server «yetar» deguncha `/login` ni necha marta ketma-ket chaqirish mumkin?
</details>

<details>
<summary>5-maslahat — parolni almashtirish</summary>

`POST /change-password` faqat faol sessiyani talab qiladi. Bu soʻrov umuman qaysi maydonlarni qabul qilishiga qarang: eski parol haqida biror narsa bormi?
</details>

## fixed/ da nimani solishtirish kerak

`fixed/app.py` ni oching va `# FIX N` izohlarini toping: har biri `vulnerable/app.py` dagi xuddi shu raqamli nuqsonga javob beradi.

## Tuzilishi
- `vulnerable/` — zaif versiya
- `fixed/` — tuzatilgan versiya
- `SOLUTION.uz.md` — yechim tahlili (spoylerlar bilan)
- `docker-compose.yml` — ikkala versiyani ishga tushirish

## Keyingi qadamlar
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) — V3 boʻlimi: Session Management, V2 boʻlimi: Authentication
- [OWASP Web Security Testing Guide — Testing for Authentication](https://owasp.org/www-project-web-security-testing-guide/)
