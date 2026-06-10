"""
embed_psha_figures.py
PSHA ve Logic Tree PNG dosyalarını base64 olarak PAGE JSON'a gömer.
"""
import json, base64, sys
sys.stdout.reconfigure(encoding='utf-8')

def img_b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')

b64_psha = img_b64('OUTPUT/PSHA/Mindanao_PSHA_v3.png')
b64_lt   = img_b64('OUTPUT/PSHA/Mindanao_LogicTree.png')

FIG_HTML = f"""
    <div style="margin:16px 0;">
      <figure style="margin:0;">
        <img src="data:image/png;base64,{b64_psha}"
             style="width:100%;border-radius:6px;border:1px solid rgba(100,181,246,.25);"
             alt="Mindanao PSHA Tehlike Eğrisi">
        <figcaption style="font-size:.78em;color:#90a4ae;margin-top:4px;text-align:center;">
          Şekil 6e-1 — Mindanao Mw 7.8 PSHA: PGA Tehlike Eğrisi ve Belirsizlik Bantları
          (Youngs vd. 1988 GMPE | Baker, Bradley &amp; Stafford 2021 §6 |
          General Santos City, Vs30=360 m/s, R=58.1 km)
        </figcaption>
      </figure>
    </div>
    <div style="margin:16px 0;">
      <figure style="margin:0;">
        <img src="data:image/png;base64,{b64_lt}"
             style="width:100%;border-radius:6px;border:1px solid rgba(100,181,246,.25);"
             alt="Mindanao Logic Tree PSHA">
        <figcaption style="font-size:.78em;color:#90a4ae;margin-top:4px;text-align:center;">
          Şekil 6e-2 — Logic Tree PSHA: 27 Dal, Epistemik Belirsizlik Fraktilleri
          (P1: b=0.635/0.90/1.12 | P2: Interface/+0.5σ/Intraslab |
          P3: M<sub>max</sub>=7.8/8.0/8.2 | Baker, Bradley &amp; Stafford 2021 §7.3)
        </figcaption>
      </figure>
    </div>
"""

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# Section 6e içindeki tablodan hemen sonra, info-note'tan önce görselleri ekle
OLD_ANCHOR = '    <div class="info-note" style="border-color:rgba(229,57,53,.4)'
NEW_ANCHOR = FIG_HTML + '\n    <div class="info-note" style="border-color:rgba(229,57,53,.4)'

if OLD_ANCHOR in rv:
    rv = rv.replace(OLD_ANCHOR, NEW_ANCHOR, 1)
    print('PAGE: PSHA görselleri gömüldü')
else:
    print('MISS: info-note anchor')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
