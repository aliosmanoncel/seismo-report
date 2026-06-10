import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# Kart 8'in kapanısını bul
OLD_END = (
    '        Mevcut N = 334; 3 tam pencere mevcut — izleme sürmekte.\n'
    '        Phase I/II/III geçiş noktaları b–D korelasyonunun işaret değiştirdiği andır.\n'
    '      </p>\n\n'
    '      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">\n'
    '        G. FTLS b-positive Tahmincisi (Gulia vd., 2024)\n'
    '      </p>'
)

NEW_END = (
    '        Mevcut N = 334; 3 tam pencere mevcut — izleme sürmekte.\n'
    '        Phase I/II/III geçiş noktaları b–D korelasyonunun işaret değiştirdiği andır.\n'
    '      </p>\n\n'
    '      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">\n'
    '        G. FTLS b-positive Tahmincisi (Gulia vd., 2024)\n'
    '      </p>'
)

# Kart 8 kapanısını ve altına ekleme noktasını bul
# Kart 8 "b-positive" paragrafından sonra bitiyor
CARD8_CLOSE = (
    'Kırmızı (Mw 8.0+ riski uyarısı).\n'
    '      </p>\n'
    '    </div>\n\n'
    '    <div class="info-note">\n'
    '      <strong>Sismolojik Değerlendirme — Metodoloji Çerçevesi:</strong>'
)

DATA_SEL_BLOCK = (
    'Kırmızı (Mw 8.0+ riski uyarısı).\n'
    '      </p>\n\n'
    '      <div style="border-top:1px solid rgba(255,255,255,.08);margin-top:16px;padding-top:14px;">\n'
    '        <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:0 0 8px;">\n'
    '          H. Veri Seçimi — Uzamsal ve Zamansal Filtreleme\n'
    '        </p>\n\n'
    '        <p style="font-size:.87em;margin-bottom:8px;">\n'
    '          <strong>H1. Gardner &amp; Knopoff (1974) — Etki Yarıçapı ve Zaman Penceresi</strong><br>\n'
    '          GK74 büyüklük-bağımlı tablosuna göre Mw 7.8 için:\n'
    '        </p>\n'
    '        <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;'
    'font-family:monospace;font-size:.9em;margin:4px 0 10px;">\n'
    '          R<sub>max</sub> = 10<sup>(0.1238·M + 0.983)</sup> km &nbsp;→&nbsp; '
    'Mw 7.8 için <strong>~560 km</strong><br>\n'
    '          T<sub>max</sub> = 10<sup>(0.5409·M − 0.547)</sup> gün &nbsp;→&nbsp; '
    'Mw 7.8 için <strong>~90 gün (3 ay)</strong>\n'
    '        </div>\n'
    '        <p style="font-size:.84em;color:#94a3b8;margin-bottom:12px;">\n'
    '          Kullanım amacı: FTLS analizinin uygulanacağı '
    '<em>coğrafi alan sınırı ve zaman penceresini</em> belirlemek.\n'
    '          Klasik "declustering" (ana şoktan arındırma) amacıyla değil,\n'
    '          sismik sekansın etki sınırlarını tanımlamak için kullanılmıştır.\n'
    '        </p>\n\n'
    '        <p style="font-size:.87em;margin-bottom:8px;">\n'
    '          <strong>H2. Wells &amp; Coppersmith (1994) — 3D Fay Kutusu Boyutları</strong><br>\n'
    '          Artçı alanını sınırlamak için fay düzlemini (NP2: gidiş 161°, eğim 45°, santroid 35.5 km)\n'
    '          çevreleyen 3 boyutlu kutular oluşturulmuştur:\n'
    '        </p>\n'
    '        <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;'
    'font-family:monospace;font-size:.9em;margin:4px 0 10px;">\n'
    '          log(SRL) = −2.57 + 0.62·M &nbsp;→&nbsp; Mw 7.8: <strong>SRL ≈ 232 km</strong><br>\n'
    '          log(RLD) = −2.42 + 0.58·M &nbsp;→&nbsp; Mw 7.8: <strong>RLD ≈ 148 km</strong><br>\n'
    '          log(W)   = −0.76 + 0.27·M &nbsp;→&nbsp; Mw 7.8: <strong>W ≈ 65 km</strong>\n'
    '        </div>\n'
    '        <p style="font-size:.84em;color:#94a3b8;margin-bottom:12px;">\n'
    '          SRL: yüzey kırık uzunluğu · RLD: subsurface kırık uzunluğu · W: fay genişliği.\n'
    '          3D kutunun derinlik sınırı: santroid (35.5 km) ± fay genişliği (65 km/2) ≈ 3–68 km.\n'
    '          Bu sınır dışında kalan olaylar (çok sığ veya çok derin) değerlendirme dışı bırakılır.\n'
    '        </p>\n\n'
    '        <p style="font-size:.87em;margin-bottom:8px;">\n'
    '          <strong>H3. Dinamik Fay Düzlemi Seçimi</strong><br>\n'
    '          Ana şok sonrası ilk 1 saatteki artçı dağılımı, iki nodal düzlemden hangisinin\n'
    '          (NP1: 359°/47°/103° mi yoksa NP2: 161°/45°/77° mi) aktif olduğunu belirler.\n'
    '          Artçıların NP2 (Cotabato arayüzü, SSE–NNW) yöneliminde kümelenmesi durumunda\n'
    '          bu düzlemin kutusu aktif olarak seçilir; FTLS analizi bu hacimle sınırlı tutulur.\n'
    '        </p>\n'
    '      </div>\n'
    '    </div>\n\n'
    '    <div class="info-note">\n'
    '      <strong>Sismolojik Değerlendirme — Metodoloji Çerçevesi:</strong>'
)

if CARD8_CLOSE in rv:
    rv = rv.replace(CARD8_CLOSE, DATA_SEL_BLOCK, 1)
    print('Veri seçimi alt notu eklendi')
else:
    print('HATA: Kart 8 kapanışı bulunamadı')
    idx = rv.find('Kırmızı (Mw 8.0+')
    print(repr(rv[idx:idx+200]))

# Kaynaklar bölümüne GK74 ve W&C ekle
OLD_REF = '<div class="review-ref-item">Scordilis'
NEW_REF = (
    '<div class="review-ref-item">Gardner, J. K. &amp; Knopoff, L. (1974). '
    'Is the sequence of earthquakes in Southern California, with aftershocks removed, Poissonian? '
    '<em>Bulletin of the Seismological Society of America</em>, 64(5), 1363–1367.</div>\n    '
    '<div class="review-ref-item">Wells, D. L. &amp; Coppersmith, K. J. (1994). '
    'New empirical relationships among magnitude, rupture length, rupture width, rupture area, '
    'and surface displacement. '
    '<em>Bulletin of the Seismological Society of America</em>, 84(4), 974–1002.</div>\n    '
)
if OLD_REF in rv:
    rv = rv.replace(OLD_REF, NEW_REF + OLD_REF, 1)
    print('GK74 ve W&C referansları eklendi')
else:
    print('MISS: Scordilis referansı bulunamadı')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
