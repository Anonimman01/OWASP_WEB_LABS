🌐 [Русский](./SOLUTION.md) · **Oʻzbekcha**

# A03 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

## Zaif bogʻliqliklarni qidirish

```bash
pip install pip-audit
pip-audit -r vulnerable/requirements.txt --no-deps --disable-pip
```

`--no-deps --disable-pip` kerak, chunki fayldagi barcha versiyalar allaqachon qotirilgan va tekshirish uchun hech narsa oʻrnatish shart emas.

Laboratoriya yaratilgan paytda (2026-yil oktabr) `pip-audit` **yetti** ta paketda bildirishnomalar topadi:

| Paket | Versiya | Loyihaga qanday kirgan |
|-------|---------|------------------------|
| Flask | 2.2.2 | bevosita |
| Werkzeug | 2.2.2 | Flask bogʻliqligi |
| Jinja2 | 3.1.2 | Flask bogʻliqligi |
| requests | 2.25.1 | bevosita |
| urllib3 | 1.26.4 | requests bogʻliqligi |
| idna | 2.10 | requests bogʻliqligi |
| certifi | 2024.8.30 | requests bogʻliqligi |

Muammolarning aksariyati **tranzitiv** bogʻliqliklarda: loyihada ularni hech kim tanlamagan, lekin ular prodakshenda ishlaydi. Aniq sonlar va identifikatorlar vaqt oʻtishi bilan oʻzgaradi, chunki zaifliklar bazalari toʻldirilib boriladi.

## Tuzatish (fixed)

1. Versiyalar yangilangan: Flask 3.1.3, Werkzeug 3.1.9, Jinja2 3.1.6, requests 2.33.0 (va ularning bogʻliqliklari).
2. `requirements.in` da faqat bevosita bogʻliqliklar sanalgan, `requirements.txt` esa `pip-compile` orqali barcha tranzitiv paketlar va xeshlar bilan birga generatsiya qilingan:

   ```bash
   pip install pip-tools
   pip-compile --generate-hashes --strip-extras --output-file=requirements.txt requirements.in
   ```

3. Docker'da oʻrnatish `--require-hashes` bilan bajariladi: paket mazmuni xeshga mos kelmasa, pip uni oʻrnatishdan bosh tortadi.

Tekshirish:

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip
# No known vulnerabilities found
```

## Xesh bilan tajriba

```bash
sed 's/--hash=sha256:[0-9a-f]\{64\}/--hash=sha256:0000000000000000000000000000000000000000000000000000000000000000/g' \
  fixed/requirements.txt > tampered.txt
python -m venv /tmp/venv-test
/tmp/venv-test/bin/pip install --require-hashes -r tampered.txt
```

Natija: `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE ...`, oʻrnatish bajarilmaydi. pip paketni indeksdan kelish yoʻlida almashtirib yuborilishidan shu tarzda himoya qiladi.

> Tajribani **toza** muhitda bajarish kerak: paketlar allaqachon oʻrnatilgan boʻlsa, pip ularni yuklab olmaydi va xeshlarni solishtirmaydi.

## SBOM

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip -f cyclonedx-json -o sbom.json
```

Natijada loyiha komponentlarining CycloneDX (JSON) formatidagi roʻyxati hosil boʻladi. Uni relizning yonida saqlash va yangi bildirishnomalar bilan solishtirish mumkin.

## Yana nimani esda tutish kerak
- Xeshlari bor lock-fayl almashtirib yuborishdan himoya qiladi, lekin zaifliklardan **himoya qilmaydi**: versiyalarni baribir yangilash kerak.
- Bogʻliqliklarni tekshirishni avtomatik (masalan, CI da) va jadval boʻyicha ishga tushirgan maʼqul.
- Bu laboratoriya zararli paketlarni koʻrsatmaydi. Ichki paketni ommaviy paket bilan almashtirish (dependency confusion) va nomlardagi xatolar (typosquatting) nazariy jihatdan koʻrib chiqiladi: faqat oʻzingiz kutgan narsani, ishonchli indekslardan oʻrnating.
