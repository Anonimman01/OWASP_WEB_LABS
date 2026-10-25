🌐 [Русский](./README.md) · **Oʻzbekcha**

# A02 — Security Misconfiguration (xavfsiz boʻlmagan konfiguratsiya)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Tipik konfiguratsiya xatolari bor kichik internet-doʻkon (API): sukut boʻyicha parol, ortiqcha ochiq fayllar, batafsil xatolar va himoya sarlavhalarining yoʻqligi. Bu yerda ekspluatatsiya kodi yoʻq: zaifliklar aynan **notoʻgʻri sozlamalardir**.

## Nimalarni oʻrganasiz
- Ilovadagi xavfsiz boʻlmagan sozlamalarni topish
- Batafsil xatolar va unutilgan fayllar (`.env`, zaxira nusxalar) nega xavfli ekanini tushunish
- HTTP himoya sarlavhalarini sozlash va tashqariga faqat keraklisini berish

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8011 |
| fixed (tuzatilgan) | http://127.0.0.1:8012 |

> 🌐 **Interfeysni oʻzbek tilida ochish.** Brauzeringiz tili, masalan, rus tilida boʻlsa, `/ui` sahifasi avval ruscha ochiladi. Oʻzbekchaga oʻtish uchun laboratoriya ochilgan brauzer oynasiga oʻting va manzil qatorining oxiriga quyidagini yozing:
>
> - manzil `http://127.0.0.1:8011/ui` boʻlsa (odatda shunday: brauzer `/` dan `/ui` ga oʻzi yoʻnaltiradi), oxiriga `?lang=uz` qoʻshing;
> - manzil `http://127.0.0.1:8011` boʻlsa, oxiriga `/ui?lang=uz` qoʻshing.
>
> Natija: `http://127.0.0.1:8011/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8012/ui?lang=uz` (fixed). Soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ Ilova ataylab zaif qilingan. Faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
vulnerable versiyada **toʻrtta** konfiguratsiya xatosini toping (har birida flag yoki belgi yashirilgan):

1. Parolni bilmasdan administrator sifatida kiring.
2. Serverga kirish huquqisiz ilovaning maxfiy maʼlumotlarini oling.
3. Ilovani ortiqcha texnik maʼlumot chiqarishga majburlang.
4. Javobning HTTP sarlavhalarini tekshiring: qaysi himoya sarlavhalari yetishmaydi va server nimani ortiqcha oshkor qiladi?

Keyin tekshiruvlarni fixed versiyada takrorlang. fixed da admin paroli ishga tushganda generatsiya qilinadi: `docker compose logs fixed` (yoki `ADMIN_PASSWORD` oʻzgaruvchisi orqali oʻzingiznikini bering).

## Maslahatlar
1. Qanday login va parollar koʻpincha «sukut boʻyicha» qolib ketadi?
2. `GET /files/<nom>` marshruti nima qiladi va `app.py` yonida qanday fayllar yotibdi?
3. `GET /items?id=abc` nima qaytaradi?
4. Sarlavhalarni koʻrish uchun `curl -i` dan foydalaning.

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- Sukut boʻyicha parollarni almashtirish, sirlarni kod yonidagi fayllarda emas, muhit oʻzgaruvchilarida saqlash
- Tashqariga ilovaning ildizini emas, faqat statik fayllar papkasini berish
- Foydalanuvchiga neytral xato koʻrsatish, tafsilotlarni server logiga yozish
- Himoya sarlavhalarini qoʻshish va versiyalar haqidagi ortiqcha bannerlarni olib tashlash
- Konfiguratsiyani avtomatik skanerlar bilan muntazam tekshirib turish
