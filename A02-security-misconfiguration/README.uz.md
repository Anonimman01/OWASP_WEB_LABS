🌐 [English](./README.md) · [Русский](./README.ru.md) · **Oʻzbekcha**

# A02 — Security Misconfiguration (xavfsiz boʻlmagan konfiguratsiya)

**Holati:** ✅ tayyor

## Laboratoriya haqida
Flask qurilgan **Lumière Café** sayti: landing sahifa, taomlar menyusi va ularning sahifalari, xodimlar uchun kirish. Interfeys **ingliz, rus va oʻzbek** tillarida: EN / RU / UZ almashtirgichi sayt boshqaruv panelida, tanlov cookie da saqlanadi va `?lang=en|ru|uz` bilan ham berilishi mumkin. U kichik biznesning oddiy sayti kabi koʻrinadi va ishlaydi, lekin tipik konfiguratsiya xatolari bilan ishga tushirilgan: sukut boʻyicha parol, ortiqcha ochiq fayllar, batafsil xatolar va himoya sarlavhalarining yoʻqligi. Bu yerda ekspluatatsiya kodi yoʻq: zaifliklar aynan **notoʻgʻri sozlamalardir**.

## Nimalarni oʻrganasiz
- Ilovadagi xavfsiz boʻlmagan sozlamalarni topish
- Batafsil xatolar va unutilgan fayllar (`.env`, zaxira nusxalar) nega xavfli ekanini tushunish
- HTTP himoya sarlavhalarini sozlash va tashqariga faqat keraklisini berish

## Sayt tuzilishi

| Sahifa | Manzil | Izoh |
|--------|--------|------|
| Bosh sahifa | `/` | Brauzerda sayt ochiladi; `curl` API haqida qisqa JSON oladi |
| Menyu | `/menu` | Barcha taomlar turkum boʻyicha |
| Taom sahifasi | `/menu/<id>` | masalan `/menu/4` |
| Xodimlar kirishi | `/admin` | Forma `POST /login` ga yuboriladi |
| Laboratoriya konsoli | `/ui` | Endpointlar roʻyxati, soʻrov namunalari, javoblar (sayt pastki qismidagi havola) |

## Ishga tushirish

```bash
docker compose up --build
```

| Versiya | Manzil |
|---------|--------|
| vulnerable (zaif) | http://127.0.0.1:8011 |
| fixed (tuzatilgan) | http://127.0.0.1:8012 |

Ikkala versiya bir xil kafe saytini koʻrsatadi — farq faqat konfiguratsiyada. Brauzerda `http://127.0.0.1:8011/` manzilini ochib, saytdan oddiy mehmon sifatida foydalaning.

> 🌐 **Interfeysni oʻzbek tilida ochish.** `/ui` sahifasi odatda inglizcha ochiladi. Oʻzbekchaga oʻtish uchun manzil qatorining oxiriga `?lang=uz` yozing — masalan `http://127.0.0.1:8011/ui?lang=uz` (vulnerable) yoki `http://127.0.0.1:8012/ui?lang=uz` (fixed), soʻng Enter bosing. Yoki sahifaning yuqori oʻng burchagidagi **UZ** tugmasini bosing: tanlov brauzerda eslab qolinadi.

Docker'siz:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ Ilova ataylab zaif qilingan. Faqat lokal ishga tushiring va internetga chiqarmang.

## Topshiriq
vulnerable versiyada **toʻrtta** konfiguratsiya xatosini toping (har birida flag yoki belgi yashirilgan):

1. Kafe paneliga parolni bilmasdan administrator sifatida kiring.
2. Serverga kirish huquqisiz ilovaning maxfiy maʼlumotlarini oling.
3. Ilovani ortiqcha texnik maʼlumot chiqarishga majburlang.
4. Javobning HTTP sarlavhalarini tekshiring: qaysi himoya sarlavhalari yetishmaydi va server nimani ortiqcha oshkor qiladi?

Keyin tekshiruvlarni fixed versiyada takrorlang. fixed da admin paroli ishga tushganda generatsiya qilinadi: `docker compose logs fixed` (yoki `ADMIN_PASSWORD` oʻzgaruvchisi orqali oʻzingiznikini bering).

## Maslahatlar
1. Qanday login va parollar koʻpincha «sukut boʻyicha» qolib ketadi? Xodimlar formasi `/admin` da turibdi.
2. `GET /files/<nom>` marshruti nima qiladi va `app.py` yonida qanday fayllar yotibdi? Ilovaning barcha marshrutlari `/ui` konsolida sanab oʻtilgan.
3. `GET /menu/abc` nima qaytaradi? (taom raqami son boʻlishi kerak)
4. Sarlavhalarni koʻrish uchun `curl -i` dan foydalaning.

Spoylerli toʻliq yechim: [SOLUTION.uz.md](./SOLUTION.uz.md)

## Qanday himoyalanish
- Sukut boʻyicha parollarni almashtirish, sirlarni kod yonidagi fayllarda emas, muhit oʻzgaruvchilarida saqlash
- Tashqariga ilovaning ildizini emas, faqat statik fayllar papkasini berish
- Foydalanuvchiga neytral xato koʻrsatish, tafsilotlarni server logiga yozish
- Himoya sarlavhalarini qoʻshish va versiyalar haqidagi ortiqcha bannerlarni olib tashlash
- Konfiguratsiyani avtomatik skanerlar bilan muntazam tekshirib turish
