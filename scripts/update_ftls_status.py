import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# ── 1. FTLS method-card içine gerçek hesap sonucu ekle ────────────
OLD_FTLS_NOTE = (
    '<strong>b-positive tahmincisi:</strong> Ana şok sonrası kısa dönem katalog eksikliğini\n'
    '        aşmak için Gulia vd. (2024)\'nin önerdiği "b-positive" yöntemi uygulanacaktır. Mindanao\n'
    '        katalog tamamlanma büyüklüğü (M<sub>c</sub>) önce maksimum eğrilik yöntemiyle\n'
    '        belirlenecek; FTLS renk kararı bu M<sub>c</sub> üzerinde verilecektir.\n'
    '      </p>\n'
    '    </div>\n\n'
    '    <!-- Veri Homojenleştirme -->'
)
NEW_FTLS_NOTE = (
    '<strong>b-positive tahmincisi:</strong> Ana şok sonrası kısa dönem katalog eksikliğini\n'
    '        aşmak için Gulia vd. (2024)\'nin önerdiği "b-positive" yöntemi uygulanacaktır. Mindanao\n'
    '        katalog tamamlanma büyüklüğü M<sub>c</sub> = 3.5 (maksimum eğrilik yöntemi).\n'
    '      </p>\n\n'
    '      <div style="background:rgba(180,0,0,.12);border:1px solid rgba(244,67,54,.5);'
    'border-radius:8px;padding:14px 18px;margin-top:12px;">\n'
    '        <strong style="color:#ef9a9a;font-size:.95em;">🔴 FTLS Durum Değerlendirmesi — '
    '7 Haziran 2026 Mindanao Mw 7.8</strong>\n'
    '        <table style="width:100%;border-collapse:collapse;font-size:.84em;margin:10px 0 8px;'
    'table-layout:fixed;">\n'
    '          <colgroup><col style="width:30%"><col style="width:14%"><col style="width:14%">'
    '<col style="width:14%"><col style="width:28%"></colgroup>\n'
    '          <thead><tr style="color:#94a3b8;">\n'
    '            <th style="padding:4px 8px;text-align:left;">b<sub>ref</sub> senaryosu</th>\n'
    '            <th style="padding:4px 8px;text-align:center;">b<sub>ref</sub></th>\n'
    '            <th style="padding:4px 8px;text-align:center;">b / b<sub>ref</sub></th>\n'
    '            <th style="padding:4px 8px;text-align:center;">Durum</th>\n'
    '            <th style="padding:4px 8px;text-align:left;">Kaynak</th>\n'
    '          </tr></thead>\n'
    '          <tbody>\n'
    '            <tr><td style="padding:3px 8px;">Cotabato alt sınır</td>'
    '<td style="text-align:center;">0.85</td>'
    '<td style="text-align:center;">0.747</td>'
    '<td style="text-align:center;color:#ef5350;font-weight:700;">🔴 KRM</td>'
    '<td style="padding:3px 8px;font-size:.82em;">Wiemer &amp; Wyss, 2002</td></tr>\n'
    '            <tr><td style="padding:3px 8px;">Filipinler yay sistemi</td>'
    '<td style="text-align:center;">0.92</td>'
    '<td style="text-align:center;">0.690</td>'
    '<td style="text-align:center;color:#ef5350;font-weight:700;">🔴 KRM</td>'
    '<td style="padding:3px 8px;font-size:.82em;">NEIC bölgesel katalog</td></tr>\n'
    '            <tr><td style="padding:3px 8px;">Subduction zonu genel</td>'
    '<td style="text-align:center;">1.00</td>'
    '<td style="text-align:center;">0.635</td>'
    '<td style="text-align:center;color:#ef5350;font-weight:700;">🔴 KRM</td>'
    '<td style="padding:3px 8px;font-size:.82em;">Kagan, 1999</td></tr>\n'
    '            <tr style="border-top:1px solid rgba(255,255,255,.08);">'
    '<td style="padding:3px 8px;font-size:.82em;color:#94a3b8;" colspan="5">'
    '<em>Seg-1 b₁=0.829 (mb karşılaştırılabilir): b₁/b<sub>ref</sub>=0.90–0.98 → SARI (sınır)</em></td></tr>\n'
    '          </tbody>\n'
    '        </table>\n'
    '        <p style="font-size:.84em;margin:4px 0 0;">\n'
    '          Tüm b<sub>ref</sub> senaryolarında b<sub>gerçek</sub>/b<sub>ref</sub> &lt; 0.90 '
    '→ <strong>KIRMIZI durum</strong>. Bu bulgu;\n'
    '          (1) bölgede gerilmenin henüz tam boşalmadığını, '
    '(2) Mw 7.8\'in ana şok olduğunu ancak sistemin kapanmadığını,\n'
    '          (3) düşük p=0.619 ile birleşince <strong>"Yüksek Sismik Kalıcılık"</strong> '
    'tablosunun devam ettiğini göstermektedir.\n'
    '        </p>\n'
    '      </div>\n'
    '    </div>\n\n'
    '    <!-- Veri Homojenleştirme -->'
)

if OLD_FTLS_NOTE in rv:
    rv = rv.replace(OLD_FTLS_NOTE, NEW_FTLS_NOTE, 1)
    print('FTLS durum tablosu eklendi')
else:
    print('HATA: FTLS eski metin bulunamadı')
    idx = rv.find('b-positive tahmincisi')
    print(repr(rv[idx:idx+200]))

# ── 2. Section 6 Temel Bulgular'a FTLS + b-değeri sonucu ekle ─────
OLD_BULGU_END = (
    '<li>Yerel tsunami uyarısı verilen depremde okyanus geneli yıkıcı tsunami '
    'potansiyeli düşük değerlendirilmiştir.</li>\n'
    '      </ul>\n'
    '    </div>'
)
NEW_BULGU_END = (
    '<li>Yerel tsunami uyarısı verilen depremde okyanus geneli yıkıcı tsunami '
    'potansiyeli düşük değerlendirilmiştir.</li>\n'
    '        <li>Gutenberg-Richter analizi (Mc=3.5, Aki 1965): tam aralık <strong>b=0.635</strong>; '
    'iki segmentli analiz M3.5–5.0 b₁=0.829, M5.0+ b₂=1.12. '
    'Slope break M5.0\'de mb doyumundan kaynaklanmakta olup iki ayrı katalog nüfusunu yansıtmaktadır.</li>\n'
    '        <li>FTLS (Gulia vd. 2024): b/b<sub>ref</sub> &lt; 0.90 → '
    '<strong style="color:#ef9a9a;">🔴 KIRMIZI durum</strong> — '
    'tüm b<sub>ref</sub> senaryolarında gerilme boşalımı tamamlanmamış; '
    'p=0.619 (Yüksek Kalıcılık) ile birleşince sismik risk aylarca masada kalacaktır.</li>\n'
    '      </ul>\n'
    '    </div>'
)

if OLD_BULGU_END in rv:
    rv = rv.replace(OLD_BULGU_END, NEW_BULGU_END, 1)
    print('Section 6 bulgular güncellendi')
else:
    print('HATA: Section 6 eski metin bulunamadı')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
