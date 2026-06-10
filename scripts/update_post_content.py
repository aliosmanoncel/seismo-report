import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', encoding='utf-8') as f:
    post = f.read()

# ── 1. Derinlik satırı: 57 km → çift değer ──────────────────────────────
OLD_DEPTH_ROW = (
    "+'<tr><td>Derinlik</td><td>57 km</td><td>Orta-derin kuşak</td></tr>'"
)
NEW_DEPTH_ROW = (
    "+'<tr><td>Derinlik</td>"
    "<td>55.2 km <span style=\"font-size:.85em;color:#888;\">(hipo.)</span>"
    " · <strong>35.5 km</strong> <span style=\"font-size:.85em;color:#888;\">(santroid)</span></td>"
    "<td>Interface/Megathrust — Cotabato arayüzü</td></tr>'"
)
if OLD_DEPTH_ROW in post:
    post = post.replace(OLD_DEPTH_ROW, NEW_DEPTH_ROW, 1)
    print('1. Derinlik satırı güncellendi')
else:
    print('MISS: derinlik satırı')

# ── 2. Mekanizma satırı ekle (derinlik satırından hemen sonra) ────────────
OLD_AFTER_DEPTH = (
    "+'<tr><td>Zaman</td><td>2026-06-07 23:37:42 UTC</td><td>Yerel: 07:37</td></tr>'"
)
NEW_AFTER_DEPTH = (
    "+'<tr><td>Mekanizma</td>"
    "<td><strong>Interface / Megathrust</strong></td>"
    "<td>NP2: 161°/45°/77° · DC %87 · Mo=5.74×10²⁰ N·m</td></tr>'"
    "\n    +'<tr><td>Zaman</td><td>2026-06-07 23:37:42 UTC</td><td>Yerel: 07:37</td></tr>'"
)
if OLD_AFTER_DEPTH in post:
    post = post.replace(OLD_AFTER_DEPTH, NEW_AFTER_DEPTH, 1)
    print('2. Mekanizma satırı eklendi')
else:
    print('MISS: zaman satırı')

# ── 3. FTLS + p-değeri satırları ekle (tablo kapanışından önce) ───────────
OLD_TABLE_END = "+'</table>'"
NEW_TABLE_END = (
    "+'<tr><td>FTLS Durumu</td>"
    "<td style=\"color:#ef5350;font-weight:700;\">🔴 KIRMIZI</td>"
    "<td>b/b<sub>ref</sub> &lt; 0.90 — gerilme boşalımı tamamlanmadı</td></tr>'"
    "\n    +'<tr><td>Sönümlenme (p)</td>"
    "<td><strong>0.619</strong></td>"
    "<td>Normalden <strong>2.8× yavaş</strong> — 90+ gün tehlike penceresi</td></tr>'"
    "\n    +'<tr><td>Bath Yasası</td>"
    "<td>M6.7 ✓</td>"
    "<td>Beklenti Mw 6.6 — en büyük artçı teyit edildi</td></tr>'"
    "\n    +'</table>'"
)
if OLD_TABLE_END in post:
    post = post.replace(OLD_TABLE_END, NEW_TABLE_END, 1)
    print('3. FTLS/p/Bath satırları eklendi')
else:
    print('MISS: tablo kapanışı')

# ── 4. Değerlendirme paragrafını güncelle ────────────────────────────────
OLD_EVAL = (
    "+'<h2>Değerlendirme</h2>"
    "<p>57 km\\'lik odak derinliği sığ odaklı depremlere kıyasla yüzey hasarını "
    "sınırlamakla birlikte, Mw 7.8 büyüklüğü geniş alanlarda güçlü sarsıntı "
    "üretmiştir. PTWC tsunami uyarı protokolleri derhal devreye girmiş, artçı "
    "sismisitenin haftalarca sürmesi beklenmektedir.</p>'"
)
NEW_EVAL = (
    "+'<h2>Değerlendirme</h2>'"
    "\n    +'<p>Deprem, <strong>55.2 km hiposantral derinlikte</strong> başlamış; "
    "W-phase moment tensörü enerji merkezinin <strong>35.5 km derinlikte</strong> "
    "yoğunlaştığını ve kırılmanın doğrudan Cotabato megathrust arayüzünde "
    "(Interface/Megathrust) gerçekleştiğini kesinleştirmiştir. "
    "Bu, 1976 Moro Körfezi (Mw 7.9) depreminin aynı tektono-sismik sınıfıdır. "
    "PEIS VIII şiddeti General Santos ve Koronadal başta olmak üzere geniş alanda "
    "ağır hasara yol açmış; sarsıntı episantreden <strong>2 000 km'den fazla uzakta</strong> "
    "Tayland (Phuket) ve Endonezya'da (Surabaya) dahi tanık raporlarıyla belgelenmiştir. "
    "PTWC tsunami uyarı protokolleri derhal devreye girmiştir.</p>'"
    "\n    +'<div style=\"background:#fff3cd;border:1px solid #f0a500;border-radius:6px;"
    "padding:10px 14px;margin:10px 0;font-size:9pt;\">'"
    "\n    +'<strong>🔴 FTLS Trafik Işığı Analizi (Gulia vd., 2024):</strong> "
    "Artçı b-değeri (0.635) tüm referans senaryolarında eşik altında kalmaktadır. "
    "Bu, bölgedeki <strong>tektonik gerilmenin henüz tam boşalmadığını</strong> "
    "ve sismik riskin <strong>KIRMIZI</strong> düzeyde sürdüğünü göstermektedir. "
    "Düşük sönümlenme hızı (p=0.619) nedeniyle tehlike penceresi normalden "
    "<strong>2.8 kat daha uzun</strong> olacak; yoğun artçı aktivitesi "
    "<strong>en az 90 gün boyunca</strong> sürmesi beklenmektedir.'"
    "\n    +'</div>'"
)
if OLD_EVAL in post:
    post = post.replace(OLD_EVAL, NEW_EVAL, 1)
    print('4. Değerlendirme paragrafı güncellendi')
else:
    print('MISS: değerlendirme — deneme 2')
    # escape farklılığını dene
    idx = post.find('57 km\\\\')
    if idx < 0:
        idx = post.find("haftalarca")
    print(f'  haftalarca idx={idx}')
    print(repr(post[max(0,idx-200):idx+50]))

# ── 5. Başlık/lead'deki "57 km" → güncelle ─────────────────────────────
OLD_LEAD = "57 km derinlikte gerçekleşen güçlü deprem"
NEW_LEAD = "55.2 km derinlikte gerçekleşen Interface/Megathrust depremi"
if OLD_LEAD in post:
    post = post.replace(OLD_LEAD, NEW_LEAD, 1)
    print('5. Başlık derinlik güncellendi')
else:
    print('MISS: başlık derinlik')

with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', 'w', encoding='utf-8') as f:
    f.write(post)
print('POST kaydedildi')
