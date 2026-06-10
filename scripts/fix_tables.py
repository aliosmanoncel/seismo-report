import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)

rv = d['REVIEW_SECTION_HTML']
ap = d['APPENDIX_SECTIONS_HTML']

fixes = 0

# ── FIX 1: p-değeri tablosu — table-layout:fixed + sütun genişlikleri ──
# <br><small> içeren satırı düzelt, tabloya col genişlikleri ekle

OLD_PTABLE_OPEN = (
    '      <table style="width:100%;border-collapse:collapse;font-size:.86em;margin-top:8px;">\n'
    '          <thead><tr>\n'
    '            <th style="padding:5px 10px;background:rgba(255,255,255,.06);text-align:left;">Durum</th>\n'
    '            <th style="padding:5px 10px;background:rgba(255,255,255,.06);">p değeri</th>\n'
    '            <th style="padding:5px 10px;background:rgba(255,255,255,.06);text-align:left;">Anlam</th>\n'
    '          </tr></thead>'
)
NEW_PTABLE_OPEN = (
    '      <table style="width:100%;border-collapse:collapse;font-size:.86em;margin-top:8px;table-layout:fixed;">\n'
    '        <colgroup><col style="width:30%"><col style="width:12%"><col style="width:58%"></colgroup>\n'
    '          <thead><tr>\n'
    '            <th style="padding:5px 10px;background:rgba(255,255,255,.06);text-align:left;">Durum</th>\n'
    '            <th style="padding:5px 10px;background:rgba(255,255,255,.06);">p</th>\n'
    '            <th style="padding:5px 10px;background:rgba(255,255,255,.06);text-align:left;">Anlam</th>\n'
    '          </tr></thead>'
)
if OLD_PTABLE_OPEN in rv:
    rv = rv.replace(OLD_PTABLE_OPEN, NEW_PTABLE_OPEN, 1)
    fixes += 1
    print('FIX 1a: p tablosu table-layout:fixed eklendi')
else:
    print('MISS 1a: p tablosu başlığı bulunamadı')

# "Yavaş sönümlenme" satırındaki <br><small> → satıraltı div
OLD_SLOW_ROW = (
    '<tr style="color:#ef5350;font-weight:600;">'
    '<td style="padding:4px 10px;">Yavaş sönümlenme<br>'
    '<small style="font-weight:400;color:#ef9a9a;">Yüksek Sismik Kalıcılık</small></td>'
)
NEW_SLOW_ROW = (
    '<tr style="color:#ef5350;font-weight:600;">'
    '<td style="padding:4px 10px;line-height:1.4;">Yavaş sönümlenme'
    '<div style="font-size:.82em;font-weight:400;color:#ef9a9a;margin-top:2px;">Yüksek Sismik Kalıcılık</div></td>'
)
if OLD_SLOW_ROW in rv:
    rv = rv.replace(OLD_SLOW_ROW, NEW_SLOW_ROW, 1)
    fixes += 1
    print('FIX 1b: Yavaş sönümlenme <br><small> → <div> düzeltildi')
else:
    print('MISS 1b: Yavaş satırı bulunamadı')

# ── FIX 2: FTLS grid — mobilde üst üste gelsin (flex-wrap) ──────────
OLD_FTLS_GRID = 'display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;'
NEW_FTLS_GRID = 'display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:12px 0;'
if OLD_FTLS_GRID in rv:
    rv = rv.replace(OLD_FTLS_GRID, NEW_FTLS_GRID, 1)
    fixes += 1
    print('FIX 2: FTLS grid responsive yapıldı')
else:
    print('MISS 2: FTLS grid bulunamadı')

# ── FIX 3: Tablo 1 — Derinlik sütunu overflow sorunu ────────────────
# USGS satırındaki uzun "55.2 (hipo) / 35.5 (W-faz santroid)" metni
OLD_USGS_DEPTH = '<td>55.2 (hipo) / 35.5 (W-faz santroid)</td>'
NEW_USGS_DEPTH = '<td style="font-size:.82em;line-height:1.4;">55.2 km hipo<br>35.5 km santroid (W-faz)</td>'
if OLD_USGS_DEPTH in rv:
    rv = rv.replace(OLD_USGS_DEPTH, NEW_USGS_DEPTH, 1)
    fixes += 1
    print('FIX 3: Tablo 1 USGS derinlik hücresi düzeltildi')
else:
    print('MISS 3: Tablo 1 USGS derinlik hücresi bulunamadı')

# ── FIX 4: Tablo 1'e table-layout:fixed + col genişlikleri ──────────
OLD_T1_OPEN = '<table class="review-table">\n      <caption>Tablo 1.'
NEW_T1_OPEN = (
    '<table class="review-table" style="table-layout:fixed;word-break:break-word;">\n'
    '      <colgroup>'
    '<col style="width:14%">'   # Ajans
    '<col style="width:15%">'   # Tarih-Saat
    '<col style="width:9%">'    # Enlem
    '<col style="width:9%">'    # Boylam
    '<col style="width:20%">'   # Derinlik
    '<col style="width:12%">'   # Büyüklük
    '<col style="width:21%">'   # Mekanizma
    '</colgroup>\n'
    '      <caption>Tablo 1.'
)
if OLD_T1_OPEN in rv:
    rv = rv.replace(OLD_T1_OPEN, NEW_T1_OPEN, 1)
    fixes += 1
    print('FIX 4: Tablo 1 col genişlikleri eklendi')
else:
    print('MISS 4: Tablo 1 bulunamadı')

# ── FIX 5: Tablo 2 (NP) — col genişlikleri ──────────────────────────
OLD_T2_OPEN = '<table class="review-table" style="margin:12px 0 18px;">'
NEW_T2_OPEN = '<table class="review-table" style="margin:12px 0 18px;table-layout:fixed;word-break:break-word;">\n      <colgroup><col style="width:22%"><col style="width:26%"><col style="width:26%"><col style="width:26%"></colgroup>'
if OLD_T2_OPEN in rv:
    rv = rv.replace(OLD_T2_OPEN, NEW_T2_OPEN, 1)
    fixes += 1
    print('FIX 5: Tablo 2 (NP) col genişlikleri eklendi')
else:
    print('MISS 5: Tablo 2 (NP) bulunamadı')

# ── FIX 6: Appendix A — NP tablosu col genişlikleri ─────────────────
OLD_AP_T = '<table class="review-table" style="font-size:.88em;margin-top:8px;">'
NEW_AP_T = '<table class="review-table" style="font-size:.88em;margin-top:8px;table-layout:fixed;word-break:break-word;"><colgroup><col style="width:24%"><col style="width:25%"><col style="width:25%"><col style="width:26%"></colgroup>'
if OLD_AP_T in ap:
    ap = ap.replace(OLD_AP_T, NEW_AP_T, 1)
    fixes += 1
    print('FIX 6: Appendix A NP tablosu col genişlikleri eklendi')
else:
    print('MISS 6: Appendix A NP tablosu bulunamadı')

d['REVIEW_SECTION_HTML'] = rv
d['APPENDIX_SECTIONS_HTML'] = ap

with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print(f'\n{fixes} düzeltme uygulandı — JSON kaydedildi')
