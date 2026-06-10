import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)

rv = d['REVIEW_SECTION_HTML']
ap = d['APPENDIX_SECTIONS_HTML']

# ── 1. REVIEW Section 3: eski tek paragraf → tablo + genisletilmis metin ──
OLD_SEC3 = (
    'Moment tensör çözümleri, depremin yaklaşık kuzey-güney doğrultusunda doğrudan '
    'baskı eksenine sahip saf ters faylanma (thrust) mekanizmasıyla gerçekleştiğini '
    'ortaya koymaktadır. USGS W-faz (Mww) çözümüne göre düğüm düzlemleri: '
    '<strong>NP1: Gidiş 359°, Eğim 47°, Kayma 103°; NP2: Gidiş 161°, Eğim 45°, Kayma 77°</strong>. '
    'Çift-çift (DC) bileşeni %87 olup saf bir thrust mekanizmasını göstermektedir '
    '(skaler moment Mo = 5.74 × 10²⁰ N·m). P-ekseninin azimütü ~80° (E-W) olup '
    'Philippine Sea Levhası\'nın KKB yönlü hareketi ile örtüşmektedir. '
    'Bu mekanizma, Filipinler Yay Sistemi\'nde Avustralya–Pasifik Levhası sınırlarında '
    'beklenen sıkışmalı tektonik rejimle tam uyum içindedir.'
)

NEW_SEC3 = (
    'USGS, GFZ, EMSC ve GlobalCMT\'nin bağımsız moment tensör çözümleri, depremin '
    '<strong>saf ters faylanma (interface/megathrust)</strong> mekanizmasıyla '
    'gerçekleştiğini tutarlı biçimde ortaya koymaktadır. '
    'USGS üç farklı yöntemle elde ettiği çözümler aşağıda özetlenmiştir:\n'
    '    </p>\n'
    '    <table class="review-table" style="margin:12px 0 18px;">\n'
    '      <caption>Tablo 2. USGS Odak Mekanizması Çözümleri — us7000srb1</caption>\n'
    '      <thead>\n'
    '        <tr><th>Yöntem</th><th>NP1 (Gidiş/Eğim/Kayma)</th>'
    '<th>NP2 (Gidiş/Eğim/Kayma)</th><th>Santroid Derinliği</th></tr>\n'
    '      </thead>\n'
    '      <tbody>\n'
    '        <tr><td><strong>Mww (W-faz)</strong></td>'
    '<td>161° / 45° / 77°</td><td>359° / 47° / 103°</td><td>35.5 km</td></tr>\n'
    '        <tr><td>Mwc (Centroid)</td>'
    '<td>346° / 40° / 89°</td><td>167° / 50° / 91°</td><td>—</td></tr>\n'
    '        <tr><td>Mwb (Body Wave)</td>'
    '<td>331° / 50° / 84°</td><td>160° / 40° / 97°</td><td>—</td></tr>\n'
    '      </tbody>\n'
    '    </table>\n'
    '    <p class="review-body-text">\n'
    '      Üç çözümün ortalaması NP2 düzlemi için gidiş ~160°–167° (SSE–NNW), '
    'eğim ~40°–50° (batıya) ve kayma ~77°–97° vermektedir; bu geometri '
    'Cotabato Hendeği\'nin dalar-çıkar levha arayüz geometrisiyle tam uyum içindedir. '
    'Çift-çift (DC) bileşeni %87 olup karmaşık kayma bileşeni yoktur '
    '(Mo = 5.74 × 10²⁰ N·m). P-ekseninin azimütü ~80° (yaklaşık E–W), '
    'Philippine Sea Levhası\'nın KKB yönlü hareketinden kaynaklanan sıkışma rejimini '
    'yansıtmaktadır. Odak mekanizması, "intraslab" (levha içi bükülme) '
    'senaryosuyla bağdaşmamaktadır; derinlik ve geometri, Cotabato subdüksiyon '
    'arayüzü üzerindeki bir <strong>megathrust kırılmasını</strong> işaret etmektedir.'
)

if OLD_SEC3 in rv:
    rv = rv.replace(OLD_SEC3, NEW_SEC3, 1)
    print('Section 3 guncellendi')
else:
    print('HATA: Section 3 eski metin bulunamadi')

# ── 2. REVIEW: 1976 Moro Körfezi karsilastirmasi ──────────────────
OLD_MORO = '2026 depremi, bu segmentin modern dönemde kayıt altına alınan en büyük olaylarından biridir.'
NEW_MORO = (
    '2026 depremi, bu segmentin modern dönemde kayıt altına alınan en büyük olaylarından biridir. '
    'Mekanizma bakımından 1976 Moro Körfezi (Mw 7.9) depremiyle aynı sınıfa — '
    '<strong>levha arayüzü (megathrust) kırılması</strong> — dahildir; her iki olay da '
    'Cotabato subdüksiyon sisteminin ana arayüz düzleminde gerçekleşmiştir.'
)
if OLD_MORO in rv:
    rv = rv.replace(OLD_MORO, NEW_MORO, 1)
    print('1976 Moro referansi eklendi')
else:
    print('HATA: Moro eski metin bulunamadi')

d['REVIEW_SECTION_HTML'] = rv

# ── 3. APPENDIX A: Mekanizma, Moment, event ID duzelt ────────────
OLD_MEC = '<strong>Mekanizma:</strong> Ters Faylanma (Thrust) — tüm moment tensör çözümleri tutarlı'
NEW_MEC = '<strong>Mekanizma:</strong> Interface/Megathrust — Levha Arayüzü Ters Faylanması (DC %87, tüm çözümler tutarlı)'
if OLD_MEC in ap:
    ap = ap.replace(OLD_MEC, NEW_MEC, 1)
    print('Appendix mekanizma guncellendi')
else:
    print('HATA: mekanizma eski metin bulunamadi')

OLD_MOM = '<strong>Moment:</strong> M₀ ≈ 4.5 × 10²⁰ N·m (Mw 7.8 eşdeğeri)'
NEW_MOM = '<strong>Moment:</strong> M₀ = 5.74 × 10²⁰ N·m (USGS Mww 7.77 = Mw 7.8 eşdeğeri)'
if OLD_MOM in ap:
    ap = ap.replace(OLD_MOM, NEW_MOM, 1)
    print('Moment guncellendi')
else:
    print('HATA: moment eski metin bulunamadi')

# Event ID duzelt
cnt = ap.count('us7000lff4')
ap = ap.replace('us7000lff4', 'us7000srb1')
print(f'Event ID duzeltildi: {cnt} yer')

# ── 4. APPENDIX A: NP tablosu ekle (Kaynak Parametreleri kartinin sonuna) ──
NEEDLE = '    </div>\n\n    <div class="info-note">\n      <strong>Cotabato Çukuru nedir?</strong>'

NP_BLOCK = (
    '    </div>\n\n'
    '    <div class="analysis-card" style="margin-top:16px;">\n'
    '      <h4>🔵 Odak Mekanizması — USGS Üç Çözüm (us7000srb1)</h4>\n'
    '      <table class="review-table" style="font-size:.88em;margin-top:8px;">\n'
    '        <thead>\n'
    '          <tr><th>Yöntem</th><th>NP1 Gidiş/Eğim/Kayma</th>'
    '<th>NP2 Gidiş/Eğim/Kayma</th><th>Santroid</th></tr>\n'
    '        </thead>\n'
    '        <tbody>\n'
    '          <tr><td><strong>Mww (W-faz)</strong></td>'
    '<td>161° / 45° / 77°</td><td>359° / 47° / 103°</td><td>35.5 km</td></tr>\n'
    '          <tr><td>Mwc (Centroid)</td>'
    '<td>346° / 40° / 89°</td><td>167° / 50° / 91°</td><td>—</td></tr>\n'
    '          <tr><td>Mwb (Body Wave)</td>'
    '<td>331° / 50° / 84°</td><td>160° / 40° / 97°</td><td>—</td></tr>\n'
    '        </tbody>\n'
    '      </table>\n'
    '      <p style="font-size:.83em;color:#94a3b8;margin-top:10px;">\n'
    '        <strong>P-ekseni:</strong> Azimüt 80°, Eğim 1° (yatay E–W sıkışma) · '
    '<strong>T-ekseni:</strong> Azimüt 343°, Eğim 81° (dik) · '
    '<strong>DC %87</strong> · Mo = 5.74 × 10²⁰ N·m<br>\n'
    '        NP2 geometrisi (gidiş ~161°, eğim ~45° batıya) Cotabato Hendeği arayüzüyle uyumludur. '
    '1976 Moro Körfezi (Mw 7.9) ile aynı sınıf: <strong>levha arayüzü (megathrust) kırılması</strong>.\n'
    '      </p>\n'
    '    </div>\n\n'
    '    <div class="info-note">\n'
    '      <strong>Cotabato Çukuru nedir?</strong>'
)

if NEEDLE in ap:
    ap = ap.replace(NEEDLE, NP_BLOCK, 1)
    print('Appendix A NP tablosu eklendi')
else:
    print('HATA: NP insertion point bulunamadi')
    idx = ap.find('Cotabato Çukuru nedir')
    print(repr(ap[max(0,idx-200):idx+50]))

d['APPENDIX_SECTIONS_HTML'] = ap

with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
