"""Build EMSC testimonies Appendix E and inject into Mindanao-2026.json"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

RAW = (
    "Witness location : General Santos (Philippines) (46 km N from epicenter)\n"
    "Time : T0+ 5 min\nMassive lots damage\n"
    "Witness location : General Santos (Philippines) (52 km N from epicenter)\n"
    "Time : T0+ 73 min\nRude awakening, multiple aftershocks. Actually couldn't stand up when it began.\n"
    "Witness location : Dahay (Philippines) (85 km NW from epicenter)\n"
    "Time : T0+ 4 min\nIts very strong and scary.. it reaaly shake things all arpund violently\n"
    "Witness location : Kidapawan (Philippines) (149 km N from epicenter)\n"
    "Time : T0+ 23 min\nWhole house shook for about a minute, lost about 4 inches of water out of the pool.\n"
    "Witness location : Bato (Philippines) (154 km N from epicenter)\n"
    "Time : T0+ 23 min\nit was very strong for possibly 1-2 minutrs\n"
    "Witness location : Bato (Philippines) (159 km N from epicenter)\n"
    "Time : T0+ 9 min\nI wake up the bed shaking, grab the dogs and phone.\n"
    "Witness location : Davao (Philippines) (160 km N from epicenter)\n"
    "Time : T0+ 13 min\nCan be strongly felt at Davao City.\n"
    "Witness location : Davao City (Philippines) (163 km N from epicenter)\n"
    "Time : T0+ 26 min\n7:37 AM followed by 7:49 AM 10 secs aftershoock\n"
    "Witness location : Davao (Philippines) (164 km N from epicenter)\n"
    "Time : T0+ 26 min\nIts strong\n"
    "Witness location : Biao (Philippines) (168 km N from epicenter)\n"
    "Time : T0+ 59 min\nHefty shaking for more than 2 or maybe 3 minutes\n"
    "Witness location : Davao (Philippines) (169 km N from epicenter)\n"
    "Time : T0+ 764 min\nstrong, long, scary. power went out\n"
    "Witness location : Babak (Philippines) (173 km N from epicenter)\n"
    "Time : T0+ 3 min\nDavao City heavy 7.6?\n"
    "Witness location : Babak (Philippines) (173 km N from epicenter)\n"
    "Time : T0+ 9 min\nWe felt that in Davao City Communal quote big in movement\n"
    "Witness location : San Antonio (Philippines) (181 km NE from epicenter)\n"
    "Time : T0+ 9 min\nStrong and more than 2 minutes long. Loads of water sloshed out of the pool.\n"
    "Witness location : Mati (Philippines) (192 km NE from epicenter)\n"
    "Time : T0+ 5 min\nSlow quake, then everything was trembling and vibrating, and then it slows down again\n"
    "Witness location : Magugpo Poblacion (Philippines) (211 km N from epicenter)\n"
    "Time : T0+ 22 min\nStrong shock traffic stopped\n"
    "Witness location : Kibureau (Philippines) (223 km N from epicenter)\n"
    "Time : T0+ 5 min\nLight shaking\n"
    "Witness location : Montevista (Philippines) (248 km NE from epicenter)\n"
    "Time : T0+ 3 min\nDavao de oro\n"
    "Witness location : Maria Cristina (Philippines) (290 km NW from epicenter)\n"
    "Time : T0+ 29 min\nIligan city\n"
    "Witness location : Iligan (Philippines) (297 km NW from epicenter)\n"
    "Time : T0+ 4 min\nIligan City, Lanao del Norte, Mindanao\n"
    "Witness location : Pagadian (Philippines) (300 km NW from epicenter)\n"
    "Time : T0+ 4 min\nshort mild shaking\n"
    "Witness location : Cagayan de Oro (Philippines) (307 km NW from epicenter)\n"
    "Time : T0+ 6 min\nDizzy\n"
    "Witness location : Cagayan de Oro (Philippines) (311 km NW from epicenter)\n"
    "Time : T0+ 15 min\nStrongest I have felt in a while.. Whole floor was literally moving\n"
    "Witness location : Cagayan de Oro (Philippines) (312 km NW from epicenter)\n"
    "Time : T0+ 4 min\n4\n"
    "Witness location : Cagayan de Oro (Philippines) (314 km NW from epicenter)\n"
    "Time : T0+ 6 min\nNo damage on the walls but doors were swinging gently as well as the chandelier\n"
    "Witness location : Bugo (Philippines) (314 km NW from epicenter)\n"
    "Time : T0+ 9 min\nIt lasted longer. Really scary\n"
    "Witness location : Alegria (Philippines) (329 km N from epicenter)\n"
    "Time : T0+ 48 min\nVery strong shaking for around one minute. Very different than typical earthquakes.\n"
    "Witness location : Butuan (Philippines) (363 km N from epicenter)\n"
    "Time : T0+ 6 min\nEveryone is poised outside of the house or by the doors for easy exit\n"
    "Witness location : Pandan (Philippines) (391 km NW from epicenter)\n"
    "Time : T0+ 7 min\nVisible shaking\n"
    "Witness location : Placer (Philippines) (441 km N from epicenter)\n"
    "Time : T0+ 200 min\nthere's no damage\n"
    "Witness location : Wori (Indonesia) (455 km S from epicenter)\n"
    "Time : T0+ 7 min\nIm here on vacation i was on the toilet haha so yea\n"
    "Witness location : Bitung (Indonesia) (467 km S from epicenter)\n"
    "Time : T0+ 17 min\nFelt it like for a good minute constantly light shaking.\n"
    "Witness location : General Luna (Philippines) (471 km N from epicenter)\n"
    "Time : T0+ 7 min\nDoor lightly swinging\n"
    "Witness location : Semporna (Malaysia) (728 km W from epicenter)\n"
    "Time : T0+ 6 min\nFelt it in semporna sabah\n"
    "Witness location : Surabaya (Indonesia) (1987 km SW from epicenter)\n"
    "Time : T0+ 60 min\nI felt cracking sounds, came out of the building and waited in a stable area.\n"
    "Witness location : Patong (Thailand) (2968 km W from epicenter)\n"
    "Time : T0+ 244 min\nYesterday at approx. 3pm in Phuket. Light, perhaps below 4.0 scale"
)

# ── Parse ──────────────────────────────────────────────────────────
witnesses = []
blocks = re.split(r'\nWitness location : ', RAW.strip())
for b in blocks:
    if not b.strip():
        continue
    lines = b.strip().splitlines()
    loc_line = lines[0].strip()
    m = re.match(r'^(.+?)\s+\((\d+)\s+km\s+(\w+)\s+from epicenter\)', loc_line)
    if not m:
        continue
    loc   = m.group(1).strip()
    dist  = int(m.group(2))
    direc = m.group(3)
    t_m   = re.search(r'T0\+\s*(\d+)', lines[1] if len(lines) > 1 else '')
    t_min = int(t_m.group(1)) if t_m else 0
    desc_lines = [l.strip() for l in lines[2:] if l.strip()]
    desc = ' '.join(desc_lines)[:220]
    witnesses.append({'loc': loc, 'dist': dist, 'dir': direc, 't_min': t_min, 'desc': desc})

witnesses.sort(key=lambda x: x['dist'])
max_dist = max(w['dist'] for w in witnesses)
print(f"{len(witnesses)} taniklik, max {max_dist} km")

# ── Renk ──────────────────────────────────────────────────────────
def dist_style(d):
    if d < 100:   return '#ff2222', 'Hasar b&#246;lgesi'
    if d < 300:   return '#ff8800', '&#350;iddetli'
    if d < 500:   return '#ffd600', 'Orta'
    if d < 1000:  return '#44ff88', 'Hafif'
    return               '#44aaff', '&#199;ok uzak'

# ── Tablo satirlari ────────────────────────────────────────────────
rows = ''
for w in witnesses:
    col, lbl = dist_style(w['dist'])
    rows += (
        f'<tr style="border-bottom:1px solid rgba(255,255,255,.06);">'
        f'<td style="padding:7px 10px;color:{col};font-weight:700;white-space:nowrap">{w["dist"]}&nbsp;km&nbsp;{w["dir"]}</td>'
        f'<td style="padding:7px 10px;color:#c8d8e8;font-size:.88em">{w["loc"]}</td>'
        f'<td style="padding:7px 10px;color:#7a9ab5;font-size:.82em;white-space:nowrap">T0+{w["t_min"]}&nbsp;dak</td>'
        f'<td style="padding:7px 10px;color:#e0eaf5;font-size:.84em;line-height:1.5">{w["desc"]}</td>'
        f'<td style="padding:7px 6px"><span style="background:rgba(0,0,0,.3);color:{col};'
        f'border:1px solid {col}66;border-radius:4px;padding:2px 7px;font-size:.75em;white-space:nowrap">{lbl}</span></td>'
        f'</tr>\n'
    )

EMSC_URL = 'https://www.emsc-csem.org/Earthquake_information/earthquake_testimonies.php?id=2006895'

PANEL = f"""<div class="analysis-card">
      <h4>&#128227; EMSC Saha Tank&#305;l&#305;klar&#305; &#8212; {len(witnesses)} Rapor &bull; Maks. {max_dist:,} km</h4>
      <p style="color:#94a3b8;font-size:.86em;margin:0 0 14px">
        Kaynak: <a href="{EMSC_URL}" target="_blank" rel="noopener" style="color:#90caf9;">
        EMSC&#8209;CSEM Vatanda&#351; Bildirimleri &#8212; Olay #2006895</a><br>
        Filipinler, Endonezya, Malezya ve Tayland&#8217;dan {len(witnesses)} tan&#305;kl&#305;k bildirimi;
        hissedilme alan&#305; General Santos (46 km) &#8212; Patong/Phuket, Tayland (2&#8202;968 km).
      </p>

      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">
        <span style="background:rgba(255,34,34,.15);color:#ff2222;border:1px solid #ff222244;border-radius:6px;padding:3px 11px;font-size:.81em">&#9679; &lt;100 km &#8212; Hasar</span>
        <span style="background:rgba(255,136,0,.15);color:#ff8800;border:1px solid #ff880044;border-radius:6px;padding:3px 11px;font-size:.81em">&#9679; 100&#8211;300 km &#8212; &#350;iddetli</span>
        <span style="background:rgba(255,214,0,.15);color:#ffd600;border:1px solid #ffd60044;border-radius:6px;padding:3px 11px;font-size:.81em">&#9679; 300&#8211;500 km &#8212; Orta</span>
        <span style="background:rgba(68,255,136,.12);color:#44ff88;border:1px solid #44ff8840;border-radius:6px;padding:3px 11px;font-size:.81em">&#9679; 500&#8211;1000 km &#8212; Hafif</span>
        <span style="background:rgba(68,170,255,.12);color:#44aaff;border:1px solid #44aaff40;border-radius:6px;padding:3px 11px;font-size:.81em">&#9679; &gt;1000 km &#8212; &#199;ok uzak</span>
      </div>

      <div style="overflow-x:auto;">
      <table style="width:100%;border-collapse:collapse;font-size:.84em;">
        <thead>
          <tr style="background:rgba(59,158,255,.1);border-bottom:1px solid rgba(59,158,255,.3);">
            <th style="padding:8px 10px;color:#90caf9;text-align:left;white-space:nowrap">Mesafe</th>
            <th style="padding:8px 10px;color:#90caf9;text-align:left">Konum</th>
            <th style="padding:8px 10px;color:#90caf9;text-align:left;white-space:nowrap">T0+</th>
            <th style="padding:8px 10px;color:#90caf9;text-align:left">Tan&#305;kl&#305;k (orijinal)</th>
            <th style="padding:8px 10px;color:#90caf9;text-align:left">&#350;iddet</th>
          </tr>
        </thead>
        <tbody>
{rows}        </tbody>
      </table>
      </div>

      <div style="margin-top:14px;font-size:.8em;color:#5a7090;line-height:1.8">
        &#128204; En yak&#305;n: General Santos 46 km &#8212; <em>"Massive lots damage"</em> &nbsp;|&nbsp;
        &#128204; En uzak: Patong/Phuket (Tayland) 2&#8202;968 km &#8212; <em>"Light, perhaps below 4.0 scale"</em><br>
        EMSC = European&#8209;Mediterranean Seismological Centre &bull;
        <a href="{EMSC_URL}" target="_blank" rel="noopener" style="color:#7a9ab5;">
        Tam tan&#305;kl&#305;k listesi &#8594;</a>
      </div>
    </div>"""

NEW_APPX = (
    '\n  <div class="accordion" data-num="5." '
    'data-label="Appendix E &#8212; EMSC Saha Tank&#305;l&#305;klar&#305;">'
    '\n    &#128227; Appendix E &#8212; EMSC Vatanda&#351; Tank&#305;l&#305;klar&#305; (Felt Reports)'
    '\n  </div>'
    '\n  <div class="panel" id="panel-appE">\n    '
    + PANEL +
    '\n  </div>'
)

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)

d['APPENDIX_SECTIONS_HTML'] = d['APPENDIX_SECTIONS_HTML'] + NEW_APPX

with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print('JSON kaydedildi. Appendix E uzunlugu:', len(NEW_APPX))
