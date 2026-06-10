"""
build_shakemap_layer.py
USGS ShakeMap verilerinden Leaflet katmanı JS'i üretir ve
INPUT/Mindanao-2026.json içindeki AFTERSHOCK_MAP_JS'e ekler.

Veri kaynakları (USGS GeoJSON API üzerinden otomatik bulunur):
  - cont_mmi.json   : MMI izokonturları (alet bazlı yoğunluk)
  - cont_pga.json   : PGA izokonturları (%g, ivme)
  - rupture.json    : Fay kırığı geometrisi
  - stationlist.json: Sismik istasyon konumları

Neden bu veriler?
  MMI kontürü  → ShakeMap'in teorik/alet bazlı MMI izohipsleri;
                  DYFI vatandaş bildirimleriyle karşılaştırma imkânı.
  PGA kontürü  → Zemin ivmesi; yapı hasarı tahmininde kullanılır.
  Rupture      → Fay kırığının yüzey projeksiyonu; artçıların dağılım
                  yönünü açıklar.
  Stations     → Hangi sismometreler ölçtü; ShakeMap'in alet tabanını kanıtlar.
"""

import json, urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# ── USGS API: event metadata ve ShakeMap timestamp ─────────────────
def get_shakemap_urls(eventid):
    url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?eventid={eventid}&format=geojson'
    d   = json.loads(urllib.request.urlopen(
        urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=20
    ).read())
    shake = d['properties']['products'].get('shakemap', [{}])[0]
    base  = shake['contents'].get('download/cont_mmi.json', {}).get('url', '')
    # timestamp'i URL'den cikart
    ts_m  = re.search(r'/shakemap/\w+/\w+/(\d+)/download/', base)
    if not ts_m:
        raise RuntimeError('ShakeMap timestamp bulunamadi')
    ts    = ts_m.group(1)
    netid = d['properties']['net']
    base_url = f'https://earthquake.usgs.gov/product/shakemap/{eventid}/{netid}/{ts}/download/'
    return base_url, d['properties']

def fetch_json(url):
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=25
    ).read())

# ── MMI renk skalası (USGS standart) ──────────────────────────────
def mmi_color(v):
    if v >= 7.0: return '#ff0000'
    if v >= 6.0: return '#ff8c00'
    if v >= 5.5: return '#ffd600'
    if v >= 5.0: return '#aaff00'
    if v >= 4.5: return '#44cc44'
    if v >= 4.0: return '#00cccc'
    if v >= 3.5: return '#66bbff'
    return '#aaaaaa'

def mmi_label(v):
    labels = {3.5:'III Zayif',4.0:'IV Hafif',4.5:'IV-V',5.0:'V Orta',
              5.5:'V-VI',6.0:'VI Kuvvetli',6.5:'VI-VII',7.0:'VII Cok Kuvvetli'}
    return labels.get(v, f'MMI {v}')

def pga_color(v):
    if v >= 50:  return '#b30000'
    if v >= 20:  return '#ff0000'
    if v >= 10:  return '#ff6600'
    if v >= 5:   return '#ffaa00'
    if v >= 2:   return '#ffe000'
    if v >= 1:   return '#90ee90'
    return '#add8e6'

def pga_label(v):
    return f'PGA {v}%g'


def build_shakemap_js(eventid):
    print(f'ShakeMap yukleniyor: {eventid}')
    base_url, evprops = get_shakemap_urls(eventid)

    mmi_data = fetch_json(base_url + 'cont_mmi.json')
    pga_data = fetch_json(base_url + 'cont_pga.json')
    rup_data = fetch_json(base_url + 'rupture.json')
    sta_data = fetch_json(base_url + 'stationlist.json')

    print(f'  MMI kontur: {len(mmi_data["features"])} feature')
    print(f'  PGA kontur: {len(pga_data["features"])} feature')

    # ── MMI konturları: her feature MultiLineString veya LineString ──
    mmi_lines = []
    for feat in mmi_data['features']:
        v    = feat['properties']['value']
        col  = mmi_color(v)
        lbl  = mmi_label(v)
        geom = feat['geometry']
        gtype= geom['type']
        if gtype == 'MultiLineString':
            segs = geom['coordinates']
        elif gtype == 'LineString':
            segs = [geom['coordinates']]
        else:
            continue
        for seg in segs:
            pts = [[round(c[1],4), round(c[0],4)] for c in seg]
            mmi_lines.append({'v': v, 'col': col, 'lbl': lbl, 'pts': pts})

    # ── PGA konturları ────────────────────────────────────────────
    pga_lines = []
    for feat in pga_data['features']:
        v    = feat['properties']['value']
        col  = pga_color(v)
        lbl  = pga_label(v)
        geom = feat['geometry']
        gtype= geom['type']
        if gtype == 'MultiLineString':
            segs = geom['coordinates']
        elif gtype == 'LineString':
            segs = [geom['coordinates']]
        else:
            continue
        for seg in segs:
            pts = [[round(c[1],4), round(c[0],4)] for c in seg]
            pga_lines.append({'v': v, 'col': col, 'lbl': lbl, 'pts': pts})

    # ── Rupture ──────────────────────────────────────────────────
    rup_segs = []
    for feat in rup_data.get('features', []):
        geom = feat['geometry']
        if geom is None:
            continue
        gtype = geom['type']
        if gtype == 'MultiLineString':
            segs = geom['coordinates']
        elif gtype == 'LineString':
            segs = [geom['coordinates']]
        else:
            continue
        for seg in segs:
            pts = [[round(c[1],4), round(c[0],4)] for c in seg]
            rup_segs.append(pts)

    # ── Stations ─────────────────────────────────────────────────
    sta_pts = []
    for feat in sta_data.get('features', []):
        p    = feat['properties']
        geom = feat['geometry']
        if geom is None:
            continue
        lon, lat = geom['coordinates'][:2]
        sta_pts.append({
            'lat':  round(lat, 4),
            'lon':  round(lon, 4),
            'code': p.get('code', '?')[:20],
            'name': (p.get('name') or p.get('code','?'))[:35],
            'net':  p.get('network', '?'),
            'type': p.get('station_type', '?'),
            'mmi':  p.get('intensity'),
            'pga':  p.get('pga'),
            'dist': round(p.get('distance', 0), 1),
        })

    print(f'  Rupture segs: {len(rup_segs)}')
    print(f'  Stations: {len(sta_pts)}')

    mmi_js = json.dumps(mmi_lines)
    pga_js = json.dumps(pga_lines)
    rup_js = json.dumps(rup_segs)
    sta_js = json.dumps(sta_pts)

    JS = f"""
// ── ShakeMap Katmanlari (USGS {eventid}) ─────────────────────────
(function() {{
  var mapEl = document.getElementById('aftershock-map');
  if (!mapEl || !window._asMap) {{
    // Harita henuz hazir degil — bekle
    var _t = setInterval(function() {{
      if (window._asMap) {{ clearInterval(_t); _initShake(); }}
    }}, 300);
  }} else {{ _initShake(); }}

  function _initShake() {{
    var map = window._asMap;
    var mmiData = {mmi_js};
    var pgaData = {pga_js};
    var rupData = {rup_js};
    var staData = {sta_js};

    // MMI kontur katmani
    var mmiLayer = L.layerGroup();
    mmiData.forEach(function(l) {{
      L.polyline(l.pts, {{color:l.col, weight:2, opacity:0.85}})
       .bindTooltip('ShakeMap ' + l.lbl, {{sticky:true}})
       .addTo(mmiLayer);
    }});

    // PGA kontur katmani
    var pgaLayer = L.layerGroup();
    pgaData.forEach(function(l) {{
      L.polyline(l.pts, {{color:l.col, weight:1.5, opacity:0.8, dashArray:'6 3'}})
       .bindTooltip(l.lbl, {{sticky:true}})
       .addTo(pgaLayer);
    }});

    // Fay kirigi
    var rupLayer = L.layerGroup();
    if (rupData.length > 0) {{
      rupData.forEach(function(seg) {{
        L.polyline(seg, {{color:'#ff44ff', weight:3.5, opacity:0.9}})
         .bindTooltip('Fay Kirigi (ShakeMap)', {{sticky:true}})
         .addTo(rupLayer);
      }});
      rupLayer.addTo(map);  // Kirigi her zaman goster
    }}

    // Sismik istasyonlar
    var staLayer = L.layerGroup();
    staData.forEach(function(s) {{
      var col = s.type==='macroseismic' ? '#ffd600' : '#44ffaa';
      var ic  = L.divIcon({{
        html: '<div style="width:10px;height:10px;border-radius:50%;background:' + col +
              ';border:2px solid #fff;box-shadow:0 0 4px rgba(0,0,0,.5)"></div>',
        className:'', iconSize:[10,10], iconAnchor:[5,5]
      }});
      L.marker([s.lat, s.lon], {{icon:ic}})
       .bindPopup('<b>' + s.code + '</b><br>' + s.name +
                  '<br>Tip: ' + s.type + ' | Net: ' + s.net +
                  '<br>MMI: ' + (s.mmi||'?') + ' | PGA: ' + (s.pga||'?') + ' %g' +
                  '<br>Mesafe: ' + s.dist + ' km')
       .addTo(staLayer);
    }});

    // Toggle butonlari
    var wrap = document.getElementById('aftershock-map-wrap');
    if (!wrap) return;

    var btnMMI = _mkBtn('MMI', '#66bbff', 'ShakeMap MMI izokonturlari (alet bazli)');
    var btnPGA = _mkBtn('PGA', '#90ee90', 'PGA ivme izokonturlari');
    var btnSTA = _mkBtn('STA', '#44ffaa', 'Sismik istasyonlar');
    btnMMI.style.right = '98px';
    btnPGA.style.right = '142px';
    btnSTA.style.right = '186px';

    var layerMap = {{MMI:[mmiLayer,btnMMI], PGA:[pgaLayer,btnPGA], STA:[staLayer,btnSTA]}};
    Object.keys(layerMap).forEach(function(k) {{
      var lay=layerMap[k][0], btn=layerMap[k][1], on=false;
      btn.onclick = function() {{
        on = !on;
        if (on) {{ lay.addTo(map); btn.style.background='rgba(255,255,255,.2)'; btn.style.fontWeight='700'; }}
        else    {{ map.removeLayer(lay); btn.style.background='rgba(10,14,21,0.85)'; btn.style.fontWeight='normal'; }}
      }};
      wrap.appendChild(btn);
    }});

    // MMI lejant (her zaman goster)
    var mmiLg = L.control({{position:'topright'}});
    mmiLg.onAdd = function() {{
      var d = L.DomUtil.create('div','');
      d.style.cssText = 'background:rgba(10,14,21,0.88);color:#e8f0f5;padding:7px 10px;'
        + 'border-radius:8px;font-size:10px;line-height:1.8;border:1px solid rgba(255,255,255,.1);margin-top:60px;';
      d.innerHTML = '<b style="color:#66bbff">ShakeMap MMI</b> <span style="color:#7a9ab5;font-size:.85em">(alet)</span><br>'
        + '<span style="color:#ff0000">&#9135;</span> VII Cok Kuvvetli<br>'
        + '<span style="color:#ff8c00">&#9135;</span> VI Kuvvetli<br>'
        + '<span style="color:#ffd600">&#9135;</span> V-VI<br>'
        + '<span style="color:#aaff00">&#9135;</span> V Orta<br>'
        + '<span style="color:#44cc44">&#9135;</span> IV Hafif<br>'
        + '<span style="color:#00cccc">&#9135;</span> III-IV<br>'
        + '<span style="color:#66bbff">&#9135;</span> III Zayif<br>'
        + '<span style="color:#ff44ff">&#9135;&#9135;</span> Fay Kirigi<br>'
        + '<span style="color:#44ffaa">&#9679;</span> Sismometre &nbsp;'
        + '<span style="color:#ffd600">&#9679;</span> DYFI';
      return d;
    }};
    mmiLg.addTo(map);
  }}

  function _mkBtn(label, color, title) {{
    var b = document.createElement('button');
    b.innerHTML = label; b.title = title;
    b.style.cssText = 'position:absolute;top:10px;z-index:1000;'
      + 'background:rgba(10,14,21,0.85);color:' + color + ';'
      + 'border:1px solid ' + color + '66;'
      + 'border-radius:6px;padding:4px 7px;font-size:11px;cursor:pointer;';
    return b;
  }}
}})();
"""
    return JS


if __name__ == '__main__':
    EVENT_ID = sys.argv[1] if len(sys.argv) > 1 else 'us7000lff4'

    shake_js = build_shakemap_js(EVENT_ID)

    # parse_aftershocks snippet'ine ekle
    with open('OUTPUT/aftershock_map_snippet.html', encoding='utf-8') as f:
        snippet = f.read()

    MARKER = '// ── ShakeMap Katmanlari'
    if MARKER in snippet:
        # Eski ShakeMap JS'i cikar
        old_start = snippet.find(MARKER)
        old_end   = snippet.find('\n}})();\n', old_start) + len('\n}})();\n')
        snippet   = snippet[:old_start] + snippet[old_end:]

    # </script> oncesine ekle
    snippet = snippet.replace('</script>', shake_js + '\n</script>', 1)

    with open('OUTPUT/aftershock_map_snippet.html', 'w', encoding='utf-8') as f:
        f.write(snippet)
    print(f'Snippet guncellendi, ShakeMap JS: {len(shake_js)} karakter')

    # JSON guncelle
    import os
    script_start = snippet.find('<script>\n')
    script_end   = snippet.rfind('</script>')
    script_body  = snippet[script_start + len('<script>\n'):script_end].strip()
    idx = script_body.find('// ── Sismik')
    map_js   = script_body[:idx].strip()
    omori_js = script_body[idx:].strip()

    with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
        d = json.load(f)
    d['AFTERSHOCK_MAP_JS'] = map_js
    d['OMORI_CHART_JS']    = omori_js
    with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    # Post guncelle
    with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', encoding='utf-8') as f:
        post = f.read()
    s = post.find('<!-- ── AFTERSHOCK MAP + OMORI')
    e = post.find('<!-- CTA -->')
    post = post[:s] + snippet + '\n\n' + post[e:]
    with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', 'w', encoding='utf-8') as f:
        f.write(post)

    print('JSON ve Post guncellendi.')
