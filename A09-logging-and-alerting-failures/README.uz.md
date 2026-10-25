🌐 [Русский](./README.md) · **Oʻzbekcha**

# A09 — Security Logging and Alerting Failures (jurnal yuritish va ogohlantirish nosozliklari)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Xavfsizlik hodisalari logga yozilmasa, ular boʻyicha ogohlantirishlar boʻlmasa yoki logning oʻzi ishonchsiz boʻlsa, hujum juda kech payqaladi: uni soxtalashtirish, begona kishi oʻqishi mumkin, ichida esa parollar va sessiyalar yotadi. Laboratoriyada bitta kichik ilovada shunday oltita nuqson bor.

## Nimalarni oʻrganasiz
- Nimalarni loglash kerak: kirishlar (muvaffaqiyatli va muvaffaqiyatsiz), kirishdan rad etishlar, muhim amallar
- Log injection ga yoʻl qoʻymaslik va logga sirlarni yozmaslik
- Ogohlantirishlarni qanday qurish: hisoblagichlar, chegaralar, vaqt oynasi
- Logning oʻzini qanday himoyalash: kirish huquqi, audit, almashtirilganini aniqlash uchun xeshlar zanjiri

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8081 |
| fixed (tuzatilgan) | http://127.0.0.1:8082 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** Brauzeringiz tili, masalan, rus tilida boʻlsa, `/ui` sahifasi avval ruscha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8081/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8081` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8081/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8082/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
PORT=8081 python vulnerable/app.py   # http://127.0.0.1:8081
```

Brauzerda `/` barcha endpointlar uchun shakllari bor `/ui` sahifasini ochadi. Xuddi shuni `curl` orqali ham qilish mumkin (Windows'da — Git Bash/WSL yoki `curl.exe`).

> ⚠️ Ilova ataylab zaif qilingan. Uni faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
Test akkauntlari: `alice` / `alice123` va `bob` / `bob123` (oddiy foydalanuvchilar), `admin` (parol kerak emas). `POST /reset-lab` laboratoriya maʼlumotlarini asl holatiga qaytaradi. `/_lab/tamper` endpointi — laboratoriya yordamchisi: u log saqlash joyiga kirish huquqi bor hujumchini taqlid qiladi.

1. `bob` parolini saralang: kamida 10 ta muvaffaqiyatsiz kirish qiling, soʻng toʻgʻri kiring. `GET /logs` da saralash izlarini toping. Soʻng `GET /alerts` ni oching (hujumni hech kim payqamagan boʻlsa, bayroq chiqadi).
2. `alice` sifatida kiring va `GET /admin/export` ga murojaat qiling (403 boʻladi). Rad etish logda qoldimi?
3. `POST /feedback` orqali logda aslida boʻlmagan foydalanuvchining kirishi haqidagi yozuvni soxtalashtiring. Natijani `GET /logs/summary` da tekshiring (bayroq).
4. Parolni saralamasdan va ilovani buzmasdan administrator huquqini oling: allaqachon oʻqiy olishingizning oʻzi yetarli (bayroq `GET /admin/export` da).
5. `POST /transfer` orqali oʻtkazma qiling va logdan u haqida yozuv qidiring.
6. `POST /_lab/tamper` orqali logdan oʻz kirishingiz yozilgan qatorni oʻchiring. Ilovada buni payqashning biror yoʻli bormi?
7. Hammasini `fixed` da (port 8082) takrorlang. U yerda siz ham hujumchi, ham himoyachisiz: loglar va ogohlantirishlarni faqat administrator oʻqiydi, shuning uchun `admin` sifatida kiring (parolni `fixed/app.py` dan oling) va `GET /alerts`, `GET /logs` va `GET /logs/verify` ga qarang.

## Endpointlar

```
POST /login                  {"username","password"}
GET  /me
POST /transfer               {"to","amount"}
POST /feedback               {"name","message"}
GET  /admin/export
GET  /logs
GET  /logs/summary           (fixed: faqat admin)
GET  /logs/verify            (faqat fixed: xeshlar zanjirini tekshirish)
GET  /alerts
POST /_lab/tamper            {"index","text"}   yordamchi: log saqlash joyini tahrirlash
POST /reset-lab
```

## Maslahatlar

<details>
<summary>1-maslahat — logda nima koʻrinadi</summary>

Bir necha marta kiring, jumladan notoʻgʻri ham, soʻng `GET /logs` ni oching. Nechta qator paydo boʻldi? Ularda qaysi hodisalar bor, qaysilari yoʻq?
</details>

<details>
<summary>2-maslahat — qator oʻtkazish</summary>

Log — oddiy matn, har bir qatorda bitta yozuv. `message` ga qator oʻtkazish belgisi (JSON da `\n`) tushsa, nima boʻladi?
</details>

<details>
<summary>3-maslahat — logda yana nima yotibdi</summary>

Administrator kirishi haqidagi qatorlarni diqqat bilan oʻqing. Ularda hammasini saqlash kerakmi?
</details>

<details>
<summary>4-maslahat — ogohlantirishlarga kim qaraydi</summary>

Ilovada saralash haqida kimdir bilib qoladigan chegara qayerda? vulnerable va fixed dagi `GET /alerts` ni solishtiring.
</details>

<details>
<summary>5-maslahat — logga ishonish mumkinmi</summary>

Hujumchi qatorni oʻchirgan boʻlsa, buni nimaga qarab bilish mumkin? fixed da har bir yozuv nimani saqlashiga va `GET /logs/verify` nima qilishiga qarang.
</details>

## fixed/ da nimani solishtirish kerak
`fixed/app.py` ni oching va `# FIX N` izohlarini toping: raqam `vulnerable/app.py` dagi nuqson raqamiga mos keladi.

## Tuzilishi
- `vulnerable/` — zaif versiya
- `fixed/` — tuzatilgan versiya
- `SOLUTION.uz.md` — yechim tahlili (spoylerlar bilan)
- `docker-compose.yml` — ikkala versiyani ishga tushirish

## Keyingi qadamlar
- [OWASP Top 10:2025](https://owasp.org/Top10/)
- [OWASP Cheat Sheet: Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [OWASP: Log Injection](https://owasp.org/www-community/attacks/Log_Injection)
- [OWASP Cheat Sheet: Application Logging Vocabulary](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Vocabulary_Cheat_Sheet.html)
