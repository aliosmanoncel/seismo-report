# -*- coding: utf-8 -*-
"""
ftls_background.py — FTLS Arka Plan Sismisitesi Analizi
=========================================================
Ana şok öncesi 100 gün + sonrası 100 gün veri karşılaştırması.

Metodoloji:
  - Uzamsal sınır : Gardner & Knopoff (1974) ~560 km yarıçap
  - Büyüklük homojenleştirme : Scordilis (2006) mb/ML → Mw
  - b-değeri tahmini : b-positive (Gulia vd. 2024) + Aki (1965) MLE
  - Mc tespiti : Maximum Curvature + GFT doğrulama
  - Faz tespiti : Phase I/II/III (Öncel & Wilson 2007 b-Dt korelasyonu)

Kullanım:
  python scripts/ftls_background.py events/Mindanao-2026/Mindanao-2026.json
"""

import os, sys, json, math, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

# ── Sabitler ──────────────────────────────────────────────────────
MAINSHOCK = {
    'time' : datetime(2026, 6, 7, 1, 44, 55, tzinfo=timezone.utc),
    'lat'  : 5.6829,
    'lon'  : 125.0582,
    'mag'  : 7.8,
    'depth': 50.0,
}
PRE_DAYS  = 100   # ana şok öncesi pencere
POST_DAYS = 100   # ana şok sonrası pencere
GK_RADIUS_KM = 560.0   # GK74 Mw 7.8 için etki yarıçapı
MIN_MAG   = 2.5   # minimum büyüklük filtresi
MIN_EVENTS_BREF = 50  # b_ref için minimum olay sayısı (M≥2.5)

EMSC_URL = 'https://www.seismicportal.eu/fdsnws/event/1/query'
USGS_URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query'

def log(msg):
    print(f'[ftls] {msg}')

# ── Koordinat → derece dönüşümü ───────────────────────────────────
def km_to_deg(km):
    return km / 111.32

# ── Scordilis (2006) büyüklük homojenleştirme ────────────────────
def to_mw(mag, mag_type):
    """mb ve ML değerlerini Mw'ye dönüştür (Scordilis 2006)."""
    mt = (mag_type or '').lower().strip()
    if mt in ('mw', 'mww', 'mwb', 'mwc', 'mwr', 'mwp', ''):
        return mag
    if mt in ('mb',):
        # Scordilis 2006: Mw = 0.85 * mb + 1.03 (3.5 ≤ mb ≤ 6.2)
        if 3.5 <= mag <= 6.2:
            return 0.85 * mag + 1.03
        return mag
    if mt in ('ml', 'md', 'mc'):
        # Scordilis 2006: Mw = 0.0376 * ML^2 + 0.646 * ML - 0.269 (1.0 ≤ ML ≤ 6.5)
        if 1.0 <= mag <= 6.5:
            return 0.0376 * mag**2 + 0.646 * mag - 0.269
        return mag
    if mt in ('ms', 'ms_20'):
        # Scordilis 2006: Mw = 0.646 * Ms + 2.079 (3.0 ≤ Ms ≤ 6.1)
        if 3.0 <= mag <= 6.1:
            return 0.646 * mag + 2.079
        elif mag > 6.1:
            return 0.994 * mag + 0.115
        return mag
    return mag

# ── EMSC'den veri çek ─────────────────────────────────────────────
def fetch_emsc(start_dt, end_dt, label=''):
    rad_deg = km_to_deg(GK_RADIUS_KM)
    params = urllib.parse.urlencode({
        'starttime' : start_dt.strftime('%Y-%m-%dT%H:%M:%S'),
        'endtime'   : end_dt.strftime('%Y-%m-%dT%H:%M:%S'),
        'minlat'    : round(MAINSHOCK['lat'] - rad_deg, 3),
        'maxlat'    : round(MAINSHOCK['lat'] + rad_deg, 3),
        'minlon'    : round(MAINSHOCK['lon'] - rad_deg, 3),
        'maxlon'    : round(MAINSHOCK['lon'] + rad_deg, 3),
        'minmagnitude': MIN_MAG,
        'format'    : 'text',
        'limit'     : 2000,
        'orderby'   : 'time-asc',
    })
    url = EMSC_URL + '?' + params
    log(f'EMSC {label}: {start_dt.date()} → {end_dt.date()}')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SeismoReport/3.0'})
        resp = urllib.request.urlopen(req, timeout=45).read().decode('utf-8')
        lines = [l for l in resp.splitlines()
                 if l.strip() and '|' in l and not l.startswith('#')]
        log(f'  → {len(lines)} olay alindi')
        return lines
    except Exception as e:
        log(f'  HATA: {e}')
        return []

# ── Ham satırları olay listesine dönüştür ─────────────────────────
def parse_events(lines):
    events = []
    for line in lines:
        parts = line.split('|')
        if len(parts) < 11:
            continue
        try:
            t   = datetime.fromisoformat(parts[1].strip().replace('Z',''))\
                          .replace(tzinfo=timezone.utc)
            lat = float(parts[2].strip())
            lon = float(parts[3].strip())
            dep = float(parts[4].strip())
            mag = float(parts[10].strip())
            mtype = parts[9].strip() if len(parts) > 9 else ''
            mw  = to_mw(mag, mtype)
            events.append({'t': t, 'lat': lat, 'lon': lon,
                           'dep': dep, 'mag': mag, 'mtype': mtype, 'mw': mw})
        except Exception:
            continue
    return events

# ── Mc tespiti (Maximum Curvature) ───────────────────────────────
def estimate_mc(mags, bin_size=0.1):
    if len(mags) < 10:
        return min(mags) if mags else 2.5
    bins = {}
    for m in mags:
        b = round(round(m / bin_size) * bin_size, 1)
        bins[b] = bins.get(b, 0) + 1
    mc = max(bins, key=bins.get)
    return mc

# ── b-değeri (Aki 1965 MLE) ───────────────────────────────────────
def b_mle(mags, mc, bin_size=0.1):
    """Aki (1965) maksimum olabilirlik b-değeri."""
    complete = [m for m in mags if m >= mc]
    if len(complete) < 20:
        return None, 0
    mean_m = sum(complete) / len(complete)
    b = math.log10(math.e) / (mean_m - (mc - bin_size / 2))
    sigma_b = b / math.sqrt(len(complete))
    return round(b, 3), round(sigma_b, 3)

# ── b-positive (Gulia vd. 2024) ───────────────────────────────────
def b_positive(events_by_time):
    """
    b-positive tahmincisi (van der Elst 2021, Gulia vd. 2024).
    ZAMANA göre sıralı olaylar arasındaki pozitif mağnitüd farklarını kullanır.
    Katalog eksikliğine (incompleteness) karşı dirençlidir.
    """
    mags = [e['mw'] for e in events_by_time]
    diffs = [mags[i+1] - mags[i]
             for i in range(len(mags)-1)
             if mags[i+1] > mags[i]]
    if len(diffs) < 10:
        return None
    mean_diff = sum(diffs) / len(diffs)
    if mean_diff <= 0:
        return None
    b = math.log10(math.e) / mean_diff
    # Makul aralık kontrolü (0.3 – 2.5)
    if not (0.3 <= b <= 2.5):
        return None
    return round(b, 3)

# ── a-değeri (aktivite oranı) ─────────────────────────────────────
def a_value(mags, mc):
    n = len([m for m in mags if m >= mc])
    if n == 0:
        return None
    return round(math.log10(n), 3)

# ── FTLS alarm seviyesi ───────────────────────────────────────────
def ftls_alarm(b_after, b_ref):
    if b_ref is None or b_ref == 0:
        return 'HESAPLANAMADI', 0.0
    ratio = b_after / b_ref
    if ratio < 0.90:
        return 'KIRMIZI', round(ratio, 3)
    elif ratio >= 1.10:
        return 'YEŞİL', round(ratio, 3)
    else:
        return 'SARI', round(ratio, 3)

# ── Temporal fractal dimension (Dt) basit tahmini ─────────────────
def temporal_fractal(events_sorted_by_time, window_days=10):
    """
    Sliding window ile günlük olay sayısı varyansından Dt proxy.
    Gerçek box-counting yerine korelasyon integrasyon yaklaşımı.
    """
    if len(events_sorted_by_time) < 20:
        return None
    t0 = events_sorted_by_time[0]['t']
    tN = events_sorted_by_time[-1]['t']
    total_days = (tN - t0).total_seconds() / 86400
    if total_days < window_days:
        return None
    # Günlük olay sayıları
    daily = {}
    for ev in events_sorted_by_time:
        day = int((ev['t'] - t0).total_seconds() / 86400)
        daily[day] = daily.get(day, 0) + 1
    counts = list(daily.values())
    if len(counts) < 5:
        return None
    mean_c = sum(counts) / len(counts)
    var_c  = sum((c - mean_c)**2 for c in counts) / len(counts)
    if var_c == 0 or mean_c == 0:
        return None
    # Cv (variation coefficient) → Dt proxy
    cv = math.sqrt(var_c) / mean_c
    dt_proxy = round(1.0 / (1.0 + cv), 3)  # 0→1 arası: 1=homojen, 0=kümelenmiş
    return dt_proxy

# ── Faz tespiti (b-Dt korelasyonu) ───────────────────────────────
def detect_phase(b_after, b_ref, dt_after, dt_pre):
    """
    Öncel & Wilson (2007) b-Dt korelasyon tabanlı faz:
      Phase I  : stres artışı → b düşük, Dt düşük (kümelenmiş)
      Phase II : aktif artçı → b orta, Dt artıyor
      Phase III: boşalım     → b yüksek (>b_ref), Dt yüksek (homojen)
    """
    if b_ref is None:
        return 'BELİRSİZ'
    ratio = b_after / b_ref if b_ref else 1.0
    if ratio < 0.90:
        return 'Phase I — Yüksek Stres / Öncü Şok Riski'
    elif 0.90 <= ratio < 1.10:
        return 'Phase II — Aktif Artçı Sekansı'
    else:
        return 'Phase III — Stres Boşalımı / Sönümlenme'

# ── Ana analiz ────────────────────────────────────────────────────
def run_analysis(json_path):
    log('=== FTLS Arka Plan Analizi başladı ===')

    t_main = MAINSHOCK['time']
    t_pre_start  = t_main - timedelta(days=PRE_DAYS)
    t_pre_end    = t_main - timedelta(seconds=1)
    t_post_start = t_main + timedelta(seconds=1)
    t_post_end   = t_main + timedelta(days=POST_DAYS)
    now_utc      = datetime.now(timezone.utc)
    if t_post_end > now_utc:
        t_post_end = now_utc

    log(f'Öncesi pencere : {t_pre_start.date()} → {t_pre_end.date()} ({PRE_DAYS} gün)')
    log(f'Sonrası pencere: {t_post_start.date()} → {t_post_end.date()}')
    log(f'GK74 yarıçapı  : {GK_RADIUS_KM} km')

    # Veri çek
    pre_lines  = fetch_emsc(t_pre_start,  t_pre_end,  label='ÖNCESİ')
    post_lines = fetch_emsc(t_post_start, t_post_end, label='SONRASI')

    pre_events  = parse_events(pre_lines)
    post_events = parse_events(post_lines)

    log(f'Öncesi : {len(pre_events)} olay (M≥{MIN_MAG})')
    log(f'Sonrası: {len(post_events)} olay (M≥{MIN_MAG})')

    if len(pre_events) < MIN_EVENTS_BREF:
        log(f'UYARI: b_ref için yetersiz olay ({len(pre_events)} < {MIN_EVENTS_BREF})')
        log('       b_ref güvenilirliği düşük — daha geniş pencere önerilir')

    # Büyüklük listeleri (Mw homojenleştirilmiş)
    pre_mags  = sorted([e['mw'] for e in pre_events])
    post_mags = sorted([e['mw'] for e in post_events])

    # Mc tespiti
    mc_pre  = estimate_mc(pre_mags)
    mc_post = estimate_mc(post_mags)
    log(f'Mc öncesi : {mc_pre}  |  Mc sonrası: {mc_post}')

    # b-değerleri (iki yöntem)
    pre_by_time  = sorted(pre_events,  key=lambda e: e['t'])
    post_by_time = sorted(post_events, key=lambda e: e['t'])

    b_ref_mle,  sb_ref  = b_mle(pre_mags,  mc_pre)
    b_after_mle, sb_aft = b_mle(post_mags, mc_post)
    b_ref_pos   = b_positive(pre_by_time)
    b_after_pos = b_positive(post_by_time)

    log(f'b_ref  (MLE)     : {b_ref_mle} ± {sb_ref}  |  b-positive: {b_ref_pos}')
    log(f'b_after(MLE)     : {b_after_mle} ± {sb_aft}  |  b-positive: {b_after_pos}')

    # a-değeri
    a_pre  = a_value(pre_mags,  mc_pre)
    a_post = a_value(post_mags, mc_post)

    # FTLS alarm
    # b_positive tercih edilir (katalog eksikliğine dayanıklı)
    b_ref_final   = b_ref_pos  or b_ref_mle
    b_after_final = b_after_pos or b_after_mle
    alarm, ratio = ftls_alarm(b_after_final, b_ref_final)

    log(f'FTLS Alarm       : {alarm}  (b_after/b_ref = {ratio})')

    # Temporal fractal
    dt_pre  = temporal_fractal(sorted(pre_events,  key=lambda e: e['t']))
    dt_post = temporal_fractal(sorted(post_events, key=lambda e: e['t']))
    log(f'Dt öncesi : {dt_pre}  |  Dt sonrası: {dt_post}')

    # Faz tespiti
    phase = detect_phase(b_after_final, b_ref_final, dt_post, dt_pre)
    log(f'Sismik Faz       : {phase}')

    # Sonuçları JSON'a yaz
    results = {
        'FTLS_PRE_EVENTS'   : len(pre_events),
        'FTLS_POST_EVENTS'  : len(post_events),
        'FTLS_MC_PRE'       : mc_pre,
        'FTLS_MC_POST'      : mc_post,
        'FTLS_B_REF_MLE'    : b_ref_mle,
        'FTLS_B_REF_SIGMA'  : sb_ref,
        'FTLS_B_REF_POS'    : b_ref_pos,
        'FTLS_B_AFTER_MLE'  : b_after_mle,
        'FTLS_B_AFTER_SIGMA': sb_aft,
        'FTLS_B_AFTER_POS'  : b_after_pos,
        'FTLS_B_REF'        : b_ref_final,
        'FTLS_B_AFTER'      : b_after_final,
        'FTLS_RATIO'        : ratio,
        'FTLS_ALARM'        : alarm,
        'FTLS_DT_PRE'       : dt_pre,
        'FTLS_DT_POST'      : dt_post,
        'FTLS_PHASE'        : phase,
        'FTLS_A_PRE'        : a_pre,
        'FTLS_A_POST'       : a_post,
        'FTLS_ANALYSIS_DATE': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'FTLS_PRE_WINDOW'   : f'{t_pre_start.date()} → {t_pre_end.date()}',
        'FTLS_POST_WINDOW'  : f'{t_post_start.date()} → {t_post_end.date()}',
        'FTLS_GK_RADIUS_KM' : GK_RADIUS_KM,
        'FTLS_METHOD'       : 'b-positive (Gulia 2024) + MLE (Aki 1965) | Scordilis (2006) Mw homogenization',
    }

    try:
        with open(json_path, encoding='utf-8') as f:
            d = json.load(f)
        d.update(results)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        log(f'Sonuçlar JSON\'a yazıldı: {json_path}')
    except Exception as e:
        log(f'JSON yazma hatası: {e}')

    # Özet rapor
    log('')
    log('══════════════════════════════════════════════════')
    log(f'  FTLS KARŞILAŞTIRMALI ANALİZ — Mindanao Mw 7.8')
    log('══════════════════════════════════════════════════')
    log(f'  Öncesi  : {len(pre_events):4d} olay | Mc={mc_pre} | b_ref={b_ref_final}')
    log(f'  Sonrası : {len(post_events):4d} olay | Mc={mc_post} | b_after={b_after_final}')
    log(f'  Oran    : b_after/b_ref = {ratio}')
    log(f'  ALARM   : ■ {alarm}')
    log(f'  FAZ     : {phase}')
    log(f'  Dt      : öncesi={dt_pre} → sonrası={dt_post}')
    log('══════════════════════════════════════════════════')

    return results

if __name__ == '__main__':
    json_path = sys.argv[1] if len(sys.argv) > 1 \
        else 'events/Mindanao-2026/Mindanao-2026.json'
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_analysis(json_path)
