"""
aftershock_update.py — Mindanao 2026 Mw 7.8 Artçı Güncelleme Aracı
====================================================================

Kullanim:
  python aftershock_update.py aftershock-update   → EMSC'den veri cek, JSON guncelle, HTML uret
  python aftershock_update.py page-update         → JSON'dan HTML uret (Blogger PAGE)
  python aftershock_update.py post-update         → Snippet'ten POST guncelle
  python aftershock_update.py status              → Kac artci var, son cekme zamanı

Calisma mantigi:
  1. EMSC FDSN API → INPUT/aftershocks_raw.txt
     (Mevcut satırlarla karşılaştırır, sadece yenileri ekler)
  2. parse_aftershocks.py → OUTPUT/aftershock_map_snippet.html guncellenir
  3. JSON (INPUT/Mindanao-2026.json) icinde AFTERSHOCK_MAP_JS + OMORI_CHART_JS degistirilir
  4. generate.py → OUTPUT/SEISMO/SeismoReport-2026-Mindanao-Mw78.html uretilir
"""

import os, sys, json, re, subprocess, urllib.request
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

# ── Konfigürasyon ─────────────────────────────────────────────────
CFG = {
    'raw'      : 'events/Mindanao-2026/aftershocks_raw.txt',
    'json'     : 'events/Mindanao-2026/Mindanao-2026.json',
    'snippet'  : 'OUTPUT/aftershock_map_snippet.html',
    'page_html': 'OUTPUT/SEISMO/SeismoReport-2026-Mindanao-Mw78.html',
    'post_html': 'OUTPUT/POSTS/Mindanao-Mw78-Post.html',
    # Ana deprem: 2026-06-07T01:44:55 UTC
    'start'    : '2026-06-07T01:44:00',
    'lat'      : 5.6829,
    'lon'      : 125.0582,
    'radius'   : 3.5,   # derece (±)
    'minmag'   : 3.0,
    'limit'    : 1000,
    'emsc_url' : 'https://www.seismicportal.eu/fdsnws/event/1/query',
}

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[{ts}] {msg}')

# ── EMSC FDSN: yeni artci verisi cek ──────────────────────────────
def fetch_emsc():
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    params = (
        f"?starttime={CFG['start']}"
        f"&endtime={now_utc}"
        f"&minlat={CFG['lat']-CFG['radius']:.4f}"
        f"&maxlat={CFG['lat']+CFG['radius']:.4f}"
        f"&minlon={CFG['lon']-CFG['radius']:.4f}"
        f"&maxlon={CFG['lon']+CFG['radius']:.4f}"
        f"&minmagnitude={CFG['minmag']}"
        f"&format=text&limit={CFG['limit']}&orderby=time-asc"
    )
    url = CFG['emsc_url'] + params
    log(f'EMSC sorgusu: {url[:80]}...')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
    lines = [l for l in resp.splitlines() if l.strip() and '|' in l and not l.startswith('#')]
    log(f'EMSC: {len(lines)} satir alindi')
    return lines

# ── Mevcut raw ile birlestir (deduplikasyon) ──────────────────────
def merge_raw(new_lines):
    existing = []
    if os.path.exists(CFG['raw']):
        with open(CFG['raw'], encoding='utf-8') as f:
            existing = [l.rstrip('\n') for l in f if l.strip() and '|' in l]

    existing_ids = set()
    for l in existing:
        parts = l.split('|')
        if parts:
            existing_ids.add(parts[0].strip())

    added = 0
    for l in new_lines:
        parts = l.split('|')
        if parts and parts[0].strip() not in existing_ids:
            existing.append(l.strip())
            existing_ids.add(parts[0].strip())
            added += 1

    # Zamana gore sirala (kolon 1 = time)
    def sort_key(line):
        p = line.split('|')
        return p[1].strip() if len(p) > 1 else ''
    existing.sort(key=sort_key)

    with open(CFG['raw'], 'w', encoding='utf-8') as f:
        f.write('\n'.join(existing) + '\n')

    log(f'Ham veri: {len(existing)} toplam, {added} yeni eklendi → {CFG["raw"]}')
    return added, len(existing)

# ── parse_aftershocks.py calistir ────────────────────────────────
def run_parse():
    log('parse_aftershocks.py calistiriliyor...')
    result = subprocess.run(
        ['python', 'scripts/parse_aftershocks.py', CFG['raw']],
        capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode != 0:
        log(f'HATA: {result.stderr[:400]}')
        return False
    # Ozet satırlari goster
    for line in result.stdout.splitlines():
        if any(k in line for k in ['Ana deprem', 'Artci', 'Omori', 'K =', 'p =', 'R²', 'DYFI', 'ShakeMap', 'Snippet']):
            log(f'  {line.strip()}')
    return True

# ── JSON icindeki MAP_JS ve OMORI_JS guncelle ─────────────────────
def update_json_from_snippet():
    if not os.path.exists(CFG['snippet']):
        log(f'HATA: snippet bulunamadi: {CFG["snippet"]}')
        return False

    with open(CFG['snippet'], encoding='utf-8') as f:
        snippet = f.read()

    # <script> blogunu cikar
    s = snippet.find('<script>\n')
    e = snippet.rfind('</script>')
    if s == -1 or e == -1:
        log('HATA: script blogu snippet icinde bulunamadi')
        return False
    script_body = snippet[s + len('<script>\n'):e].strip()

    # MAP_JS ve OMORI_JS'i ayir
    # MAP_JS: baslangicindan '// -- Sismik' e kadar
    split_markers = [
        '// ── Sismik İstatistik',
        '// -- Sismik',
        '(function() {\n  var canvasOmori',
    ]
    split_idx = -1
    for m in split_markers:
        idx = script_body.find(m)
        if idx != -1:
            split_idx = idx
            break

    if split_idx == -1:
        log('HATA: OMORI_CHART_JS ayrac bulunamadi')
        return False

    map_js   = script_body[:split_idx].strip()
    omori_js = script_body[split_idx:].strip()

    with open(CFG['json'], encoding='utf-8') as f:
        d = json.load(f)

    d['AFTERSHOCK_MAP_JS'] = map_js
    d['OMORI_CHART_JS']    = omori_js

    with open(CFG['json'], 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    log(f'JSON guncellendi: MAP_JS={len(map_js)} chr, OMORI_JS={len(omori_js)} chr')
    return True

# ── REVIEW_SECTION_HTML içindeki parametreleri guncelle ───────────
def update_params_in_review():
    with open(CFG['json'], encoding='utf-8') as f:
        d = json.load(f)

    p   = d.get('PARAM_P')
    b   = d.get('PARAM_B')
    K   = d.get('PARAM_K')
    c   = d.get('PARAM_C')
    mc  = d.get('PARAM_MC', '3.5')
    n   = d.get('PARAM_N_TOTAL')
    n5  = d.get('PARAM_N_M5')
    n6  = d.get('PARAM_N_M6')
    ftls = d.get('PARAM_FTLS', 'KIRMIZI')
    upd  = d.get('PARAM_UPDATED', '')

    if not all([p, b, K, n]):
        log('UYARI: PARAM_* alanlari eksik, REVIEW guncellenmedi')
        return False

    html = d.get('REVIEW_SECTION_HTML', '')
    original_len = len(html)

    # p değeri — "p = 0.xxx" veya "p=0.xxx"
    html = re.sub(r'\bp\s*=\s*0\.\d{3,4}\b', f'p = {p}', html)
    # b değeri — tam aralık (b₁ b₂ dokunma)
    html = re.sub(r'(?<![₁₂_\d])b\s*=\s*0\.\d{3,4}(?![₁₂_\d])', f'b={b}', html)
    # K değeri
    html = re.sub(r'\bK\s*=\s*\d{1,3}\.\d{1,4}\b', f'K = {K}', html)
    # Artçı sayısı — "NNN artçı" veya "N=NNN artçı" veya "N = NNN)"
    html = re.sub(r'\b(\d{3,4})\s*artç[ıi]', lambda m: f'{n} artçı', html)
    html = re.sub(r'N\s*=\s*\d{3,4}\b', f'N={n}', html)
    # FTLS durumu metni
    html = re.sub(r'FTLS\s+(KIRMIZI|SARI|YEŞİL)', f'FTLS {ftls}', html)
    # Güncelleme tarihi — "Son güncelleme:" satırı
    html = re.sub(
        r'Son güncelleme:[^<\n]*',
        f'Son güncelleme: {upd}',
        html
    )

    d['REVIEW_SECTION_HTML'] = html
    with open(CFG['json'], 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    log(f'REVIEW parametreleri guncellendi: p={p} b={b} K={K} N={n} FTLS={ftls}')
    return True

# ── GitHub'a push ─────────────────────────────────────────────────
# msg_prefix: 'data' (otomatik artci), 'sablon' (manuel sablon), vs.
def _push_to_github(new_count=0, msg_prefix='data', custom_msg=None):
    import subprocess as _sp
    try:
        # Tüm takip edilen (tracked) değişiklikleri stage et — şablonlar dahil
        _sp.run(['git', 'add', '-u'], check=True, capture_output=True)
        if custom_msg:
            msg = custom_msg
        elif msg_prefix == 'data':
            msg = (f'data: Mindanao artci guncelleme +{new_count} olay '
                   f'({datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")})')
        else:
            msg = (f'{msg_prefix}: sablon/JSON guncelleme '
                   f'({datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")})')

        result = _sp.run(['git', 'commit', '-m', msg],
                         capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            push = _sp.run(['git', 'push', 'origin', 'main'],
                           capture_output=True, text=True, encoding='utf-8')
            if push.returncode == 0:
                log(f'GitHub push basarili: {msg}')
            else:
                log(f'GitHub push HATASI: {push.stderr[:200]}')
        else:
            # returncode=1 + "nothing to commit" → normal durum
            if 'nothing to commit' in result.stdout + result.stderr:
                log('Git: degisiklik yok, push atlandı')
            else:
                log(f'Git commit HATA: {result.stderr[:200]}')
    except Exception as ex:
        log(f'Git islem hatasi: {ex}')

# ── generate.py calistir → PAGE HTML ─────────────────────────────
def run_generate():
    log('generate.py calistiriliyor...')
    result = subprocess.run(
        ['python', 'generate.py', CFG['json']],
        capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode != 0:
        log(f'HATA: {result.stderr[:400]}')
        return False
    log(result.stdout.strip())
    return True

# ── Post HTML guncelle (snippet enjekte) ─────────────────────────
def update_post():
    if not os.path.exists(CFG['snippet']):
        log(f'HATA: snippet yok: {CFG["snippet"]}')
        return False
    if not os.path.exists(CFG['post_html']):
        log(f'HATA: post yok: {CFG["post_html"]}')
        return False

    with open(CFG['snippet'], encoding='utf-8') as f:
        snippet = f.read()
    with open(CFG['post_html'], encoding='utf-8') as f:
        post = f.read()

    # Harita wrap baslangici
    s_wrap = post.find('<div id="aftershock-map-wrap"')
    if s_wrap == -1:
        log('HATA: aftershock-map-wrap post icinde bulunamadi')
        return False

    # CTA yorumu veya script bitisi
    cta_idx = post.find('<!-- CTA -->')
    if cta_idx == -1:
        # fallback: script bitis
        cta_idx = post.find('</script>', post.find('// ── Sismik')) + len('</script>')

    # Haritanin basindan CTA'ya kadar olan eski blogu yeni snippet ile degistir
    # Haritanin oncesindeki div-wrap baslangic satrini koru
    # Harita wrapi iceren en basi bul (tam enclosing div)
    outer_div = post.rfind('<div', 0, s_wrap)
    # Eger dogrudan wrap ise, ya da parent div ise — guvenlice sadece wrap'tan kes
    post = post[:s_wrap] + snippet + '\n\n' + post[cta_idx:]

    with open(CFG['post_html'], 'w', encoding='utf-8') as f:
        f.write(post)

    log(f'Post guncellendi → {CFG["post_html"]} ({round(len(post)/1024)} KB)')
    return True

# ── status ────────────────────────────────────────────────────────
def show_status():
    if not os.path.exists(CFG['raw']):
        log('Ham veri yok: ' + CFG['raw'])
        return
    with open(CFG['raw'], encoding='utf-8') as f:
        lines = [l for l in f if l.strip() and '|' in l]
    # En buyuk ve en yeni artci
    events = []
    for l in lines:
        p = l.split('|')
        if len(p) > 10:
            try:
                events.append({'time': p[1].strip(), 'mag': float(p[10].strip()), 'region': p[12].strip()[:40] if len(p)>12 else ''})
            except ValueError:
                pass
    if not events:
        log('Veri yok'); return
    events.sort(key=lambda x: x['time'])
    biggest = max(events, key=lambda x: x['mag'])
    log(f'Toplam: {len(events)} artci')
    log(f'Ilk   : {events[0]["time"]} M{events[0]["mag"]}')
    log(f'Son   : {events[-1]["time"]} M{events[-1]["mag"]}')
    log(f'En buyuk: M{biggest["mag"]} @ {biggest["time"]} — {biggest["region"]}')
    # M5+ sayisi
    m5 = sum(1 for e in events if e['mag'] >= 5.0)
    m6 = sum(1 for e in events if e['mag'] >= 6.0)
    log(f'M5+: {m5}  M6+: {m6}')

    # HTML guncelleme zamani
    if os.path.exists(CFG['page_html']):
        mtime = os.path.getmtime(CFG['page_html'])
        ts = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        log(f'Son HTML guncellemesi: {ts}')

# ── Ana akis ─────────────────────────────────────────────────────
def cmd_aftershock_update():
    log('=== aftershock-update basladi ===')
    try:
        new_lines = fetch_emsc()
    except Exception as ex:
        log(f'EMSC baglanamadi: {ex}')
        log('Cevrimdisi mod: mevcut ham veri kullaniliyor')
        new_lines = []

    added, total = merge_raw(new_lines)

    if added == 0 and total > 0:
        log('Yeni artci yok — son guncelleme gecerli, yeniden isleniyor...')

    ok = run_parse()
    if not ok:
        log('parse_aftershocks.py basarisiz'); return

    ok = update_json_from_snippet()
    if not ok:
        log('JSON guncellemesi basarisiz'); return

    ok = update_params_in_review()
    if not ok:
        log('UYARI: REVIEW parametreleri guncellenemedi (devam ediliyor)')

    ok = run_generate()
    if ok:
        _push_to_github(added)
        log(f'=== Tamamlandi. Yeni: {added}, Toplam: {total} artci ===')
    else:
        log('generate.py basarisiz')

def cmd_page_update():
    log('=== page-update basladi ===')
    ok = run_generate()
    if ok:
        log(f'PAGE hazir → {CFG["page_html"]}')
        log('Blogger\'a yapistirmak icin dosyayi HTML modunda acin.')

def cmd_post_update():
    log('=== post-update basladi ===')
    if not os.path.exists(CFG['snippet']):
        log('Snippet yok, once aftershock-update calistirin.')
        return
    ok = update_post()
    if ok:
        log(f'POST hazir → {CFG["post_html"]}')

def cmd_push():
    """Tüm yerel degisiklikleri (sablon, JSON, HTML) GitHub'a push et."""
    log('=== github-push basladi ===')
    # Önce generate et (en guncel HTML uret)
    run_generate()
    _push_to_github(msg_prefix='sablon')
    log('=== push tamamlandi ===')

# ── CLI ──────────────────────────────────────────────────────────
COMMANDS = {
    'aftershock-update': cmd_aftershock_update,
    'page-update'      : cmd_page_update,
    'post-update'      : cmd_post_update,
    'push'             : cmd_push,
    'status'           : show_status,
}

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd in COMMANDS:
        COMMANDS[cmd]()
    else:
        print(__doc__)
        print('Gecerli komutlar:', ', '.join(COMMANDS.keys()))
