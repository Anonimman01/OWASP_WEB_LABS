🌐 [Русский](./README.md) · **Oʻzbekcha**

# A03 — Software Supply Chain Failures (dasturiy taʼminot yetkazib berish zanjiridagi nosozliklar)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Ilovaning oʻzi zararsiz: u faqat oʻrnatilgan paketlar versiyalarini koʻrsatadi. Muammo uning **bogʻliqliklarida**: `vulnerable/requirements.txt` da ataylab maʼlum zaifliklarga ega eski versiyalar qayd etilgan, jumladan tranzitiv bogʻliqliklar (`requests` va `Flask` bilan birga keladigan paketlar).

## Nimalarni oʻrganasiz
- Bogʻliqliklarni maʼlum zaifliklarga tekshirish (`pip-audit`)
- Tranzitiv bogʻliqliklar nima ekanini va ularni ham nega tekshirish kerakligini tushunish
- Paketlar versiyalarini va **xeshlarini** qotirish (lock-fayl) hamda ularni `--require-hashes` bilan oʻrnatish
- Loyihaning SBOM ini (komponentlar roʻyxati) olish

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (eski bogʻliqliklar) | http://127.0.0.1:8021 |
| fixed (yangilangan + xeshlar) | http://127.0.0.1:8022 |

`GET /deps` endpointi oʻrnatilgan paketlar versiyalarini koʻrsatadi.

> ⚠️ Ataylab eskirgan bogʻliqliklarga ega ilova. Faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
1. Vositani oʻrnating: `pip install pip-audit`
2. Zaif versiyani tekshiring: `pip-audit -r vulnerable/requirements.txt`
3. Qaysi paketlar zaif ekanini va ularni qaysi versiyagacha yangilash kerakligini aniqlang. Ulardan qaysilarini loyihada siz **bevosita koʻrsatmagansiz**?
4. fixed versiyani xuddi shu buyruq bilan tekshiring: `pip-audit -r fixed/requirements.txt`
5. `fixed/requirements.in` va `fixed/requirements.txt` ni oching. Ular nimasi bilan farq qiladi va xeshlar nega kerak?
6. Tajriba: `fixed/requirements.txt` ni nusxalang, istalgan xeshni nollarga almashtiring va `pip install --require-hashes -r <fayl>` ni sinab koʻring. Nima sodir boʻladi?

## Maslahatlar
1. `pip-audit` paket nomini, versiyasini, bildirishnoma raqamini va muammo tuzatilgan versiyani chiqaradi.
2. `requests` oʻzi bilan `urllib3`, `idna` va `certifi` ni olib keladi, `Flask` esa `Werkzeug` va `Jinja2` ni.
3. Bunday loyihalarda versiyalar tez eskiradi: yangi bildirishnomalar doimo chiqib turadi, tekshiruvni takrorlab turish kerak.

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- Bogʻliqliklarni muntazam tekshirish (`pip-audit`, Dependabot, shunga oʻxshashlar) va yangilab turish
- Xeshlari bor lock-faylni saqlash va `--require-hashes` bilan oʻrnatish
- Mahsulot nimalardan tashkil topganini bilish uchun SBOM yuritish
- Paketlarni faqat ishonchli manbalardan olish va nomlarga eʼtibor berish (paket nomidagi xatolar va ichki paketlarni ommaviy paketlar bilan almashtirish)
