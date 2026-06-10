"""Figure B1 SVG'yi Appendix B'ye göm ve raporu yeniden üret."""
import json, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')

SVG_HTML = """<figure style="margin:20px 0;">
<svg viewBox="0 0 780 680" xmlns="http://www.w3.org/2000/svg" font-family="'Segoe UI',sans-serif" role="img" style="width:100%;max-width:780px;display:block;border-radius:8px;">
  <title>Figure B1 &#8212; Epicentral Area Map (R approx 250 km), Mindanao Mw 7.8, 7 June 2026</title>
  <defs>
    <clipPath id="mc"><rect x="55" y="45" width="670" height="555"/></clipPath>
    <filter id="eglow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softg" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="seapat" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse">
      <rect width="8" height="8" fill="#07192e"/>
      <line x1="0" y1="8" x2="8" y2="0" stroke="rgba(59,120,180,0.06)" stroke-width="0.5"/>
    </pattern>
  </defs>
  <!-- Outer frame -->
  <rect x="0" y="0" width="780" height="680" fill="#06101e" rx="3"/>
  <!-- Sea -->
  <rect x="55" y="45" width="670" height="555" fill="url(#seapat)" rx="2"/>
  <!-- Grid -->
  <g stroke="rgba(80,140,200,0.13)" stroke-width="0.7" fill="none" clip-path="url(#mc)">
    <line x1="106.5" y1="45" x2="106.5" y2="600"/>
    <line x1="209.6" y1="45" x2="209.6" y2="600"/>
    <line x1="312.7" y1="45" x2="312.7" y2="600"/>
    <line x1="415.8" y1="45" x2="415.8" y2="600"/>
    <line x1="518.9" y1="45" x2="518.9" y2="600"/>
    <line x1="621.9" y1="45" x2="621.9" y2="600"/>
    <line x1="55" y1="87.7"  x2="725" y2="87.7"/>
    <line x1="55" y1="173.1" x2="725" y2="173.1"/>
    <line x1="55" y1="258.5" x2="725" y2="258.5"/>
    <line x1="55" y1="343.8" x2="725" y2="343.8"/>
    <line x1="55" y1="429.2" x2="725" y2="429.2"/>
    <line x1="55" y1="514.6" x2="725" y2="514.6"/>
    <line x1="55" y1="600"   x2="725" y2="600"/>
  </g>
  <!-- Mindanao island polygon (simplified, CW from NW coast incl. Zamboanga peninsula) -->
  <polygon clip-path="url(#mc)"
    points="189,130.4 261.2,87.7 343.6,62.1 395.2,45 467.3,45 518.8,62.1 549.8,113.3 570.4,173.1 570.4,232.8 549.8,301.2 518.8,369.5 467.3,429.2 374.5,429.2 312.7,386.5 261.2,343.8 209.6,301.2 127.2,301.2 65.3,275.5 85.9,258.5 106.5,232.8 158.1,215.8 158.1,173.1"
    fill="#1e2d14" stroke="#3d5c24" stroke-width="1.3"/>
  <!-- Interior highlands hint -->
  <ellipse cx="390" cy="240" rx="90" ry="70" fill="rgba(45,65,28,0.5)" clip-path="url(#mc)"/>
  <!-- Cotabato basin -->
  <ellipse cx="350" cy="295" rx="55" ry="40" fill="rgba(30,50,18,0.8)" clip-path="url(#mc)"/>
  <!-- Sea labels -->
  <text x="155" y="490" fill="rgba(59,120,180,0.55)" font-size="10" text-anchor="middle" font-style="italic" transform="rotate(-8,155,490)">MORO</text>
  <text x="155" y="503" fill="rgba(59,120,180,0.55)" font-size="10" text-anchor="middle" font-style="italic" transform="rotate(-8,155,503)">GULF</text>
  <text x="370" y="488" fill="rgba(59,120,180,0.5)" font-size="11" text-anchor="middle" font-style="italic">CELEBES SEA</text>
  <text x="655" y="235" fill="rgba(59,120,180,0.5)" font-size="10" text-anchor="middle" font-style="italic" transform="rotate(-75,655,235)">PHILIPPINE SEA</text>
  <text x="508" y="340" fill="rgba(59,120,180,0.45)" font-size="9" text-anchor="middle" font-style="italic">Davao Gulf</text>
  <!-- Island name -->
  <text x="420" y="195" fill="rgba(120,160,80,0.6)" font-size="14" font-weight="700" text-anchor="middle" letter-spacing="4" transform="rotate(-3,420,195)">MINDANAO</text>
  <!-- 250 km radius ellipse -->
  <ellipse cx="421.7" cy="371.0" rx="232.7" ry="191.8"
    fill="rgba(255,140,0,0.06)" stroke="#ff8c00" stroke-width="1.8"
    stroke-dasharray="9 6" opacity="0.9" clip-path="url(#mc)"/>
  <text x="421.7" y="173" fill="#ff8c00" font-size="10" text-anchor="middle" font-weight="600">R &#8776; 250 km</text>
  <!-- Epicenter star -->
  <g transform="translate(421.7,371.0)" filter="url(#eglow)">
    <polygon points="0,-16 3.8,-5.3 14.2,-4.9 6.4,2.1 9.2,12.8 0,6.8 -9.2,12.8 -6.4,2.1 -14.2,-4.9 -3.8,-5.3"
      fill="#ff2222" stroke="#ffaaaa" stroke-width="0.8"/>
  </g>
  <text x="421.7" y="398" fill="#ff6666" font-size="9" text-anchor="middle">Mw 7.8 &#183; 7 Jun 2026</text>
  <text x="421.7" y="409" fill="#ff6666" font-size="8.5" text-anchor="middle">5.68&#176;N 125.06&#176;E</text>
  <!-- Cities -->
  <circle cx="433.6" cy="334.4" r="4.5" fill="#d4e8f8" stroke="#06101e" stroke-width="1.2" filter="url(#softg)"/>
  <text x="441" y="330" fill="#d4e8f8" font-size="10" font-weight="600">General Santos</text>
  <text x="441" y="341" fill="#94afc8" font-size="8.5">46 km N</text>
  <circle cx="479.0" cy="252.3" r="4.5" fill="#d4e8f8" stroke="#06101e" stroke-width="1.2" filter="url(#softg)"/>
  <text x="487" y="248" fill="#d4e8f8" font-size="10" font-weight="600">Davao</text>
  <text x="487" y="259" fill="#94afc8" font-size="8.5">163 km N</text>
  <circle cx="338.5" cy="239.5" r="4.5" fill="#d4e8f8" stroke="#06101e" stroke-width="1.2" filter="url(#softg)"/>
  <text x="330" y="235" fill="#d4e8f8" font-size="10" font-weight="600" text-anchor="end">Cotabato</text>
  <text x="330" y="246" fill="#94afc8" font-size="8.5" text-anchor="end">~168 km NW</text>
  <circle cx="400.0" cy="300.9" r="4.5" fill="#d4e8f8" stroke="#06101e" stroke-width="1.2" filter="url(#softg)"/>
  <text x="392" y="296" fill="#d4e8f8" font-size="10" font-weight="600" text-anchor="end">Koronadal</text>
  <text x="392" y="307" fill="#94afc8" font-size="8.5" text-anchor="end">~97 km N</text>
  <circle cx="452.2" cy="279.9" r="4.5" fill="#d4e8f8" stroke="#06101e" stroke-width="1.2" filter="url(#softg)"/>
  <text x="460" y="276" fill="#d4e8f8" font-size="10" font-weight="600">Digos</text>
  <text x="460" y="287" fill="#94afc8" font-size="8.5">~130 km N</text>
  <!-- Map frame -->
  <rect x="55" y="45" width="670" height="555" fill="none" stroke="rgba(100,160,220,0.3)" stroke-width="1"/>
  <!-- Lon axis labels -->
  <g fill="#6a8fa8" font-size="10" text-anchor="middle">
    <text x="106.5" y="626">122&#176;E</text>
    <text x="209.6" y="626">123&#176;E</text>
    <text x="312.7" y="626">124&#176;E</text>
    <text x="415.8" y="626">125&#176;E</text>
    <text x="518.9" y="626">126&#176;E</text>
    <text x="621.9" y="626">127&#176;E</text>
  </g>
  <!-- Lat axis labels -->
  <g fill="#6a8fa8" font-size="10" text-anchor="end">
    <text x="50" y="91">9&#176;N</text>
    <text x="50" y="177">8&#176;N</text>
    <text x="50" y="262">7&#176;N</text>
    <text x="50" y="348">6&#176;N</text>
    <text x="50" y="433">5&#176;N</text>
    <text x="50" y="519">4&#176;N</text>
    <text x="50" y="604">3&#176;N</text>
  </g>
  <!-- Legend box -->
  <rect x="578" y="435" width="145" height="110" fill="rgba(6,16,30,0.88)" stroke="rgba(100,160,220,0.2)" stroke-width="0.8" rx="6"/>
  <text x="650" y="452" fill="#90caf9" font-size="10" font-weight="700" text-anchor="middle" letter-spacing="1">LEGEND</text>
  <g transform="translate(592,467)" filter="url(#eglow)">
    <polygon points="0,-8 1.9,-2.6 7.1,-2.5 3.2,1.0 4.6,6.4 0,3.4 -4.6,6.4 -3.2,1.0 -7.1,-2.5 -1.9,-2.6"
      fill="#ff2222" stroke="#ffaaaa" stroke-width="0.5"/>
  </g>
  <text x="604" y="470" fill="#e0ecf8" font-size="9">Epicenter Mw 7.8</text>
  <line x1="585" y1="483" x2="600" y2="483" stroke="#ff8c00" stroke-width="1.8" stroke-dasharray="5 3"/>
  <text x="604" y="486" fill="#e0ecf8" font-size="9">R &#8776; 250 km radius</text>
  <circle cx="592" cy="497" r="3.5" fill="#d4e8f8" stroke="#06101e" stroke-width="0.8"/>
  <text x="600" y="500" fill="#e0ecf8" font-size="9">City / Settlement</text>
  <text x="592" y="516" fill="#4a6a8a" font-size="8">EMSC / USGS-NEIC (2026)</text>
  <text x="592" y="526" fill="#4a6a8a" font-size="8">Equirectangular proj.</text>
  <text x="592" y="536" fill="#4a6a8a" font-size="8">Outline: simplified</text>
  <!-- Scale bar (100 km = 93.1 px at 6N) -->
  <g transform="translate(75,578)">
    <line x1="0" y1="0" x2="186.2" y2="0" stroke="#a0b8cc" stroke-width="1.5"/>
    <line x1="0"     y1="-6" x2="0"     y2="4" stroke="#a0b8cc" stroke-width="1.5"/>
    <line x1="93.1"  y1="-4" x2="93.1"  y2="4" stroke="#a0b8cc" stroke-width="1"/>
    <line x1="186.2" y1="-6" x2="186.2" y2="4" stroke="#a0b8cc" stroke-width="1.5"/>
    <rect x="0"    y="-5" width="93.1" height="5" fill="rgba(160,184,204,0.25)"/>
    <rect x="93.1" y="-5" width="93.1" height="5" fill="rgba(160,184,204,0.1)"/>
    <text x="0"     y="14" fill="#8aaec8" font-size="9" text-anchor="middle">0</text>
    <text x="93.1"  y="14" fill="#8aaec8" font-size="9" text-anchor="middle">100</text>
    <text x="186.2" y="14" fill="#8aaec8" font-size="9" text-anchor="middle">200 km</text>
  </g>
  <!-- North arrow -->
  <g transform="translate(720,558)">
    <polygon points="0,-18 5,5 0,2 -5,5" fill="#c8dce8"/>
    <polygon points="0,2 5,5 0,18 -5,5" fill="rgba(200,220,235,0.25)" stroke="#c8dce8" stroke-width="0.8"/>
    <text x="0" y="-22" fill="#c8dce8" font-size="12" text-anchor="middle" font-weight="700">N</text>
  </g>
  <!-- Caption inside SVG -->
  <text x="390" y="651" fill="#7a95ae" font-size="10" text-anchor="middle">
    Figure B1 &#8212; Epicentral Area Map (R &#8776; 250 km) &#183; Mindanao Mw 7.8 &#183; 7 June 2026 &#183; Sources: EMSC / USGS-NEIC
  </text>
</svg>
<figcaption class="figure-caption">
  <b>Figure B1</b> &#8212; Epicentral Area Map (R &#8776; 250 km). Red star: June 7, 2026 Mindanao Mw 7.8 epicenter (5.68&#176;N, 125.06&#176;E).
  Orange dashed circle: ~250 km radius of impact. City points: General Santos (46 km N), Davao (163 km N),
  Cotabato (~168 km NW), Koronadal (~97 km N), Digos (~130 km N).
  Equirectangular projection; island outline simplified.
  Seismological source: EMSC / USGS/NEIC (2026).
</figcaption>
</figure>"""

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)

app = d['APPENDIX_SECTIONS_HTML']

# Appendix B panel-appB icinde, tanim paragrafinin ardindan SVG ekle
NEEDLE = '</p>\n    <div class="analysis-card">'
if NEEDLE not in app:
    # Fallback: panel-appB icinde ilk </p>'yi bul
    idx = app.find('id="panel-appB"')
    p_end = app.find('</p>', idx)
    if p_end == -1:
        print('HATA: insertion point bulunamadi'); raise SystemExit(1)
    app = app[:p_end+4] + '\n    ' + SVG_HTML + app[p_end+4:]
else:
    # Sadece panel-appB icindeki ilk NEEDLE
    idx_panel = app.find('id="panel-appB"')
    idx_needle = app.find(NEEDLE, idx_panel)
    app = app[:idx_needle+len('</p>\n')] + '    ' + SVG_HTML + '\n    ' + app[idx_needle+len('</p>\n'):]

d['APPENDIX_SECTIONS_HTML'] = app
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON guncellendi')

# generate.py ile HTML uret
result = subprocess.run(['python', 'generate.py', 'INPUT/Mindanao-2026.json'],
                        capture_output=True, text=True, encoding='utf-8')
print(result.stdout.strip())
if result.returncode != 0:
    print('HATA:', result.stderr[:300])
