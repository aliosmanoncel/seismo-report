import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────
# Alıntılar (pasajlar kitaplardan ayıklandı)
# ─────────────────────────────────────────────────────────────

QUOTE_GR = (
    "Stein &amp; Wysession (2003, s. 274): <em>\"The number of earthquakes that occur yearly "
    "around the world varies with magnitude, with successively smaller earthquakes being more "
    "common. This observation was quantified by Gutenberg and Richter in the 1940s via the "
    "logarithmic earthquake frequency–magnitude [relation] in which N is the number of earthquakes "
    "with magnitude greater than or equal to M occurring in a given time… the slope, b, is "
    "generally about 1… significant variations occur on smaller scales. The b value of earthquake "
    "swarms is often much larger than 1… Some patches have b values much less than 1, implying "
    "shorter recurrence time. These patches have been interpreted as possible asperities or stress "
    "concentrations.\"</em>"
)

QUOTE_AFTERSHOCK = (
    "Stein &amp; Wysession (2003, s. 277): <em>\"The smaller aftershocks following a mainshock "
    "have a characteristic distribution in size and time… The diminishing number of aftershocks "
    "with time is typical for large earthquakes.\"</em>"
)

QUOTE_SUBDUCTION = (
    "Stein &amp; Wysession (2003, s. 308): <em>\"Subduction zones have a wide variety of "
    "earthquakes with different focal mechanisms and depths. There are shallow (less than 70 km "
    "deep)… Great thrust earthquakes — often, but not always — occur at the subduction zone "
    "interface.\"</em>"
)

QUOTE_LIQUEFACTION = (
    "Stein &amp; Wysession (2003, s. 20): <em>\"Another earthquake hazard involves liquefaction, "
    "a process by which loose water-saturated sands behave like liquids when vigorously shaken. "
    "Under normal conditions, the sand grains are in contact with each other, and water fills the "
    "pore spaces between them. Strong shaking moves the grains apart, so the [mixture] behaves "
    "like a fluid.\"</em>"
)

QUOTE_SCHOLZ = (
    "Scholz (2002, s. 303): <em>\"About 85% of the [global seismic] moment release occurs at "
    "subduction zones. More than 95% is produced by shallow, plate-boundary earthquakes… "
    "The great Chile earthquake of 1960 ruptured about 800 km of the subduction zone interface "
    "at the Peru–Chile trench… Most of the moment must be contained in the few largest "
    "events.\"</em>"
)

QUOTE_FOWLER = (
    "Fowler (2005, s. 118): <em>\"[The frequency–magnitude relationship] for earthquakes "
    "demonstrates the self-similar scaling of seismic sources — a fundamental property "
    "of earthquake populations across tectonic regimes.\"</em>"
)

# ─────────────────────────────────────────────────────────────
# 1. PAGE (SeismoReport) — REVIEW_SECTION_HTML güncelle
# ─────────────────────────────────────────────────────────────
with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# 1a. b-değeri kartına (Kart 8 B. bölümüne) GR alıntısı ekle
OLD_B_SECTION = (
    '        M̄ = ortalama büyüklük (M ≥ M<sub>c</sub>); +0.05 bin düzeltmesi (Utsu, 1966).\n'
    '        İki segmentli analiz: M<sub>c</sub>–M5.0 arası\n'
    '        <strong>b₁ = 0.829</strong> (mb ağırlıklı);\n'
    '        M5.0+ için <strong>b₂ = 1.12</strong> (Mw ağırlıklı).\n'
    '        Slope break M5.0\'de mb doyumundan kaynaklanmaktadır.\n'
    '      </p>'
)
NEW_B_SECTION = (
    '        M̄ = ortalama büyüklük (M ≥ M<sub>c</sub>); +0.05 bin düzeltmesi (Utsu, 1966).\n'
    '        İki segmentli analiz: M<sub>c</sub>–M5.0 arası\n'
    '        <strong>b₁ = 0.829</strong> (mb ağırlıklı);\n'
    '        M5.0+ için <strong>b₂ = 1.12</strong> (Mw ağırlıklı).\n'
    '        Slope break M5.0\'de mb doyumundan kaynaklanmaktadır.\n'
    '      </p>\n'
    '      <blockquote style="border-left:3px solid rgba(100,181,246,.5);margin:10px 0 10px 8px;'
    'padding:6px 14px;font-size:.84em;color:#90caf9;font-style:italic;line-height:1.6;">\n'
    f'        {QUOTE_GR}\n'
    '      </blockquote>'
)
if OLD_B_SECTION in rv:
    rv = rv.replace(OLD_B_SECTION, NEW_B_SECTION, 1)
    print('PAGE: b-değeri GR alıntısı eklendi')
else:
    print('MISS: b-value section')

# 1b. Omori-Utsu bölümüne aftershock alıntısı
OLD_OMORI = (
    '        Mindanao 2026: <strong>K = 14.10, c ≈ 0.0001, p = 0.619</strong>.\n'
    '        p &lt; 0.7 → Yüksek Sismik Kalıcılık.\n'
    '        Tipik aralık: p = 0.8–1.2 (Utsu, 1957).\n'
    '      </p>'
)
NEW_OMORI = (
    '        Mindanao 2026: <strong>K = 14.10, c ≈ 0.0001, p = 0.619</strong>.\n'
    '        p &lt; 0.7 → Yüksek Sismik Kalıcılık.\n'
    '        Tipik aralık: p = 0.8–1.2 (Utsu, 1957).\n'
    '      </p>\n'
    '      <blockquote style="border-left:3px solid rgba(100,181,246,.5);margin:10px 0 10px 8px;'
    'padding:6px 14px;font-size:.84em;color:#90caf9;font-style:italic;line-height:1.6;">\n'
    f'        {QUOTE_AFTERSHOCK}\n'
    '      </blockquote>'
)
if OLD_OMORI in rv:
    rv = rv.replace(OLD_OMORI, NEW_OMORI, 1)
    print('PAGE: Omori aftershock alıntısı eklendi')
else:
    print('MISS: omori section')

# 1c. Jeoteknik Risk (sıvılaşma) bölümüne Stein alıntısı
OLD_LIQUEF_NOTE = (
    '        <strong>Kaynaklar:</strong>\n'
    '        Zhu vd. (2017) <em>BSSA</em> 107(3);\n'
    '        Nowicki-Jessee vd. (2018) <em>Remote Sensing of Environment</em> 219, 151–166;\n'
    '        USGS ShakeMap/PAGER (us7000srb1).\n'
    '      </p>'
)
NEW_LIQUEF_NOTE = (
    '      <blockquote style="border-left:3px solid rgba(255,167,38,.4);margin:10px 0 10px 8px;'
    'padding:6px 14px;font-size:.84em;color:#ffcc80;font-style:italic;line-height:1.6;">\n'
    f'        {QUOTE_LIQUEFACTION}\n'
    '      </blockquote>\n'
    '        <strong>Kaynaklar:</strong>\n'
    '        Zhu vd. (2017) <em>BSSA</em> 107(3);\n'
    '        Nowicki-Jessee vd. (2018) <em>Remote Sensing of Environment</em> 219, 151–166;\n'
    '        USGS ShakeMap/PAGER (us7000srb1).\n'
    '      </p>'
)
if OLD_LIQUEF_NOTE in rv:
    rv = rv.replace(OLD_LIQUEF_NOTE, NEW_LIQUEF_NOTE, 1)
    print('PAGE: Sıvılaşma Stein alıntısı eklendi')
else:
    print('MISS: liquefaction note')

# 1d. Megathrust mekanizması / Appendix A ya da Section 3'e Scholz alıntısı
OLD_MECHANISM_SECTION = '    <div class="review-section-title">3. Moment Tensor Çözümü'
NEW_MECHANISM_SECTION = (
    '    <blockquote style="border-left:3px solid rgba(100,181,246,.4);margin:0 0 14px 0;'
    'padding:8px 16px;font-size:.84em;color:#90caf9;font-style:italic;line-height:1.6;'
    'background:rgba(100,181,246,.04);border-radius:0 6px 6px 0;">\n'
    f'      {QUOTE_SCHOLZ}\n'
    '    </blockquote>\n'
    '    <div class="review-section-title">3. Moment Tensor Çözümü'
)
if OLD_MECHANISM_SECTION in rv:
    rv = rv.replace(OLD_MECHANISM_SECTION, NEW_MECHANISM_SECTION, 1)
    print('PAGE: Scholz subduction alıntısı eklendi (Section 3 önü)')
else:
    print('MISS: Section 3 title')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('PAGE JSON kaydedildi')

# ─────────────────────────────────────────────────────────────
# 2. POST dosyasını güncelle — Değerlendirme altına ders kitabı notları
# ─────────────────────────────────────────────────────────────
with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', encoding='utf-8') as f:
    post = f.read()

OLD_POST_CTA = (
    "+'<p style=\"font-size:8pt;color:#777;border-top:1px solid #ccc;"
    "margin-top:18pt;padding-top:6pt;text-align:center;\">"
)
NEW_POST_INSERT = (
    "+'<div style=\"background:#f0f4ff;border-left:4px solid #5b8dee;border-radius:4px;"
    "padding:10pt 14pt;margin:10pt 0;font-size:8.5pt;color:#334;\">'"
    "\n    +'<strong>📚 Temel Kavram (Stein &amp; Wysession, 2003):</strong><br>'"
    "\n    +'<em>\"Another earthquake hazard involves liquefaction, a process by which loose "
    "water-saturated sands behave like liquids when vigorously shaken… Strong shaking moves "
    "the grains apart, so the [mixture] behaves like a fluid.\"</em> — "
    "Mindanao\\'nın Sarangani Körfezi kıyı dolguları bu risk altındadır.'"
    "\n    +'</div>'"
    "\n    +'<div style=\"background:#fff8f0;border-left:4px solid #e8a020;border-radius:4px;"
    "padding:10pt 14pt;margin:10pt 0;font-size:8.5pt;color:#334;\">'"
    "\n    +'<strong>📚 Subdüksiyon Gerçeği (Scholz, 2002):</strong><br>'"
    "\n    +'<em>\"About 85% of the global seismic moment release occurs at subduction zones. "
    "More than 95% is produced by shallow, plate-boundary earthquakes.\"</em> — "
    "Mindanao Mw 7.8 bu kategorinin tipik bir örneğidir.'"
    "\n    +'</div>'"
    "\n    +'<p style=\"font-size:8pt;color:#777;border-top:1px solid #ccc;"
    "margin-top:18pt;padding-top:6pt;text-align:center;\">"
)

if OLD_POST_CTA in post:
    post = post.replace(OLD_POST_CTA, NEW_POST_INSERT, 1)
    print('\nPOST: Ders kitabı alıntıları eklendi')
else:
    print('\nMISS: POST CTA insertion point')

with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', 'w', encoding='utf-8') as f:
    f.write(post)
print('POST kaydedildi')
