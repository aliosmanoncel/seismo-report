import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# ─────────────────────────────────────────────────────────────
# Baker, Bradley & Stafford (2021) pasajları — preview metin
# ─────────────────────────────────────────────────────────────

BAKER_SUBDUCTION = (
    "Baker, Bradley &amp; Stafford (2021, s. 24): <em>\"Subduction margins, or subduction zones, "
    "are responsible for the destruction of crust… By the time the oceanic crust reaches the "
    "continental crust, it is relatively old, dense, cool, and thin compared with the continental "
    "crust. The result is that the oceanic crust is pushed beneath the continental crust, down "
    "into the mantle. The collision also causes uplift of the continental crust, so subduction "
    "zones are often coastal regions with significant topographic relief. The uplift is a result "
    "of the collision.\"</em>"
)

BAKER_ELASTIC_REBOUND = (
    "Baker, Bradley &amp; Stafford (2021, s. 31): <em>\"Elastic rebound theory essentially states "
    "that a region of the Earth's crust will be gradually loaded as a result of tectonic processes. "
    "The shear stress at a given location will gradually increase as a result of this loading. "
    "At some point, this accumulated stress exceeds the frictional resistance of a fault, and "
    "an earthquake initiates.\"</em>"
)

BAKER_SEISMIC_MOMENT = (
    "Baker, Bradley &amp; Stafford (2021, s. 36): <em>\"The size of an earthquake event is best "
    "characterized by the energy it releases. The seismic moment is the standard measure used to "
    "quantify the size of an earthquake… more conventional expressions use the average displacement "
    "over the rupture area [and shear modulus], making it directly proportional to the physical "
    "dimensions of the rupture.\"</em>"
)

BAKER_INTRO = (
    "Baker, Bradley &amp; Stafford (2021, s. 1): <em>\"Earthquakes cause damage to many parts of "
    "the natural and built environment, with potentially widespread and devastating impacts. "
    "Since 1900, earthquakes have killed approximately 8.5 million people and caused $2 trillion "
    "of damage (Daniell et al., 2011).\"</em>"
)

# ─────────────────────────────────────────────────────────────
# JSON güncelle — PAGE (REVIEW_SECTION_HTML)
# ─────────────────────────────────────────────────────────────
with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

BQ_BLUE = (
    'border-left:3px solid rgba(100,181,246,.5);margin:10px 0 10px 8px;'
    'padding:6px 14px;font-size:.84em;color:#90caf9;font-style:italic;line-height:1.6;'
)
BQ_AMBER = (
    'border-left:3px solid rgba(255,167,38,.4);margin:10px 0 10px 8px;'
    'padding:6px 14px;font-size:.84em;color:#ffcc80;font-style:italic;line-height:1.6;'
)

def bq(style, quote):
    return (
        f'\n      <blockquote style="{style}">\n'
        f'        {quote}\n'
        '      </blockquote>'
    )

# 1. Section 3 megathrust paragraf sonuna Baker seismic moment ekle
OLD_MO_PARA = (
    'bir <strong>megathrust kırılmasını</strong> işaret etmektedir.\n'
    '    </p>'
)
NEW_MO_PARA = OLD_MO_PARA + bq(BQ_BLUE, BAKER_SEISMIC_MOMENT)

if OLD_MO_PARA in rv:
    rv = rv.replace(OLD_MO_PARA, NEW_MO_PARA, 1)
    print('PAGE: Baker seismic moment alıntısı eklendi (Section 3)')
else:
    print('MISS: Mo/megathrust paragrafı')

# 2. Section 3 (Moment Tensor & Tektonik Bağlam) başlığı önüne Baker subduction ekle
OLD_SEC3_COMMENT = '<!-- 3. Moment Tensor ve Tektonik Bağlam -->'
NEW_SEC3_COMMENT = (
    bq(BQ_BLUE, BAKER_SUBDUCTION) + '\n\n    <!-- 3. Moment Tensor ve Tektonik Bağlam -->'
)
if OLD_SEC3_COMMENT in rv:
    rv = rv.replace(OLD_SEC3_COMMENT, NEW_SEC3_COMMENT, 1)
    print('PAGE: Baker subdüksiyon alıntısı eklendi (Section 3 önü)')
else:
    print('MISS: Section 3 comment anchor')

# 3. Sismik Çevrim (elastic rebound) — Section 5c ya da Appendix E'ye
OLD_SEISMIC_CYCLE = 'Sismik Çevrim Durumu'
if OLD_SEISMIC_CYCLE in rv:
    # Bu başlıktan sonra gelen ilk </p> kapanışına ekle
    idx = rv.find(OLD_SEISMIC_CYCLE)
    # İlk </p> sonrasına ekle
    end_p = rv.find('</p>', idx)
    if end_p > 0:
        insert_pos = end_p + 4
        rv = rv[:insert_pos] + bq(BQ_AMBER, BAKER_ELASTIC_REBOUND) + rv[insert_pos:]
        print('PAGE: Baker elastic rebound alıntısı eklendi (Sismik Çevrim bölümü)')
    else:
        print('MISS: Sismik Çevrim </p> bulunamadı')
else:
    print('MISS: Sismik Çevrim Durumu başlığı')

# 4. Giriş / Özet bölümüne (review başı) Baker intro istatistiği ekle
# REVIEW başının ilk <p> sonrasına
OLD_SEC1_COMMENT = '<!-- 1. Giriş -->\n    <div class="review-section-title">1. Giriş</div>'
NEW_SEC1_COMMENT = (
    '<!-- 1. Giriş -->\n    <div class="review-section-title">1. Giriş</div>'
    + bq(BQ_BLUE, BAKER_INTRO)
)
if OLD_SEC1_COMMENT in rv:
    rv = rv.replace(OLD_SEC1_COMMENT, NEW_SEC1_COMMENT, 1)
    print('PAGE: Baker intro istatistiği eklendi (Section 1 Giriş sonrası)')
else:
    print('MISS: Section 1 Giriş başlığı')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
