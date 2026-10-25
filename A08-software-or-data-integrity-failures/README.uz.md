🌐 [Русский](./README.md) · **Oʻzbekcha**

# A08 — Software or Data Integrity Failures (dasturiy taʼminot va maʼlumotlar yaxlitligining buzilishi)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Ilova haqiqiyligini hech kim tekshirmagan kod va maʼlumotlarni qabul qiladi: cookie dagi foydalanuvchi holati, «imzolangan» litsenziya, oynadan (mirror) kelgan yangilanish, toʻlov tizimi xabarnomasi va uchinchi tomon CDN dagi skript. Hujumchi bunday maʼlumotlarni «yoʻlda» yoki saqlash joyida oʻzgartira olsa, ilova uning irodasini bajaradi.

## Nimalarni oʻrganasiz
- Nazorat yigʻindisi (xesh) bilan haqiqiy imzoni (HMAC / asimmetrik imzo) farqlash
- Ishonchli holatni mijoz tomonida imzosiz saqlamaslik
- Yangilanishlar va bogʻliqliklar yaxlitligini tekshirish (lock-fayllar, qotirilgan xeshlar, imzolar)
- Webhook larning haqiqiyligini tekshirish: imzo, yangilik, takroriy yetkazish (replay)
- Uchinchi tomon skriptlarini SRI bilan ulash

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8071 |
| fixed (tuzatilgan) | http://127.0.0.1:8072 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** Brauzeringiz tili, masalan, rus tilida boʻlsa, `/ui` sahifasi avval ruscha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8071/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8071` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8071/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8072/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
PORT=8071 python vulnerable/app.py   # http://127.0.0.1:8071
```

> ⚠️ Ilova ataylab zaif qilingan. Uni faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
Test akkauntlari: `alice` / `alice123` (oddiy foydalanuvchi) va `admin` (parol kerak emas). `curl` (Windows'da — Git Bash/WSL yoki `curl.exe`) va qisqa Python skriptlari orqali ishlash qulay. `POST /reset-lab` laboratoriya maʼlumotlarini asl holatiga qaytaradi. `/mirror/publish` va `/cdn/compromise` endpointlari laboratoriya yordamchilari: ular yangilanishlar oynasiga va CDN ga kirish huquqini olgan hujumchini taqlid qiladi.

1. `alice` sifatida kiring va admin parolini **bilmasdan** `GET /admin` ga kirish huquqini oling.
2. `basic` tarifini sotib oling (`POST /buy`) va pro uchun **toʻlamasdan** `GET /pro` ga kirish huquqini oling.
3. Avtoyangilanish (`POST /system/run-update`) orqali sozlamalardagi `payout_account` ni hujumchi hisobiga almashtiring (bayroq `GET /settings` da chiqadi).
4. `1001` buyurtmani **toʻlamasdan** toʻlangan qiling (`GET /orders/1001` kalitni koʻrsatadi).
5. `GET /donate` ni brauzerda oching, soʻng `POST /cdn/compromise` qiling va sahifani qayta yuklang: qurbon endi qaysi rekvizitlarni koʻradi? fixed da nima oʻzgargan?

## Endpointlar

```
POST /login                  {"username","password"}
GET  /me
GET  /admin
POST /buy                    {"plan":"basic"}
GET  /pro
POST /system/run-update      cron taqlidi: oynadan avtoyangilanish
POST /mirror/publish         {"package","version","content":{}}   (yordamchi: oynani «buzish»)
GET  /settings
GET  /orders/<id>
POST /webhook/payment        {"order_id","status","amount"}
GET  /donate                 uchinchi tomon skripti bor HTML sahifa
POST /cdn/compromise         (yordamchi: CDN ni «buzish»)
POST /reset-lab
```

## Maslahatlar

<details>
<summary>1-maslahat — kirgandan keyingi cookie</summary>

Kiring va `a08v_profile` cookie'siga qarang. U base64 ga oʻxshaydimi? Uni dekodlab, bitta maydonni oʻzgartirib, qayta kodlasangiz nima chiqadi?
</details>

<details>
<summary>2-maslahat — litsenziya cookie'si</summary>

`a08v_license` cookie'sida nuqtadan keyin «imzo» bor. U nima bilan hisoblanadi? Buning uchun faqat server biladigan biror sir kerakmi?
</details>

<details>
<summary>3-maslahat — yangilanishlar oynasi</summary>

`/system/run-update` oynadan paketni qoʻllashdan oldin nimani tekshiradi? Paket umuman sozlamalarning qaysi maydonlarini oʻzgartirishga haqli?
</details>

<details>
<summary>4-maslahat — webhook</summary>

Toʻlov tizimidan boshqa kim `/webhook/payment` ga POST yubora oladi? Server haqiqiy xabarnomani soxtasidan qanday ajratadi?
</details>

<details>
<summary>5-maslahat — SRI</summary>

`/donate` sahifasining HTML ini vulnerable va fixed da solishtiring (sahifa manba kodi). `<script>` teglari nimasi bilan farq qiladi?
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
- [OWASP Cheat Sheet: Deserialization](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- [SLSA](https://slsa.dev/) va [Sigstore](https://www.sigstore.dev/) — artefaktlarni imzolash va kelib chiqishini tasdiqlash
- [MDN: Subresource Integrity](https://developer.mozilla.org/docs/Web/Security/Subresource_Integrity)
