🌐 [Русский](./README.md) · **Oʻzbekcha**

# A10 — Mishandling of Exceptional Conditions (istisno holatlarni notoʻgʻri qayta ishlash)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Har qanday ilova gohida buziladi: kutilmagan maʼlumotlar keladi, bogʻliqliklar ishdan chiqadi, resurslar tugaydi. Gap shundaki, u **qanday** buziladi. Bu yerda nosozlikka beshta notoʻgʻri javob bor: mijozga oʻzi haqida hamma narsani koʻrsatish, «har ehtimolga qarshi» ruxsat berish, amalni yarim yoʻlda tashlab ketish, soʻrovni hajmi boʻyicha cheklamaslik va istisno matnini ochib tashlash.

## Nimalarni oʻrganasiz
- Fail-closed (fail-secure) tamoyilini: tekshiruv ishdan chiqsa, kirish yopiladi
- Amallarni atomar qilishni: amalning «yarmi» oʻrniga tranzaksiya va orqaga qaytarish
- Mijozga `error_id` bilan neytral xato berishni, tafsilotlarni esa logda saqlashni
- Resurs ajratishdan oldin kiruvchi maʼlumotlarning hajmi va chegaralarini tekshirishni
- Kutilgan xatolarni (mohiyatan qayta ishlaymiz) kutilmagan xatolardan (yagona ishlovchi) farqlashni

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8091 |
| fixed (tuzatilgan) | http://127.0.0.1:8092 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** `/ui` sahifasi odatda inglizcha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8091/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8091` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8091/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8092/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
PORT=8091 python vulnerable/app.py   # http://127.0.0.1:8091
```

Brauzerda `/` barcha endpointlar uchun shakllari bor `/ui` sahifasini ochadi. Xuddi shuni `curl` orqali ham qilish mumkin (Windows'da — Git Bash/WSL yoki `curl.exe`).

> ⚠️ Ilova ataylab zaif qilingan. Uni faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
Test akkauntlari: `alice` / `alice123` (kirish darajasi 1) va `bob` / `bob123` (daraja 2). Ikkalasining boshlangʻich balansi 100. `POST /reset-lab` laboratoriya maʼlumotlarini asl holatiga qaytaradi va yiqilgan servisni «koʻtaradi». `GET /_lab/consistency` — laboratoriya yordamchisi: u yechib olingan pullar va buyurtmalarni solishtiradi.

1. `GET /report` da xatoni shunday chaqiringki, server kerakli darajadan koʻproq koʻrsatsin: javobda aynan nimani koʻryapsiz? (bayroq javobda)
2. `alice` sifatida kiring va unga huquq berilmagan `3` hujjatni oʻqing (bayroq mazmunida). `2` va `4` hujjatlar unga yopiq, `3` esa nima uchundir ochilib qoldi. Nima uchun?
3. Uchta krujka buyurtma qiling (`POST /orders`, `item_id: 1`, `qty: 3`). Balansingizga nima boʻladi? `GET /_lab/consistency` ni tekshiring (bayroq).
4. `POST /thumbnail` ga **bitta** soʻrov bilan servisni ishdan chiqaring, soʻng `GET /health` orqali ishonch hosil qiling (bayroq).
5. `GET /reports/q1`, `/reports/q2` va `/reports/archive` hisobotlarini oching. Xato matnlaridan server haqida nimalarni bilib oldingiz?
6. Hammasini `fixed` da (port 8092) takrorlang va javoblar hamda xatti-harakatni solishtiring. Server konsoliga qarab turing: u yerda javoblarda yoʻq tafsilotlar qoladi.

## Endpointlar

```
POST /login                  {"username","password"}
GET  /me
GET  /documents/<id>
GET  /report?month=<1-12>
GET  /items
POST /orders                 {"item_id","qty"}
POST /thumbnail              {"width","height"}
GET  /reports/<nom>
GET  /health
GET  /_lab/consistency       (yordamchi: yechib olingan pullar va buyurtmalarni solishtirish)
POST /reset-lab
```

## Maslahatlar

<details>
<summary>1-maslahat — xato javobida nima bor</summary>

`month` ga son boʻlmagan qiymat bering. Javobni toʻliq oʻqing: xatoning oʻzidan tashqari yana ikkita maydon bor. Ularda nima yotibdi va bu kimga qoʻl kelishi mumkin?
</details>

<details>
<summary>2-maslahat — «xususiyati» bor hujjat</summary>

Har bir hujjatda `level` maydoni bor. `2`, `3` va `4` hujjatlarni solishtiring: `3` hujjat qolganlardan nimasi bilan farq qiladi va kirish tekshiruvi qiymatlarni solishtira olmasa, nima qiladi?
</details>

<details>
<summary>3-maslahat — qadamlar tartibi</summary>

`POST /orders` qaysi tartibda pulni yechadi, omborni tekshiradi va buyurtma yaratadi? Birinchi va ikkinchi qadam orasida yiqilsa, bazada nima qoladi?
</details>

<details>
<summary>4-maslahat — soʻrov hajmi</summary>

Servisga 64 MB «mavjud», rasm uchun esa har bir piksel uchun 4 bayt kerak. Ilova xotira ajratishdan oldin `width` va `height` ning qaysi qiymatlarini tekshiradi?
</details>

<details>
<summary>5-maslahat — uchta hisobot, uchta xato</summary>

`q2` (fayl yoʻq) va `archive` (fayl oʻrnida katalog) uchun xato matnlarini solishtiring. Ularda umumiy nima va bu serverni oʻrganayotgan kishiga qanday foydali?
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
- [OWASP Cheat Sheet: Error Handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
- [OWASP: Improper Error Handling](https://owasp.org/www-community/Improper_Error_Handling)
- [CWE-636: Not Failing Securely («Failing Open»)](https://cwe.mitre.org/data/definitions/636.html)
