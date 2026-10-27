🌐 [English](./README.md) · [Русский](./README.ru.md) · **Oʻzbekcha**

# OWASP Top 10:2025 — oʻquv laboratoriyalari

Har bir **[OWASP Top 10:2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)** toifasi uchun bittadan, jami oʻnta lokal laboratoriya ishi.
Format «**buz → tuzat**»: har bir laboratoriyada bir ilovaning ikki versiyasi, zaif va tuzatilgani, bir vaqtda ishga tushadi. Siz birinchisidagi nuqsonlarni topasiz, keyin uni tuzatilgani bilan solishtirib, har bir teshik aynan nima bilan yopilganini koʻrasiz.

Barcha laboratoriyalar (A01–A10) hujjatlari inglizcha, ruscha va oʻzbekcha (lotin alifbosida) mavjud. Shu README ham uch tilda. Litsenziya: MIT.

> ⚠️ **Muhim.** Ushbu repozitoriydagi ilovalar **ataylab zaif qilingan**.
> - Ularni faqat lokal (`127.0.0.1`) yoki izolyatsiyalangan muhitda (Docker, virtual mashina) ishga tushiring.
> - **Ularni hech qachon internetga chiqarmang.** `docker-compose.yml` dagi portlar aynan shu maqsadda `127.0.0.1` ga bogʻlangan.
> - Olingan bilimlarni faqat oʻz tizimlaringizda yoki sinab koʻrish uchun aniq ruxsat olgan tizimlarda qoʻllang.
> - Laboratoriyalardagi barcha maʼlumotlar xayoliy: foydalanuvchilar, parollar, karta raqamlari va sirlar.

## Mundarija

- [Laboratoriyalar jadvali](#laboratoriyalar-jadvali)
- [Tez boshlash](#tez-boshlash)
- [Interfeys tili (UZ)](#interfeys-tili-uz)
- [Laboratoriyani qanday bajarish](#laboratoriyani-qanday-bajarish)
- [Har bir laboratoriya tuzilishi](#har-bir-laboratoriya-tuzilishi)
- [Umumiy kelishuvlar](#umumiy-kelishuvlar)
- [Tillar](#tillar)
- [Yechimlar va spoylerlar](#yechimlar-va-spoylerlar)
- [Muammolarni hal qilish](#muammolarni-hal-qilish)
- [Testlar va Makefile](#testlar-va-makefile)
- [Foydali havolalar](#foydali-havolalar)

## Laboratoriyalar jadvali

Portlar **vulnerable / fixed** tartibida koʻrsatilgan. Barcha manzillar `http://127.0.0.1:<port>` koʻrinishida.
Havolalar laboratoriyalarning oʻzbekcha README fayllariga olib boradi.

| №   | Laboratoriya | Toifa | Ichida nima | Portlar |
|-----|--------------|-------|-------------|---------|
| A01 | [broken-access-control](./A01-broken-access-control/README.uz.md) | Kirish nazoratining buzilishi | Rollari bor HR-portal: server resurs kimga tegishli ekanini va foydalanuvchi roli qanday ekanini tekshirmaydi | 8001 / 8002 |
| A02 | [security-misconfiguration](./A02-security-misconfiguration/README.uz.md) | Xavfsiz boʻlmagan konfiguratsiya | Kafe sayti (Flask): sukut boʻyicha parol, ortiqcha ochiq fayllar, batafsil xatolar, himoya sarlavhalari yoʻq | 8011 / 8012 |
| A03 | [software-supply-chain-failures](./A03-software-supply-chain-failures/README.uz.md) | Dasturiy taʼminot yetkazib berish zanjiridagi nosozliklar | «Kestrel CI» SaaS sayti (Flask): xesh va imzo tekshirilmaydi, yigʻish profilida pickle, imzosiz vebhuk, ichki paketni ommaviy paket bilan almashtirish | 8021 / 8022 |
| A04 | [cryptographic-failures](./A04-cryptographic-failures/README.uz.md) | Kriptografik nosozliklar | Akkauntlar va bank kartalari: zaif kriptografiya, administrator akkauntini egallash | 8031 / 8032 |
| A05 | [injection](./A05-injection/README.uz.md) | Inyeksiyalar (SQLi, XSS va boshq.) | Kirish, qidiruv va mehmonlar kitobi bor doʻkon; kiritilgan maʼlumot SQL va HTML ga ishlovsiz tushadi | 8041 / 8042 |
| A06 | [insecure-design](./A06-insecure-design/README.uz.md) | Xavfsiz boʻlmagan arxitektura | Kodi toza, ammo biznes-mantiqi buzilgan doʻkon JSON API si | 8051 / 8052 |
| A07 | [authentication-failures](./A07-authentication-failures/README.uz.md) | Autentifikatsiya nosozliklari | Roʻyxatdan oʻtish, kirish, «meni eslab qol», parolni almashtirish | 8061 / 8062 |
| A08 | [software-or-data-integrity-failures](./A08-software-or-data-integrity-failures/README.uz.md) | Dasturiy taʼminot va maʼlumotlar yaxlitligining buzilishi | Imzolanmagan cookie, litsenziya, oynadan yangilash va webhook | 8071 / 8072 |
| A09 | [logging-and-alerting-failures](./A09-logging-and-alerting-failures/README.uz.md) | Jurnal yuritish va ogohlantirish nosozliklari | Hujum logda koʻrinmaydi: yozuvlar yoʻq, log injection, logda sirlar, ogohlantirishlar yoʻq | 8081 / 8082 |
| A10 | [mishandling-of-exceptional-conditions](./A10-mishandling-of-exceptional-conditions/README.uz.md) | Istisno holatlarni notoʻgʻri qayta ishlash | Batafsil xatolar, fail-open, orqaga qaytarilmaydigan amallar, cheklovlarning yoʻqligi | 8091 / 8092 |

Holati: ✅ barcha oʻnta laboratoriya tayyor.

## Tez boshlash

### Nima kerak

- Git
- Docker va Compose plagini **yoki** Python 3.11+ (Docker'siz)
- `curl` buyruqlari uchun: Windows'da Git Bash, WSL yoki `curl.exe` dan foydalaning. PowerShell'da `curl` boshqa buyruqning taxallusi, shuning uchun laboratoriyalardagi misollar unda oʻz holicha ishlamaydi.

### Docker orqali ishga tushirish

Bash / Git Bash / WSL:

```bash
git clone https://github.com/Anonimman01/my-labs.git
cd my-labs/A01-broken-access-control
docker compose up --build
```

PowerShell:

```powershell
git clone https://github.com/Anonimman01/my-labs.git
cd my-labs\A01-broken-access-control
docker compose up --build
```

Ikkala versiya (zaif va tuzatilgan) yuqoridagi jadvaldagi portlarda bir vaqtda koʻtariladi. Toʻxtatish: `Ctrl+C`, keyin `docker compose down`.

### Docker'siz ishga tushirish

Python 3.11+ kerak. Virtual muhitdan foydalangan maʼqul. Port `PORT` oʻzgaruvchisi bilan beriladi (sukut boʻyicha `5000`).

Bash / Git Bash / WSL:

```bash
cd my-labs/A09-logging-and-alerting-failures
python -m venv .venv && source .venv/bin/activate
pip install -r vulnerable/requirements.txt
PORT=8081 python vulnerable/app.py     # http://127.0.0.1:8081
```

PowerShell:

```powershell
cd my-labs\A09-logging-and-alerting-failures
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r vulnerable\requirements.txt
$env:PORT = 8081
python vulnerable\app.py               # http://127.0.0.1:8081
```

Tuzatilgan versiyani ishga tushirish uchun `vulnerable` ni `fixed` ga (portni esa `8082` ga) almashtiring. Versiyalarning bogʻliqliklari farq qilishi mumkin, shuning uchun aynan ishga tushirayotgan versiyangizning `requirements.txt` ini oʻrnating. A03 da bu Flask ning turli versiyalari: `vulnerable/` da u ataylab eskirgan.

## Interfeys tili (UZ)

**Interfeysni oʻzbek tilida ochish.** Barcha laboratoriyalarda brauzer sahifasi (`/ui`) uch tilli: ingliz, rus va oʻzbek. Sahifa odatda inglizcha ochiladi. Oʻzbekchaga oʻtish uchun:

1. Laboratoriya ochilgan brauzer oynasiga oʻting.
2. Manzil qatorining oxiriga quyidagini yozing:
   - manzil `http://127.0.0.1:8041/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
   - manzil `http://127.0.0.1:8041` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
3. Enter bosing. Natija, masalan: `http://127.0.0.1:8041/ui?lang=uz`.

Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing (yonida **EN** va **RU** tugmalari ham bor). Tanlov brauzerda eslab qolinadi va keyingi laboratoriyalar ham oʻzbekcha ochiladi. Brauzeringiz tili oʻzbekcha boʻlsa, sahifa darhol oʻzbekcha ochiladi.

Har bir laboratoriyaning portlari yuqoridagi jadvalda. Masalan, A01 uchun: `http://127.0.0.1:8001/ui?lang=uz` (vulnerable) va `http://127.0.0.1:8002/ui?lang=uz` (fixed).

## Laboratoriyani qanday bajarish

1. Kerakli laboratoriyaning `README.uz.md` (yoki inglizcha `README.md`, ruscha `README.ru.md`) faylini oching va u nima haqida ekanini hamda test akkauntlarini oʻqing.
2. Laboratoriyani ishga tushiring va `vulnerable` manzilini oching. Brauzerda `/` barcha endpointlar uchun shakllari bor `/ui` sahifasiga yoʻnaltiradi; A01 va A02 da bunday oʻrniga ilovaning oʻzi ochiladi (portal va kafe sayti), `/ui` konsoliga esa uning sahifalarida havola bor. Xuddi shu soʻrovlarni `curl` yoki Postman orqali ham yuborish mumkin.
3. «Topshiriq» boʻlimidagi bandlarni bajaring. Qiynalsangiz, maslahatlarni oching.
4. `vulnerable/app.py` da nuqsonlar `# ДЕФЕКТ N` izohlari bilan belgilangan. Ularni toping va buzilgan qoidani shakllantiring.
5. `fixed/app.py` ni oching: tuzatishlar `# FIX N` bilan belgilangan, raqam nuqson raqamiga mos keladi. Xuddi shu soʻrovlarni `fixed` da takrorlang va hujum endi ishlamasligiga, oddiy stsenariylar esa ishlashiga ishonch hosil qiling.
6. Faqat shundan keyin `SOLUTION.uz.md` (yoki `SOLUTION.md`) ni oʻqing.

## Har bir laboratoriya tuzilishi

```
AXX-toifa-nomi/
  README.md              tavsif, topshiriq, endpointlar, maslahatlar (inglizcha)
  README.ru.md           ruscha tarjima
  README.uz.md           oʻzbekcha tarjima
  SOLUTION.md            yechim tahlili (spoylerlar bilan, inglizcha)
  SOLUTION.ru.md         ruscha tarjima
  SOLUTION.uz.md         oʻzbekcha tarjima
  Dockerfile             python:3.11-slim, ARG VARIANT, ENV HOST=0.0.0.0 PORT=5000
  docker-compose.yml     ikkita servis (vulnerable va fixed), 127.0.0.1 dagi portlar
  vulnerable/
    app.py               zaif versiya
    labui.py             oʻquv interfeysi /ui
    requirements.txt
  fixed/
    app.py               tuzatilgan versiya
    labui.py
    requirements.txt
```

Ayrim laboratoriyalarda qoʻshimcha fayllar bor: masalan, A04 da `wordlist.txt`, A02 ning `vulnerable/` papkasida `backup.sql`, A03 ning `fixed/` papkasida `requirements.in`. A02 da saytning oʻz fayllari ham bor: har bir versiyada `templates/`, `static/` va `cafe.py`.

## Umumiy kelishuvlar

- **Stek.** Flask, odatda JSON API. Manzil va port `HOST` va `PORT` muhit oʻzgaruvchilaridan olinadi (sukut boʻyicha `127.0.0.1:5000`).
- **`/ui` sahifasi.** Oʻquv qobigʻi, zaiflikning qismi emas. Flask marshrutlari roʻyxati boʻyicha quriladi, shuning uchun ikkala versiyada bir xil. Brauzerda u oʻrniga JSON koʻrinsa, `/ui` ni qoʻlda oching.
- **Flaglar.** `vulnerable` javoblarida `FLAG{aNN_...}` koʻrinishidagi qatorlar uchraydi. Bu nuqson topilgani va ekspluatatsiya qilinganining tasdigʻi.
- **Holatni tiklash.** A06–A10 laboratoriyalarida maʼlumotlarni dastlabki holatga qaytaradigan `POST /reset-lab` bor. Boshqa laboratoriyalarda holat ilovani qayta ishga tushirish bilan tiklanadi.
- **Yordamchi endpointlar.** Hujumchi yoki tashqi tizim harakatlarini imitatsiya qiladigan marshrutlar (masalan, A08 dagi yangilanishlar oynasi) kodda laboratoriya yordamchilari sifatida belgilangan va zaiflikning qismi emas.
- **Cookie.** `vulnerable` va `fixed` da cookie nomlari har xil, chunki `127.0.0.1` dagi turli portlar brauzerda bitta cookie toʻplamini baham koʻradi.
- **Parollar.** Soddalik uchun ochiq matnda saqlanadi. Parollarni toʻgʻri saqlashni A04 laboratoriyasi tahlil qiladi.
- **Jangovar ekspluatlar yoʻq.** Laboratoriyalar nuqsonni xavfsiz misolda koʻrsatadi, deserializatsiya orqali RCE kabi tayyor ekspluatatsiyasiz.

## Tillar

Barcha laboratoriyalar (A01–A10) hujjatlari uch tilda mavjud: inglizcha (`README.md`, `SOLUTION.md`), ruscha (`README.ru.md`, `SOLUTION.ru.md`) va oʻzbekcha, lotin alifbosida (`README.uz.md`, `SOLUTION.uz.md`). Ildiz README esa uch tilda: inglizcha (`README.md`), ruscha (`README.ru.md`) va oʻzbekcha (`README.uz.md`). Har bir fayl tepasida tilni almashtirish havolasi bor.

Barcha laboratoriyalarda `/ui` sahifasi ham uch tilli (inglizcha, ruscha, oʻzbekcha), oʻtish usuli [yuqorida](#interfeys-tili-uz) tushuntirilgan. Faqat qobiq tarjima qilinadi (sarlavhalar, tugmalar, maslahatlar, namunalar). Ilovalarning oʻz javoblari (qaydlar matni, mahsulot nomlari, xato xabarlari) `SOLUTION` ga mos kelishi uchun oʻzgarishsiz qoladi. Koddagi izohlar (`# ДЕФЕКТ N` / `# FIX N`) rus tilida qoladi.

## Yechimlar va spoylerlar

Har bir laboratoriyadagi `SOLUTION.uz.md` (yoki `SOLUTION.md`) har bir nuqson uchun buyruqlarni, buzilgan qoidani va tuzatish tavsifini, oxirida esa xulosani oʻz ichiga oladi. Uni oʻzingiz urinib koʻrganingizdan keyin oʻqing.

## Muammolarni hal qilish

- **Port band.** Boshqa laboratoriyani toʻxtating yoki `docker-compose.yml` da chap tomondagi portni oʻzgartiring (masalan, `127.0.0.1:9001:5000`). Docker'siz boʻlsa, `PORT` ga boshqa qiymat bering.
- **Cookie laboratoriyalar orasida «yopishib qoldi».** Sahifani inkognito rejimida oching yoki `127.0.0.1` uchun cookie larni tozalang.
- **PowerShell'da `curl` gʻalati ishlayapti.** `curl.exe`, Git Bash yoki WSL dan foydalaning.
- **Docker ishga tushmayapti.** Docker Desktop ishlayotganini va `docker compose` buyrugʻi (faqat `docker-compose` emas) mavjudligini tekshiring.
- **Sahifa oʻzbekcha ochilmayapti.** `git pull` qiling (laboratoriya papkasida `README.uz.md` boʻlishi kerak) va Docker obrazini `docker compose up --build` bilan qayta yigʻing.

## Testlar va Makefile

[#testlar-va-makefile](#testlar-va-makefile)

`tests/` papkasida avtomatik eksploit-testlar bor: `SOLUTION.md` dagi har bir hujum **`vulnerable` da ishlashi** va **`fixed` da ishlamasligi** kerak, oddiy stsenariylar esa ikkala versiyada ham ishlashi kerak. Testlar CI da har bir push va pull request da ishga tushadi, shuning uchun laboratoriyani yoki uning tuzatishini buzadigan o‘zgarish darhol sezilib qoladi. Hozircha A05 qamrab olingan (qolganlarini namuna bo‘yicha qo‘shing: `tests/test_a05_injection.py` ni nusxalab moslashtiring).

```
pip install -r requirements-dev.txt
make test          # yoki: python -m pytest
```

`make` buyruqlari (Linux, macOS, WSL, Git Bash): `make up LAB=A05` bitta laboratoriyani ishga tushiradi, `make down LAB=A05` to‘xtatadi, `make up-all` / `make down-all` barcha o‘nta laboratoriya bilan ishlaydi, `make check` repozitoriy tekshiruvlarini bajaradi. `make help` to‘liq ro‘yxatni ko‘rsatadi.

## Foydali havolalar

- [OWASP Top 10:2025](https://owasp.org/Top10/2025/0x00_2025-Introduction/)
- Chuqurroq oʻrganish uchun [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) va [Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

## Litsenziya

[MIT](./LICENSE)
