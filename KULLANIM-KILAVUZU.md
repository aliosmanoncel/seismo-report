# SeismoReport Kullanım Kılavuzu
**Sürüm 4.0 | Öncel, A.O. (2026)**

---

## Yeni Deprem Raporu Başlatmak

Claude'a şunu söyleyin:

> **"[Yer] Mw [büyüklük] depremini SeismoReport formatında incele.  
> Çalışma dizini: C:\Users\oncel\OneDrive\Documents\MEDYA\Final\seismo-report"**

Örnek:
> "Cuba Mw 6.1 depremini SeismoReport formatında incele.  
> Çalışma dizini: C:\Users\oncel\OneDrive\Documents\MEDYA\Final\seismo-report"

---

## Gerekli Ham Veriler (EMSC / USGS'den alınır)

| Veri | Kaynak | Kullanım |
|------|--------|----------|
| Büyüklük, konum, derinlik, tarih | EMSC / USGS | JSON temel alanlar |
| Artçı sismik CSV | USGS Earthquake Catalog | `parse_aftershocks.py` |
| ShakeMap (PGA/MMI GeoJSON) | USGS ShakeMap | `build_shakemap_layer.py` |
| Moment tensör (fay mekanizması) | GCMT / USGS | `update_mechanism.py` |
| DYFI (Did You Feel It?) GeoJSON | USGS | `build_testimonies.py` |
| W-phase santroid derinliği | USGS/IRIS | PSHA mesafe hesabı |

---

## Klasör Yapısı

```
seismo-report/
├── SeismoReport-Base.html     ← HTML şablonu (değiştirme)
├── generate.py                ← HTML üretici
├── KULLANIM-KILAVUZU.md       ← bu dosya
│
├── scripts/                   ← tüm Python scriptleri
│   ├── parse_aftershocks.py
│   ├── update_mechanism.py
│   ├── update_ftls_status.py
│   ├── update_methodology.py
│   ├── mindanao_psha.py       ← PSHA (depreme özel uyarla)
│   ├── mindanao_logic_tree.py ← Logic Tree (depreme özel uyarla)
│   ├── generate_gr_figure.py  ← G-R grafiği
│   ├── embed_psha_figures.py  ← görselleri JSON'a göm
│   ├── update_psha_results.py ← PSHA tablosunu ekle
│   ├── update_baker_quotes.py ← kaynak alıntıları
│   └── ... (diğerleri)
│
├── events/                    ← her deprem kendi klasöründe
│   ├── Mindanao-2026/         ← referans örnek (tamamlandı)
│   │   ├── Mindanao-2026.json
│   │   ├── Mindanao-2026-aftershocks.csv
│   │   └── shakemap_*.json
│   └── Cuba-2026/
│       └── Cuba-2026.json
│
└── OUTPUT/
    ├── SEISMO/    ← üretilen PAGE HTML
    ├── POSTS/     ← üretilen POST HTML
    └── PSHA/      ← figürler (PNG)
```

---

## Adım Adım Üretim Akışı

### 1. Olay klasörü aç
```
events/YeniDeprem-2026/
```

### 2. JSON iskeletini oluştur
`Mindanao-2026.json`'u referans al — aynı anahtar yapısı gerekir.  
Temel alanlar: `FILENAME`, `BASE_TEMPLATE`, `EQ_DATE`, `EQ_MAG`, `EQ_REGION`,  
`EQ_DEPTH`, `EQ_LAT`, `EQ_LON`, `REVIEW_SECTION_HTML`, `POST_HTML`

### 3. Scriptleri sırayla çalıştır
```
cd seismo-report
python scripts/parse_aftershocks.py events/YeniDeprem-2026/
python scripts/update_mechanism.py events/YeniDeprem-2026/YeniDeprem.json
python scripts/update_ftls_status.py events/YeniDeprem-2026/YeniDeprem.json
python scripts/update_methodology.py events/YeniDeprem-2026/YeniDeprem.json
python scripts/generate_gr_figure.py events/YeniDeprem-2026/YeniDeprem.json
python scripts/mindanao_psha.py        ← deprem parametrelerine göre düzenle
python scripts/mindanao_logic_tree.py  ← deprem parametrelerine göre düzenle
python scripts/embed_psha_figures.py events/YeniDeprem-2026/YeniDeprem.json
python scripts/update_psha_results.py events/YeniDeprem-2026/YeniDeprem.json
python scripts/update_baker_quotes.py events/YeniDeprem-2026/YeniDeprem.json
```

### 4. HTML üret (PAGE + POST tek komut)
```
python generate.py events/YeniDeprem-2026/YeniDeprem.json
```
Çıktı:
- `OUTPUT/SEISMO/<FILENAME>.html` — PAGE (tam analiz raporu)
- `OUTPUT/POSTS/<POST_FILENAME>.html` — POST (Blogger özet yazısı)

> **Not:** POST üretimi için JSON'da `POST_FILENAME` ve `POST_*` anahtarlarının dolu olması gerekir.  
> `SeismoReport-Post-Base.html` şablonu otomatik kullanılır.  
> Türkçe kesme işareti (`'`) `generate.py` tarafından otomatik `'` (U+2019) yapılır — JS hatası olmaz.

### POST için ek JSON anahtarları

| Anahtar | Örnek |
|---------|-------|
| `POST_FILENAME` | `"Mindanao-Mw78-Post"` |
| `POST_BADGE` | `"Deprem Analizi · Haziran 2026"` |
| `POST_BRAND_TITLE` | `"🔴 Mindanao'da Mw 7.8 Büyük Deprem"` |
| `POST_JS_TITLE` | `"Mindanao-da Mw 7.8 Buyuk Deprem"` (apostrof yok) |
| `POST_PAGE_URL` | Blogger PAGE tam URL |
| `POST_STAT_TABLE` | 4 stat kutusu HTML |
| `POST_STEPS_SECTION` | Analiz adımları HTML |
| `POST_BODY_SECTION` | Ana metin + kartlar + kutular HTML |
| `POST_REFS` | `<li>` kaynakça satırları |

### Video Özeti (Türkçe + İngilizce)

Her iki şablonda (PAGE + POST) hero bölümünün hemen altında yan yana iki video kutusu gösterilir.

| Anahtar | Açıklama | Örnek |
|---------|----------|-------|
| `YOUTUBE_VIDEO_ID` | Türkçe özet video ID | `"-GY0w_Tmub0"` |
| `YOUTUBE_VIDEO_ID_EN` | İngilizce özet video ID | `"XTUmUOGXfFM"` |

**Nasıl bulunur:** `https://youtu.be/ABC123` → ID = `ABC123`

> **Neden iki video?**  
> Türkçe + İngilizce video çifti, aynı anda yerel ve uluslararası kitleye ulaşmanın en hızlı yolu.  
> Yeni bir deprem raporunda her zaman her iki alanı doldurun.

---

## Cuba Mw 6.1 — Hızlı Başlangıç

**Deprem bilgileri:**
- Büyüklük: Mw 6.1 | Derinlik: 20 km
- Konum: 22.817°N, 85.108°W (Küba batısı)
- Tarih: 8 Haziran 2026, 18:00 UTC
- En yakın şehir: Pinar del Río (~152 km D), Mantua (~103 km GD)
- Fay bağlamı: Orta Amerika subdüksiyon + Karayip levhası doğrultu atım sistemi

**`Cuba-2026.json` zaten mevcut** — içeriğini doldurmak için  
Claude'a şunu söyleyin:

> "Cuba-2026.json iskeletini Mw 6.1 verileriyle doldur,  
> Mindanao-2026.json referans yapısını kullan"

---

## Mindanao Mw 7.8 — Referans Örnek (Tamamlandı ✓)

Tüm bölümler mevcut:
- ✓ Artçı dizisi analizi (Omori-Utsu p=0.619)
- ✓ FTLS b-değeri (b=0.635, KIRMIZI uyarı)
- ✓ G-R grafiği (Öncel 2026)
- ✓ PSHA tehlike eğrisi (Baker 2021 §6, Youngs 1988 GMPE)
- ✓ Logic Tree 27 dal (epistemik belirsizlik fraktilleri)
- ✓ Baker, Bradley & Stafford (2021) alıntıları
- ✓ Placeholder şekiller (Gulia, Cardwell, Aurelio)
- ✓ PAGE + POST HTML çıktıları

---

## Notlar

- `SeismoReport-Base.html` şablona dokunma — tüm içerik JSON üzerinden gider
- PSHA scriptleri (`mindanao_psha.py`, `mindanao_logic_tree.py`) depreme özel  
  parametreler (R, Vs30, Mmax, b) içeriyor — yeni deprem için kopyala ve uyarla
- `OUTPUT/PSHA/` içindeki PNG'ler `embed_psha_figures.py` ile JSON'a base64 olarak gömülür
- BOOKS klasörü taşınmadı — `INPUT/BOOKS/` konumunda referans PDF'ler mevcut
