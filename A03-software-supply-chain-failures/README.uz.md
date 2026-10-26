🌐 [English](./README.md) · [Русский](./README.ru.md) · **Oʻzbekcha**

# A03 — Software Supply Chain Failures (dasturiy taʼminot yetkazib berish zanjiridagi nosozliklar)

**Holati:** ✅ tayyor

## Laboratoriya haqida

**Kestrel CI** — relizlarni yigʻish va yetkazish uchun oʻylab topilgan SaaS sayti: bosh sahifa, narxlar, hujjatlar, yigʻishlar sahifasi va paketlar reyestri. Interfeys **ingliz, rus va oʻzbek tillarida** ishlaydi (boshqaruv panelidagi EN / RU / UZ almashtirgichi). Laboratoriya ikki qismdan iborat:

1. **Ilova ichidagi butunlik.** Server yigʻish yuborgan narsaga ishonadi: artefakt xeshi qayta hisoblanmaydi, imzo tekshirilmaydi, yigʻish profili kod sifatida oʻqiladi, CI hodisasiga imzosiz ishoniladi, paket nomlari esa bir vaqtda ikki indeksdan hal qilinadi. Bu yerda flagli toʻrt nuqson bor.
2. **Bogʻliqliklar.** `vulnerable/requirements.txt` da ataylab maʼlum zaifliklarga ega eski versiyalar, jumladan tranzitiv paketlar qayd etilgan. `fixed/` da toʻgʻri yondashuv koʻrsatilgan: `requirements.in`, xeshlari bor lock-fayl va `--require-hashes` bilan oʻrnatish.

## Nimalarni oʻrganasiz

- Xeshni server tomonida mazmundan hisoblash va qatʼiy belgilangan qiymat bilan solishtirish
- Artefaktlarni imzolash (HMAC) va joylashtirishdan oldin imzoni tekshirish
- Maʼlumotlarni xavfsiz boʻlmagan deserializatorlar bilan (`pickle`) oʻqish mumkin emasligini va bu nima bilan tugashini tushunish
- Vebhuk imzosini tekshirish va imzosiz hodisalarni rad etish
- Bogʻliqliklar versiyalari **va xeshlarini** qotirish (lock-fayl) hamda nomlarni ommaviy indeksdan hal qilmaslik
- Bogʻliqliklarni maʼlum zaifliklarga tekshirish (`pip-audit`) va SBOM olish

## Sayt tuzilishi

| Sahifa | Manzil | Izoh |
|--------|--------|------|
| Bosh sahifa | `/` | Brauzerda sayt ochiladi; `curl` API haqida qisqa JSON oladi |
| Narxlar | `/pricing` | Uch reja va barcha rejalarga kirgan narsalar |
| Hujjatlar | `/docs` | Tez boshlash, `kestrel.yml` formati, imzo formulasi, endpointlar jadvali |
| Yigʻishlar | `/builds` | Artefakt xeshlari bilan ishga tushishlar, reliz, profil va vebhuk formalari |
| Paketlar reyestri | `/registry` | Ichki indeks va ommaviy oyna, paket oʻrnatish formasi |
| Laboratoriya konsoli | `/ui` | Endpointlar roʻyxati, tayyor soʻrovlar va javoblar |
| Paket versiyalari | `/deps` | Oʻrnatilgan bogʻliqliklar versiyalari (JSON) |

> 🌐 **Sayt tilini oʻzgartirish.** Almashtirgich sahifaning yuqori oʻng burchagida; tanlov cookie da eslab qolinadi. Xuddi shu natijani manzilga `?lang=uz` qoʻshib ham olish mumkin, masalan `http://127.0.0.1:8021/registry?lang=uz`. Laboratoriya konsoli uchun: `http://127.0.0.1:8021/ui?lang=uz`.

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (butunlik nuqsonlari + eski bogʻliqliklar) | http://127.0.0.1:8021 |
| fixed (tekshiruvlar joyida + xeshlar bilan yangilangan bogʻliqliklar) | http://127.0.0.1:8022 |

Ikki versiya ham bir xil saytni koʻrsatadi — faqat `app.py` farq qiladi. Brauzerda http://127.0.0.1:8021/ ni ochib, saytdan oddiy tashrif buyuruvchi sifatida foydalaning. Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

Relizlar va vebhuklar imzolanadigan laboratoriya kaliti — `kestrel-lab-project-key` (u `/docs` sahifasida ham koʻrsatilgan). Kalit ataylab kodda yotibdi: usiz tekshiradigan narsa boʻlmasdi.

> ⚠️ Ilova ataylab zaif. Faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq

### 1-qism. Ilova ichidagi butunlik

vulnerable versiyada **toʻrtta** butunlik xatosini toping (har birida flag yashiringan):

1. Artefakt mazmuniga mos kelmaydigan xesh bilan va umuman imzosiz reliz eʼlon qiling. Server uni qabul qildimi? Xeshni oʻzi qayta hisobladimi?
2. Yigʻish profiliga JSON emas, balki seriyalangan obyektning base64 blobini yuboring. Server profilning birinchi maydonini oʻqishidan **oldin** nima sodir boʻldi?
3. `/webhooks/ci` manziliga `X-Kestrel-Signature` sarlavhasisiz hodisa yuboring. Yigʻishga nima boʻldi va bu manzilni bilgan odam uchun bu nimani anglatadi?
4. `kestrel-utils` paketini avval versiyasiz, keyin `1.4.2` versiyasi bilan oʻrnating. Har bir holatda paket qaysi indeksdan keldi va uning xeshi lock-faylda qotirilgan xesh bilan solishtirildimi?

Toʻrt holatni ham tuzatilgan versiyada (8022-port) takrorlab koʻring va u yerda aynan nima oʻzgarganini ayting. Nuqsonlar `vulnerable/app.py` da `# ДЕФЕКТ N` izohlari bilan belgilangan.

### 2-qism. Bogʻliqliklar

1. Vositani oʻrnating: `pip install pip-audit`
2. Zaif versiyani tekshiring: `pip-audit -r vulnerable/requirements.txt`
3. Qaysi paketlar zaif ekanini va ularni qaysi versiyagacha yangilash kerakligini aniqlang. Ulardan qaysilarini loyihada siz **bevosita koʻrsatmagansiz**?
4. fixed versiyani xuddi shu buyruq bilan tekshiring: `pip-audit -r fixed/requirements.txt`
5. `fixed/requirements.in` va `fixed/requirements.txt` ni oching. Ular nimasi bilan farq qiladi va xeshlar nega kerak?
6. Tajriba: `fixed/requirements.txt` ni nusxalang, istalgan xeshni nollarga almashtiring va `pip install --require-hashes -r <fayl>` ni sinab koʻring. Nima sodir boʻladi?

## Maslahatlar

1. Barcha soʻrovlar uchun formalar `/builds` va `/registry` sahifalarida bor, shuning uchun ishning bir qismini brauzerda bajarish mumkin. curl uchun JSON qulayroq: `curl -X POST http://127.0.0.1:8021/api/releases -H 'Content-Type: application/json' -d '{...}'`.
2. Reliz imzosi — xesh satrining loyiha kaliti bilan olingan HMAC-SHA256 qiymati. Python misoli `/docs` sahifasida.
3. Yigʻish profili `pickle` oʻqiy oladigan narsaning base64 koʻrinishida yuboriladi. Keyingi natija obyekt ichida nima borligiga bogʻliq.
4. `/registry` sahifasidagi «Ommaviy oyna» jadvali qaysi paketlar tashqi indeksdan kelishini koʻrsatadi. Xeshlarga eʼtibor bering: ular ichki xeshlardan farq qiladi.
5. `pip-audit` paket nomini, versiyasini, bildirishnoma raqamini va muammo tuzatilgan versiyani chiqaradi.
6. `requests` oʻzi bilan `urllib3`, `idna` va `certifi` ni olib keladi, `Flask` esa `Werkzeug` va `Jinja2` ni.

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish

- Xeshni server tomonida mazmundan hisoblab, qotirilgan qiymat bilan solishtirish; relizlarni imzolash va chiqarishdan oldin imzoni tekshirish
- Kiruvchi maʼlumotlarni hech qachon xavfsiz boʻlmagan deserializatorlar bilan oʻqimaslik (`pickle`, `marshal`, `yaml.load`): faqat JSON, sxemalar va validatsiya
- Vebhuklardan imzo talab qilish va uni constant-time solishtirish; imzosiz hodisalarni rad etish
- Paket nomlarini faqat ichki indeksdan hal qilish, versiya **va xeshlarni** lock-faylda qotirish, tashqi indeksni teng huquqli manba deb hisoblamaslik
- Bogʻliqliklarni muntazam tekshirish (`pip-audit`, Dependabot va shunga oʻxshashlar), yangilab turish va SBOM yuritish
