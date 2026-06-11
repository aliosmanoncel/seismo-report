"""
parse_aftershocks.py  v3.0
Kullanim: python parse_aftershocks.py INPUT/aftershocks_raw.txt

Omori-Utsu yasasi: lambda(t) = K / (c + t)^p
  → Scipy varsa curve_fit (nonlineer LS)
  → Yoksa dahili Nelder-Mead (K, c, p ayni anda optimize)
  → Grafik: lineer eksende gercek hiperbolik egri + log-log karsilastirma (2 tab)
"""

import os, sys, json, math, re
from datetime import datetime, timezone
sys.stdout.reconfigure(encoding='utf-8')

RAW = sys.argv[1] if len(sys.argv) > 1 else 'INPUT/aftershocks_raw.txt'

# ── Veri yukle ─────────────────────────────────────────────────────
with open(RAW, encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.strip() and '|' in l]

events = []
for l in lines:
    p = l.split('|')
    events.append({'id':p[0],'time':p[1],'lat':float(p[2]),'lon':float(p[3]),
                   'depth':float(p[4]),'magtype':p[9],'mag':float(p[10]),'region':p[12]})

mainshock  = max(events, key=lambda x: x['mag'])
aftershocks = [e for e in events if e['id'] != mainshock['id']]

from collections import Counter
bins = Counter()
for e in aftershocks:
    if e['mag'] >= 6.0:   bins['M6+']    += 1
    elif e['mag'] >= 5.0: bins['M5-5.9'] += 1
    elif e['mag'] >= 4.0: bins['M4-4.9'] += 1
    else:                 bins['M3-3.9'] += 1

print(f'Ana deprem : M{mainshock["mag"]} @ {mainshock["lat"]},{mainshock["lon"]}')
print(f'Artci       : {len(aftershocks)} (M6+:{bins["M6+"]} M5+:{bins["M5-5.9"]} M4+:{bins["M4-4.9"]} M3+:{bins["M3-3.9"]})')

# ── CSV ────────────────────────────────────────────────────────────
_csv_dir = os.path.dirname(RAW) if os.path.dirname(RAW) else 'events/Mindanao-2026'
base_name = os.path.basename(RAW).replace('_raw.txt','').replace('aftershocks_raw','Mindanao-2026-aftershocks')
csv_path  = os.path.join(_csv_dir, base_name + '.csv')
with open(csv_path,'w',encoding='utf-8') as f:
    f.write('EventID,Time_UTC,Lat,Lon,Depth_km,MagType,Mag,Region\n')
    for e in aftershocks:
        f.write(f"{e['id']},{e['time']},{e['lat']},{e['lon']},{e['depth']},{e['magtype']},{e['mag']},{e['region']}\n")
print(f'CSV: {csv_path}')

# ── Zaman damgalari (saat cinsinden) ──────────────────────────────
def parse_iso(s):
    s = re.sub(r'(\.\d+)?Z$','',s)
    return datetime.strptime(s[:19],'%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)

t0 = parse_iso(mainshock['time'])
dt_hours = sorted(
    (parse_iso(e['time'])-t0).total_seconds()/3600.0
    for e in aftershocks
    if (parse_iso(e['time'])-t0).total_seconds() > 0
)

# ── Log-esit aralıklı zaman bölütleri ─────────────────────────────
N_BINS   = 32
log_min  = math.log10(min(dt_hours))
log_max  = math.log10(max(dt_hours))
step     = (log_max - log_min) / N_BINS
edges    = [10**(log_min + i*step) for i in range(N_BINS+1)]

bin_t, bin_r = [], []
for i in range(N_BINS):
    lo, hi  = edges[i], edges[i+1]
    count   = sum(1 for t in dt_hours if lo <= t < hi)
    width   = hi - lo
    rate    = count / width
    if rate > 0:
        bin_t.append((lo+hi)/2)
        bin_r.append(rate)

# ── Omori modeli ───────────────────────────────────────────────────
def omori(t, K, c, p):
    return K / (c + t)**p

def sse(params):
    K, c, p = params
    if K <= 0 or c <= 0.0001 or p <= 0.05 or p > 5:
        return 1e18
    return sum((omori(t,K,c,p)-r)**2 for t,r in zip(bin_t,bin_r))

# ── Scipy varsa curve_fit, yoksa Nelder-Mead ──────────────────────
try:
    from scipy.optimize import curve_fit
    import numpy as np
    popt, pcov = curve_fit(
        omori, bin_t, bin_r,
        p0=[10.0, 0.1, 1.0],
        bounds=([0.01, 1e-4, 0.1],[1e5, 20, 4]),
        maxfev=20000
    )
    K_fit, c_fit, p_fit = popt
    perr = np.sqrt(np.diag(pcov))
    p_err = perr[2]
    method = 'scipy curve_fit (nonlineer LS)'
except Exception:
    # Nelder-Mead (scipy olmadan)
    def nelder_mead(f, x0, tol=1e-9, max_iter=8000):
        n   = len(x0)
        alpha, gamma_, rho, sigma = 1.0, 2.0, 0.5, 0.5
        simplex = [list(x0)]
        for i in range(n):
            pt = list(x0)
            pt[i] *= 1.5 if abs(pt[i]) > 1e-8 else 0.5
            simplex.append(pt)
        for _ in range(max_iter):
            simplex.sort(key=f)
            best = simplex[0]; worst = simplex[-1]; sw = simplex[-2]
            if f(worst) - f(best) < tol:
                break
            centroid = [sum(s[i] for s in simplex[:-1])/n for i in range(n)]
            refl     = [centroid[i]+alpha*(centroid[i]-worst[i]) for i in range(n)]
            if f(refl) < f(best):
                expan = [centroid[i]+gamma_*(refl[i]-centroid[i]) for i in range(n)]
                simplex[-1] = expan if f(expan)<f(refl) else refl
            elif f(refl) < f(sw):
                simplex[-1] = refl
            else:
                contr = [centroid[i]+rho*(worst[i]-centroid[i]) for i in range(n)]
                if f(contr) < f(worst):
                    simplex[-1] = contr
                else:
                    simplex = [simplex[0]] + [
                        [simplex[0][i]+sigma*(s[i]-simplex[0][i]) for i in range(n)]
                        for s in simplex[1:]
                    ]
        return simplex[0]

    result    = nelder_mead(sse, [10.0, 0.1, 1.0])
    K_fit, c_fit, p_fit = result
    p_err  = None
    method = 'Nelder-Mead (nonlineer LS, scipy yok)'

K_fit = round(K_fit, 4)
c_fit = round(c_fit, 4)
p_fit = round(p_fit, 4)

# R² (lineer uzayda — gercek fit kalitesi)
y_mean = sum(bin_r)/len(bin_r)
ss_res = sum((r - omori(t,K_fit,c_fit,p_fit))**2 for t,r in zip(bin_t,bin_r))
ss_tot = sum((r - y_mean)**2                      for r in bin_r)
r2     = round(1 - ss_res/ss_tot, 4) if ss_tot > 0 else 0

print(f'\n── Omori-Utsu ({method}) ───────────')
print(f'  lambda(t) = K / (c + t)^p')
print(f'  K = {K_fit}')
print(f'  c = {c_fit} saat')
print(f'  p = {p_fit}  {"±"+str(round(p_err,3)) if p_err else ""}  (tipik: 0.8–1.2)')
print(f'  R² (lineer uzay) = {r2}')
if   p_fit < 0.8: print('  Yorum: Dusuk p → uzun sureli aktif artci zonu')
elif p_fit > 1.2: print('  Yorum: Yuksek p → artci aktivitesi hizla sonumleniyor')
else:             print('  Yorum: Normal p → tipik artci sismisitesi (0.8-1.2)')

# ── Omori log-log grafik verileri ─────────────────────────────────
obs_log = [{'x':round(math.log10(t),4),'y':round(math.log10(r),4)} for t,r in zip(bin_t,bin_r)]

N_FIT  = 120
fit_log = []
for i in range(N_FIT):
    t = 10**(log_min + i*(log_max-log_min)/(N_FIT-1))
    r = omori(t, K_fit, c_fit, p_fit)
    if r > 0:
        fit_log.append({'x':round(math.log10(t),4),'y':round(math.log10(r),6)})

obs_log_js = json.dumps(obs_log)
fit_log_js = json.dumps(fit_log)

# ── Gutenberg-Richter: kumulatif N(>=M) ───────────────────────────
mags_all = sorted([e['mag'] for e in aftershocks])
# Scordilis (2006) mb/m → Mw donusumu
# Mw = 0.85*mb + 1.03  (±0.29)  [3.5 ≤ mb ≤ 6.2]
def mb_to_mw(mb):
    return round(0.85 * mb + 1.03, 2)

mags_mw = []
for e in aftershocks:
    mt = e.get('magtype', 'm').lower()
    m  = e['mag']
    if mt == 'mw':
        mags_mw.append(m)
    else:
        mags_mw.append(mb_to_mw(m))
mags_mw = sorted(mags_mw)

# ── GR gözlem noktalari (ham + Mw) ───────────────────────────────
M_MIN = math.floor(min(mags_all)*10)/10
M_MAX = math.ceil(max(mags_all)*10)/10
gr_steps = [round(M_MIN + i*0.1, 1) for i in range(int((M_MAX-M_MIN)/0.1)+1)]
gr_obs   = []
gr_obs_mw = []
for m in gr_steps:
    n_raw = sum(1 for x in mags_all if x >= m)
    n_mw  = sum(1 for x in mags_mw  if x >= m)
    if n_raw > 0:
        gr_obs.append({'x': m, 'y': round(math.log10(n_raw), 4)})
    if n_mw > 0:
        gr_obs_mw.append({'x': m, 'y': round(math.log10(n_mw), 4)})

# ── b-değeri: tek çizgi (Mc=3.5, ham büyüklük) ───────────────────
M_C   = 3.5   # katalog tamamlanma büyüklüğü (max eğrilik yöntemiyle ~3.5)
mags_c = [x for x in mags_all if x >= M_C]
M_mean = sum(mags_c)/len(mags_c)
b_val  = round(math.log10(math.e) / (M_mean - M_C + 0.05), 4)
a_val  = round(math.log10(len(mags_c)) + b_val * M_C, 4)
gr_fit = [{'x': round(m,1), 'y': round(a_val - b_val*m, 4)}
          for m in [M_C + i*0.1 for i in range(int((M_MAX-M_C)/0.1)+2)]
          if a_val - b_val*m > 0]

# ── İki segmentli fit: M_C–5.0 (Segment 1) ve M5.0+ (Segment 2) ──
M_BREAK = 5.0
# Segment 1
seg1 = [x for x in mags_all if M_C <= x < M_BREAK]
if len(seg1) >= 5:
    b1 = round(math.log10(math.e) / (sum(seg1)/len(seg1) - M_C + 0.05), 4)
    a1 = round(math.log10(sum(1 for x in mags_all if x >= M_C)) + b1 * M_C, 4)
    gr_fit1 = [{'x': round(m,1), 'y': round(a1 - b1*m, 4)}
               for m in [M_C + i*0.1 for i in range(int((M_BREAK-M_C)/0.1)+1)]
               if a1 - b1*m > 0]
else:
    b1, a1, gr_fit1 = b_val, a_val, []

# Segment 2
seg2 = [x for x in mags_all if x >= M_BREAK]
if len(seg2) >= 4:
    b2 = round(math.log10(math.e) / (sum(seg2)/len(seg2) - M_BREAK + 0.05), 4)
    a2 = round(math.log10(sum(1 for x in mags_all if x >= M_BREAK)) + b2 * M_BREAK, 4)
    gr_fit2 = [{'x': round(m,1), 'y': round(a2 - b2*m, 4)}
               for m in [M_BREAK + i*0.1 for i in range(int((M_MAX-M_BREAK)/0.1)+2)]
               if a2 - b2*m > 0]
else:
    b2, a2, gr_fit2 = 0, 0, []

print(f'\n── Gutenberg-Richter ──────────────────────────')
print(f'  Tek çizgi (Mc={M_C}): a={a_val}  b={b_val}')
print(f'  Segment 1 (M{M_C}–{M_BREAK}): b1={b1}  N={len(seg1)}')
print(f'  Segment 2 (M{M_BREAK}+):     b2={b2}  N={len(seg2)}')
print(f'  Slope break at M={M_BREAK} → magnitude heterogeneity (mb vs Mw)')

gr_obs_js    = json.dumps(gr_obs)
gr_fit_js    = json.dumps(gr_fit)
gr_obs_mw_js = json.dumps(gr_obs_mw)
gr_fit1_js   = json.dumps(gr_fit1)
gr_fit2_js   = json.dumps(gr_fit2)
b1_val = b1; b2_val = b2; M_BREAK_val = M_BREAK

# ── Korelasyon Boyutu Dc (Grassberger-Procaccia) ──────────────────
# 2D uzaysal veri: lat/lon (derece), Öklid mesafesi
pts = [(e['lat'], e['lon']) for e in aftershocks]
N_pts = len(pts)

# Log-esit r degerleri (derece cinsinden: ~0.01° ≈ 1 km, ~3° ≈ 300 km)
R_MIN, R_MAX, N_R = 0.02, 4.0, 40
r_vals = [R_MIN * (R_MAX/R_MIN)**(i/(N_R-1)) for i in range(N_R)]

# Tum cift mesafeleri hesapla (bir kez)
print(f'\n── Korelasyon Boyutu (GP algoritması, N={N_pts}) ──────────')
pair_dists = []
for i in range(N_pts):
    for j in range(i+1, N_pts):
        d = math.sqrt((pts[i][0]-pts[j][0])**2 + (pts[i][1]-pts[j][1])**2)
        pair_dists.append(d)
pair_dists.sort()
N_pairs = len(pair_dists)  # = N*(N-1)/2

# C(r) = (cift sayisi < r) / toplam cift
def count_lt(dists, r):
    lo, hi = 0, len(dists)
    while lo < hi:
        mid = (lo+hi)//2
        if dists[mid] < r: lo = mid+1
        else: hi = mid
    return lo

C_vals = [count_lt(pair_dists, r) / N_pairs for r in r_vals]

# Lineer bolge: C>0 ve C<0.98 (doyum oncesi)
lr_pts = [(math.log10(r), math.log10(C))
          for r, C in zip(r_vals, C_vals) if 0 < C < 0.98]

# En az kareler egimi = Dc
n = len(lr_pts)
sx  = sum(x for x,y in lr_pts)
sy  = sum(y for x,y in lr_pts)
sx2 = sum(x**2 for x,y in lr_pts)
sxy = sum(x*y  for x,y in lr_pts)
denom = n*sx2 - sx**2
Dc    = round((n*sxy - sx*sy)/denom, 4) if denom else 0
Dc_a  = round((sy - Dc*sx)/n, 4)  # intercept

# R² Dc icin
y_vals = [y for _,y in lr_pts]
y_mean = sum(y_vals)/len(y_vals)
ss_res = sum((y - (Dc*x+Dc_a))**2 for x,y in lr_pts)
ss_tot = sum((y - y_mean)**2 for y in y_vals)
Dc_r2  = round(1 - ss_res/ss_tot, 4) if ss_tot else 0

print(f'  Dc = {Dc}  (intercept={Dc_a})  R²={Dc_r2}')
if   Dc < 1.3: print('  Yorum: Guclu kümeleme (lineer artci zinciri)')
elif Dc < 1.7: print('  Yorum: Orta kuemeleme (yaygin artci alani)')
else:          print('  Yorum: Daginik artci dagilimi (bolgesel alan)')

# Dc grafik verileri
dc_obs = [{'x':round(math.log10(r),4),'y':round(math.log10(C),4)}
          for r,C in zip(r_vals,C_vals) if C > 0]
x_fit_min = min(x for x,y in lr_pts)
x_fit_max = max(x for x,y in lr_pts)
dc_fit = [{'x':round(x_fit_min + i*(x_fit_max-x_fit_min)/39, 4),
           'y':round(Dc*(x_fit_min + i*(x_fit_max-x_fit_min)/39)+Dc_a, 4)}
          for i in range(40)]

dc_obs_js = json.dumps(dc_obs)
dc_fit_js = json.dumps(dc_fit)

# ── Zamansal Kümelenme İndeksi Dt ─────────────────────────────────
# dt_hours zaten sirali
inter_ev = [dt_hours[i+1] - dt_hours[i] for i in range(len(dt_hours)-1)]
mean_dt  = sum(inter_ev) / len(inter_ev)
norm_dt  = [d / mean_dt for d in inter_ev]
short_ratio = sum(1 for d in norm_dt if d < 0.5) / len(norm_dt)
Dt       = round(short_ratio - 0.5, 4)

print(f'\n── Zamansal Kümelenme (Dt) ─────────────────────────────')
print(f'  Dt = {Dt}')
if   Dt >  0.15: print('  Yorum: Güçlü zamansal kümelenme (Poisson değil)')
elif Dt > -0.05: print('  Yorum: Zayıf/orta kümelenme')
else:            print('  Yorum: Düzenli artçı dizisi (Poisson altı)')

# Inter-event zaman histogrami (normalize edilmis) → Dc tabina ekle
N_HIST  = 20
hist_max = min(sorted(inter_ev)[int(len(inter_ev)*0.95)], mean_dt*5)  # 95. persentil
hist_w   = hist_max / N_HIST
hist_counts = [0]*N_HIST
for d in inter_ev:
    b = int(d / hist_w)
    if 0 <= b < N_HIST:
        hist_counts[b] += 1
hist_total = sum(hist_counts)
# Normalize: yogunluk
hist_data = [{'x': round((i+0.5)*hist_w, 4),
              'y': round(hist_counts[i]/(hist_total*hist_w), 4)}
             for i in range(N_HIST)]
# Üstel beklenti (Poisson): lambda * exp(-lambda * t), lambda = 1/mean_dt
lam = 1.0 / mean_dt
hist_exp  = [{'x': round((i+0.5)*hist_w, 4),
              'y': round(lam * math.exp(-lam*(i+0.5)*hist_w), 6)}
             for i in range(N_HIST)]

hist_data_js = json.dumps(hist_data)
hist_exp_js  = json.dumps(hist_exp)

Dt_yorum = ('Güçlü zamansal kümelenme — artçılar kısa aralıklarla yoğunlaştı'
            if Dt > 0.15 else
            'Orta kümelenme — zaman dağılımı Poisson\'a yakın'
            if Dt > -0.05 else
            'Düzenli artçı dizisi')

# ── DYFI GeoJSON verisini hazirla ─────────────────────────────────
import urllib.request as _ur

def _cdi_color(cdi):
    if cdi >= 9.0: return '#b30000'
    if cdi >= 8.0: return '#ff0000'
    if cdi >= 7.0: return '#ff6600'
    if cdi >= 6.0: return '#ffaa00'
    if cdi >= 5.0: return '#ffe000'
    if cdi >= 4.0: return '#90ee90'
    if cdi >= 3.0: return '#add8e6'
    return '#c0c0c0'

_dyfi_compact = []
try:
    _DYFI_URL = ('https://earthquake.usgs.gov/product/dyfi/us7000lff4/us/'
                 '1777917204474/dyfi_geo_10km.geojson')
    _gj = json.loads(_ur.urlopen(
        _ur.Request(_DYFI_URL, headers={'User-Agent':'Mozilla/5.0'}), timeout=20
    ).read())
    for _feat in _gj['features']:
        _cdi = _feat['properties'].get('cdi', 0)
        if _cdi < 2: continue
        _nm  = _feat['properties'].get('name','').split('<br>')[-1].strip()[:40]
        _dist= _feat['properties'].get('dist', '?')
        _nr  = _feat['properties'].get('nresp', 0)
        _coords = [[round(c[0],4), round(c[1],4)]
                   for c in _feat['geometry']['coordinates'][0]]
        _dyfi_compact.append({'cdi':round(_cdi,1),'name':_nm,'dist':_dist,
                               'nresp':_nr,'coords':_coords,'color':_cdi_color(_cdi)})
    _dyfi_compact.sort(key=lambda x: x['cdi'], reverse=True)
    print(f'DYFI: {len(_dyfi_compact)} poligon, {sum(f["nresp"] for f in _dyfi_compact)} yanit')
except Exception as _e:
    print(f'DYFI yuklenemedi: {_e}')

dyfi_js_data = json.dumps(_dyfi_compact)

# ── ShakeMap verilerini yukle (INPUT/shakemap_*.json) ─────────────
# Kaynak: USGS GeoJSON API → ShakeMap zaman damgali URL'den cekildi.
# MMI konturlari: alet bazli yogunluk izohipsleri (cont_mmi.json)
# PGA konturlari: zemin ivme izohipsleri, yapi hasarinda kullanilir (cont_pga.json)
# Rupture: fay kirigi yuzey projeksiyonu, artci yonunu aciklar (rupture.json)
# Stations: olcum noktaları — ShakeMap'in alet dayanagini kanitlar (stationlist.json)

def _mmi_color(v):
    if v >= 7.0: return '#ff0000'
    if v >= 6.0: return '#ff8c00'
    if v >= 5.5: return '#ffd600'
    if v >= 5.0: return '#aaff00'
    if v >= 4.5: return '#44cc44'
    if v >= 4.0: return '#00cccc'
    if v >= 3.5: return '#66bbff'
    return '#aaaaaa'

def _mmi_label(v):
    labels = {3.5:'III Zayif',4.0:'IV Hafif',4.5:'IV-V',5.0:'V Orta',
              5.5:'V-VI',6.0:'VI Kuvvetli',6.5:'VI-VII',7.0:'VII Cok Kuvvetli'}
    return labels.get(v, f'MMI {v}')

def _pga_color(v):
    if v >= 50:  return '#b30000'
    if v >= 20:  return '#ff0000'
    if v >= 10:  return '#ff6600'
    if v >= 5:   return '#ffaa00'
    if v >= 2:   return '#ffe000'
    if v >= 1:   return '#90ee90'
    return '#add8e6'

_sm_mmi_lines, _sm_pga_lines, _sm_rup_segs, _sm_sta_pts = [], [], [], []

_RAW_DIR = os.path.dirname(RAW) if os.path.dirname(RAW) else 'events/Mindanao-2026'
_SM_MMI = os.path.join(_RAW_DIR, 'shakemap_cont_mmi.json')
_SM_PGA = os.path.join(_RAW_DIR, 'shakemap_cont_pga.json')
_SM_RUP = os.path.join(_RAW_DIR, 'shakemap_rupture.json')
_SM_STA = os.path.join(_RAW_DIR, 'shakemap_stationlist.json')

def _extract_lines(filepath, color_fn, label_fn):
    lines_out = []
    try:
        with open(filepath, encoding='utf-8') as _f:
            _gj = json.load(_f)
        for feat in _gj['features']:
            v    = feat['properties']['value']
            col  = color_fn(v)
            lbl  = label_fn(v)
            geom = feat['geometry']
            segs = geom['coordinates'] if geom['type']=='MultiLineString' else [geom['coordinates']]
            for seg in segs:
                pts = [[round(c[1],4), round(c[0],4)] for c in seg]
                lines_out.append({'v':v,'col':col,'lbl':lbl,'pts':pts})
    except Exception as _ex:
        print(f'ShakeMap {filepath} yuklenemedi: {_ex}')
    return lines_out

_sm_mmi_lines = _extract_lines(_SM_MMI, _mmi_color, _mmi_label)
_sm_pga_lines = _extract_lines(_SM_PGA, _pga_color, lambda v: f'PGA {v}%g')

try:
    with open(_SM_RUP, encoding='utf-8') as _f:
        _rj = json.load(_f)
    for feat in _rj.get('features', []):
        geom = feat.get('geometry')
        if not geom: continue
        gtype = geom['type']
        if gtype == 'MultiLineString':
            for seg in geom['coordinates']:
                _sm_rup_segs.append([[round(c[1],4), round(c[0],4)] for c in seg])
        elif gtype == 'LineString':
            _sm_rup_segs.append([[round(c[1],4), round(c[0],4)] for c in geom['coordinates']])
        elif gtype == 'MultiPolygon':
            # Her polygon'un dis halkasini cizgi olarak al
            for poly in geom['coordinates']:
                _sm_rup_segs.append([[round(c[1],4), round(c[0],4)] for c in poly[0]])
        elif gtype == 'Polygon':
            _sm_rup_segs.append([[round(c[1],4), round(c[0],4)] for c in geom['coordinates'][0]])
except Exception as _ex:
    print(f'Rupture yuklenemedi: {_ex}')

try:
    with open(_SM_STA, encoding='utf-8') as _f:
        _sj = json.load(_f)
    for feat in _sj.get('features', []):
        p = feat['properties']; g = feat.get('geometry')
        if not g: continue
        lon, lat = g['coordinates'][:2]
        _sm_sta_pts.append({
            'lat':round(lat,4),'lon':round(lon,4),
            'code':p.get('code','?')[:20],
            'name':(p.get('name') or p.get('code','?'))[:35],
            'net':p.get('network','?'),
            'type':p.get('station_type','?'),
            'mmi':p.get('intensity'),'pga':p.get('pga'),
            'dist':round(p.get('distance',0),1)
        })
except Exception as _ex:
    print(f'Stations yuklenemedi: {_ex}')

print(f'ShakeMap: {len(_sm_mmi_lines)} MMI seg, {len(_sm_pga_lines)} PGA seg, '
      f'{len(_sm_rup_segs)} rupture seg, {len(_sm_sta_pts)} station')

sm_mmi_js = json.dumps(_sm_mmi_lines)
sm_pga_js = json.dumps(_sm_pga_lines)
sm_rup_js = json.dumps(_sm_rup_segs)
sm_sta_js = json.dumps(_sm_sta_pts)

# ── Leaflet JS (tam ekran destekli) ───────────────────────────────
after_rows = []
for e in aftershocks:
    t2 = e['time'][:16].replace('T',' ')
    after_rows.append(f"  [{e['lat']},{e['lon']},{e['mag']},{e['depth']},\"{t2}\",\"{e['region']}\"]")
after_js_array = '[\n' + ',\n'.join(after_rows) + '\n]'

AFTERSHOCK_MAP_JS = f"""
// ── Artci Haritasi (tam ekran destekli, bagimsiz) ──────────────────
(function() {{
  var mapEl = document.getElementById('aftershock-map');
  if (!mapEl) return;

  // Leaflet CSS ekle (yoksa)
  if (!document.querySelector('link[href*="leaflet"]')) {{
    var lnk = document.createElement('link');
    lnk.rel = 'stylesheet';
    lnk.href = 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.css';
    document.head.appendChild(lnk);
  }}

  // Tam ekran butonu
  var wrap = document.getElementById('aftershock-map-wrap');
  if (wrap) {{
    var btn = document.createElement('button');
    btn.id = 'as-fs-btn'; btn.title = 'Tam Ekran'; btn.innerHTML = '⛶';
    btn.style.cssText = 'position:absolute;top:10px;right:10px;z-index:1000;'
      +'background:rgba(10,14,21,0.85);color:#7ecbff;border:1px solid rgba(59,158,255,.4);'
      +'border-radius:6px;padding:4px 9px;font-size:16px;cursor:pointer;';
    btn.onmouseenter=function(){{this.style.background='rgba(59,158,255,.25)';}};
    btn.onmouseleave=function(){{this.style.background='rgba(10,14,21,0.85)';}};
    wrap.style.position='relative'; wrap.appendChild(btn);
    var _full=false, _origH=mapEl.style.height;
    btn.onclick=function(){{
      _full=!_full;
      if(_full){{
        wrap.style.position='fixed';
        wrap.style.top='0'; wrap.style.left='0';
        wrap.style.right='0'; wrap.style.bottom='0';
        wrap.style.zIndex='9998'; wrap.style.borderRadius='0';
        wrap.style.padding='0'; wrap.style.margin='0';
        wrap.style.background='#0a0e15'; wrap.style.width='100%';
        mapEl.style.height='100vh'; mapEl.style.borderRadius='0';
        btn.innerHTML='✕'; btn.style.top='14px'; btn.style.right='14px';
      }} else {{
        wrap.style.position='relative';
        wrap.style.top=''; wrap.style.left='';
        wrap.style.right=''; wrap.style.bottom='';
        wrap.style.zIndex=''; wrap.style.borderRadius='';
        wrap.style.padding=''; wrap.style.margin='';
        wrap.style.background=''; wrap.style.width='';
        mapEl.style.height=_origH||'460px'; mapEl.style.borderRadius='10px';
        btn.innerHTML='⛶'; btn.style.top='10px'; btn.style.right='10px';
      }}
      setTimeout(function(){{if(window._asMap)window._asMap.invalidateSize();}},250);
    }};
    document.addEventListener('keydown',function(e){{if(e.key==='Escape'&&_full)btn.onclick();}});
  }}

  // Leaflet yukle (kendisi; baska script'e bagimli degil)
  function _loadLeaflet(cb) {{
    if (window.L) {{ cb(); return; }}
    var urls = [
      'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js',
      'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    ];
    var i = 0;
    function tryNext() {{
      if (i >= urls.length) {{ console.error('Leaflet yuklenemedi'); return; }}
      var s = document.createElement('script');
      s.src = urls[i++];
      s.onload = function() {{ if (window.L) cb(); else tryNext(); }};
      s.onerror = tryNext;
      document.head.appendChild(s);
    }}
    tryNext();
  }}

  _loadLeaflet(function(){{
    var map=L.map('aftershock-map').setView([{mainshock['lat']},{mainshock['lon']}],7);
    window._asMap=map;
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{attribution:'© OpenStreetMap',maxZoom:13}}).addTo(map);
    var si=L.divIcon({{html:'<div style="font-size:30px;line-height:1;transform:translate(-50%,-50%);filter:drop-shadow(0 0 4px #ff8800)">⭐</div>',className:'',iconSize:[30,30],iconAnchor:[15,15]}});
    L.marker([{mainshock['lat']},{mainshock['lon']}],{{icon:si}})
      .bindPopup('<b>Ana Deprem</b><br>M{mainshock["mag"]} · {mainshock["time"][:16].replace("T"," ")} UTC<br>Derinlik: {mainshock["depth"]} km<br>{mainshock["region"]}').addTo(map);
    var data={after_js_array};
    data.forEach(function(d){{
      var lat=d[0],lon=d[1],mag=d[2],dep=d[3],t=d[4],reg=d[5];
      var color=mag>=6?'#ff2222':mag>=5?'#ff8800':mag>=4?'#ffd600':'#44aaff';
      var r=Math.pow(2,mag-2)*3;
      L.circleMarker([lat,lon],{{radius:r,color:color,fillColor:color,fillOpacity:0.65,weight:1}})
       .bindPopup('<b>M'+mag+'</b> · '+t+' UTC<br>Derinlik: '+dep+' km<br>'+reg).addTo(map);
    }});
    var lg=L.control({{position:'bottomright'}});
    lg.onAdd=function(){{
      var d=L.DomUtil.create('div','');
      d.style.cssText='background:rgba(10,14,21,0.88);color:#e8f0f5;padding:8px 12px;border-radius:8px;font-size:11px;line-height:1.9;border:1px solid rgba(255,255,255,.12)';
      d.innerHTML='<b style="color:#7ecbff">Artçı Lejantı</b><br>'
        +'<span style="color:#ff2222">●</span> M6+ ({bins["M6+"]})<br>'
        +'<span style="color:#ff8800">●</span> M5–5.9 ({bins["M5-5.9"]})<br>'
        +'<span style="color:#ffd600">●</span> M4–4.9 ({bins["M4-4.9"]})<br>'
        +'<span style="color:#44aaff">●</span> M3–3.9 ({bins["M3-3.9"]})<br>'
        +'⭐ Ana Deprem M{mainshock["mag"]}';
      return d;
    }};
    lg.addTo(map);

    // ── DYFI MMI katmani (USGS us7000lff4) ────────────────────────
    var dyfiData = {dyfi_js_data};
    var dyfiLayer = L.layerGroup();
    dyfiData.forEach(function(f) {{
      L.polygon(f.coords.map(function(c){{return [c[1],c[0]];}}), {{
        color: f.color, fillColor: f.color, fillOpacity: 0.45, weight: 0.5
      }}).bindPopup(
        '<b>CDI ' + f.cdi + '</b> (' + mmiLabel(f.cdi) + ')<br>' +
        f.name + '<br>' + f.dist + ' km &bull; ' + f.nresp + ' yanit'
      ).addTo(dyfiLayer);
    }});

    function mmiLabel(c) {{
      if (c>=9) return 'Siddetli/Yikici';
      if (c>=8) return 'Agir Hasar';
      if (c>=7) return 'Cok Kuvvetli';
      if (c>=6) return 'Kuvvetli';
      if (c>=5) return 'Orta';
      if (c>=4) return 'Hafif';
      if (c>=3) return 'Zayif';
      return 'Hissedilmedi';
    }}

    // DYFI toggle butonu
    var dyfiBtn = document.createElement('button');
    dyfiBtn.innerHTML = 'DYFI';
    dyfiBtn.title = 'USGS DYFI Yogunluk Haritasi';
    dyfiBtn.style.cssText = 'position:absolute;top:10px;right:52px;z-index:1000;'
      + 'background:rgba(10,14,21,0.85);color:#ffd600;border:1px solid #ffd60066;'
      + 'border-radius:6px;padding:4px 9px;font-size:12px;font-weight:700;cursor:pointer;';
    var dyfiOn = false;
    dyfiBtn.onclick = function() {{
      dyfiOn = !dyfiOn;
      if (dyfiOn) {{ dyfiLayer.addTo(map); dyfiBtn.style.background='rgba(255,214,0,.25)'; }}
      else {{ map.removeLayer(dyfiLayer); dyfiBtn.style.background='rgba(10,14,21,0.85)'; }}
    }};
    if (wrap) wrap.appendChild(dyfiBtn);

    // DYFI lejant
    var dyfiLg = L.control({{position:'bottomleft'}});
    dyfiLg.onAdd = function() {{
      var d = L.DomUtil.create('div','');
      d.style.cssText = 'background:rgba(10,14,21,0.88);color:#e8f0f5;padding:7px 11px;'
        + 'border-radius:8px;font-size:10px;line-height:1.8;border:1px solid rgba(255,255,255,.1);'
        + 'display:none;';
      d.id = 'dyfi-legend';
      d.innerHTML = '<b style="color:#ffd600">USGS DYFI (CDI)</b><br>'
        + '<span style="color:#b30000">&#9632;</span> IX+ Siddetli<br>'
        + '<span style="color:#ff0000">&#9632;</span> VIII Agir Hasar<br>'
        + '<span style="color:#ff6600">&#9632;</span> VII Cok Kuvvetli<br>'
        + '<span style="color:#ffaa00">&#9632;</span> VI Kuvvetli<br>'
        + '<span style="color:#ffe000">&#9632;</span> V Orta<br>'
        + '<span style="color:#90ee90">&#9632;</span> IV Hafif<br>'
        + '<span style="color:#add8e6">&#9632;</span> III Zayif';
      return d;
    }};
    dyfiLg.addTo(map);
    dyfiBtn.onclick = (function(orig) {{ return function() {{
      orig();
      var el = document.getElementById('dyfi-legend');
      if (el) el.style.display = dyfiOn ? 'block' : 'none';
    }}; }})(dyfiBtn.onclick);

    // ── ShakeMap Katmanlari (USGS us7000lff4, alet bazli) ────────────
    // MMI: alet bazli yogunluk izohipsleri — DYFI vatandas bildirimleriyle karsilastirin
    // PGA: zemin ivmesi (%g) — yapi hasari tahmininde kullanilir
    // Rupture: fay kirigi geometrisi — artcilarin neden kuzey-guney uzandığını aciklar
    // Stations: olcum yapan sismometreler veya DYFI noktalari
    var smMMI = {sm_mmi_js};
    var smPGA = {sm_pga_js};
    var smRup = {sm_rup_js};
    var smSta = {sm_sta_js};

    var mmiLayer = L.layerGroup();
    smMMI.forEach(function(l) {{
      L.polyline(l.pts, {{color:l.col, weight:2, opacity:0.9}})
       .bindTooltip('ShakeMap ' + l.lbl, {{sticky:true}})
       .addTo(mmiLayer);
    }});

    var pgaLayer = L.layerGroup();
    smPGA.forEach(function(l) {{
      L.polyline(l.pts, {{color:l.col, weight:1.5, opacity:0.85, dashArray:'6 3'}})
       .bindTooltip(l.lbl, {{sticky:true}})
       .addTo(pgaLayer);
    }});

    var rupLayer = L.layerGroup();
    smRup.forEach(function(seg) {{
      L.polyline(seg, {{color:'#ff44ff', weight:3.5, opacity:0.95}})
       .bindTooltip('Fay Kirigi (ShakeMap USGS)', {{sticky:true}})
       .addTo(rupLayer);
    }});
    if (smRup.length > 0) rupLayer.addTo(map);

    var staLayer = L.layerGroup();
    smSta.forEach(function(s) {{
      var col = s.type === 'macroseismic' ? '#ffd600' : '#44ffaa';
      var ic = L.divIcon({{
        html:'<div style="width:10px;height:10px;border-radius:50%;background:'+col+';border:2px solid #fff;box-shadow:0 0 4px rgba(0,0,0,.5)"></div>',
        className:'', iconSize:[10,10], iconAnchor:[5,5]
      }});
      L.marker([s.lat, s.lon], {{icon:ic}})
       .bindPopup('<b>'+s.code+'</b><br>'+s.name+'<br>Tip: '+s.type+' | Net: '+s.net+
                 '<br>MMI: '+(s.mmi||'?')+' | PGA: '+(s.pga||'?')+'%g<br>Mesafe: '+s.dist+' km')
       .addTo(staLayer);
    }});

    // ShakeMap toggle butonlari
    function _mkSmBtn(label, color, title, rightPx) {{
      var b = document.createElement('button');
      b.innerHTML = label; b.title = title;
      b.style.cssText = 'position:absolute;top:10px;z-index:1000;'
        + 'background:rgba(10,14,21,0.85);color:'+color+';'
        + 'border:1px solid '+color+'66;'
        + 'border-radius:6px;padding:4px 7px;font-size:11px;cursor:pointer;';
      b.style.right = rightPx + 'px';
      return b;
    }}

    var btnMMI = _mkSmBtn('MMI','#66bbff','ShakeMap MMI izokonturlari (alet bazli)',100);
    var btnPGA = _mkSmBtn('PGA','#90ee90','PGA ivme izokonturlari',144);
    var btnSTA = _mkSmBtn('STA','#44ffaa','Sismik istasyon/DYFI noktalari',188);
    var smBtns = {{MMI:[mmiLayer,btnMMI], PGA:[pgaLayer,btnPGA], STA:[staLayer,btnSTA]}};
    Object.keys(smBtns).forEach(function(k) {{
      var lay=smBtns[k][0], btn=smBtns[k][1], on=false;
      btn.onclick = function() {{
        on = !on;
        if (on) {{ lay.addTo(map); btn.style.background='rgba(255,255,255,.15)'; btn.style.fontWeight='700'; }}
        else    {{ map.removeLayer(lay); btn.style.background='rgba(10,14,21,0.85)'; btn.style.fontWeight='normal'; }}
      }};
      if (wrap) wrap.appendChild(btn);
    }});

    // ShakeMap MMI lejant
    var smLg = L.control({{position:'topright'}});
    smLg.onAdd = function() {{
      var d = L.DomUtil.create('div','');
      d.style.cssText = 'background:rgba(10,14,21,0.88);color:#e8f0f5;padding:7px 10px;'
        + 'border-radius:8px;font-size:10px;line-height:1.85;border:1px solid rgba(255,255,255,.1);margin-top:50px;';
      d.innerHTML = '<b style="color:#66bbff">ShakeMap</b> <span style="color:#7a9ab5;font-size:.85em">(alet)</span><br>'
        + '<span style="color:#ff0000">&#9135;</span> VII+ Cok Kuvvetli<br>'
        + '<span style="color:#ff8c00">&#9135;</span> VI Kuvvetli<br>'
        + '<span style="color:#ffd600">&#9135;</span> V-VI<br>'
        + '<span style="color:#aaff00">&#9135;</span> V Orta<br>'
        + '<span style="color:#44cc44">&#9135;</span> IV Hafif<br>'
        + '<span style="color:#00cccc">&#9135;</span> III-IV<br>'
        + '<span style="color:#66bbff">&#9135;</span> III Zayif<br>'
        + '<span style="color:#ff44ff">&#9135;&#9135;</span> Fay Kirigi<br>'
        + '<span style="color:#44ffaa">&#9679;</span> Sismometre '
        + '<span style="color:#ffd600">&#9679;</span> DYFI';
      return d;
    }};
    smLg.addTo(map);

  }});
}})();
"""

# ── Chart JS (Omori log-log + Gutenberg-Richter 2 tab) ────────────
p_err_str = f'±{round(p_err,3)}' if p_err else ''
if   p_fit < 0.8: p_yorum = 'Düşük p — uzun süreli aktif artçı zonu'
elif p_fit > 1.2: p_yorum = 'Yüksek p — artçı aktivitesi hızla sönümleniyor'
else:             p_yorum = 'Normal p — tipik artçı sismisitesi (0.8–1.2 aralığı)'
b_yorum = 'yüksek b — küçük depremler baskın' if b_val > 1.0 else 'düşük b — büyük artçılar görece önemli'

OMORI_CHART_JS = f"""
// ── Sismik İstatistik Grafikleri (Omori log-log + G-R) ────────────
(function() {{
  var canvasOmori = document.getElementById('omori-chart-log');
  var canvasGR    = document.getElementById('omori-chart-gr');
  if (!canvasOmori && !canvasGR) return;

  var obsLog  = {obs_log_js};
  var fitLog  = {fit_log_js};
  var grObs   = {gr_obs_js};
  var grFit   = {gr_fit_js};
  var dcObs   = {dc_obs_js};
  var dcFit   = {dc_fit_js};
  var histData = {hist_data_js};
  var histExp  = {hist_exp_js};
  var grObsMw  = {gr_obs_mw_js};
  var grFit1   = {gr_fit1_js};
  var grFit2   = {gr_fit2_js};
  var mBreak   = {M_BREAK_val};

  var labelOmori = 'Omori-Utsu  p={p_fit}{p_err_str}  K={K_fit}  c={c_fit}h  R²={r2}';
  var labelGR    = 'G-R fit  log N = {a_val} − {b_val}·M  (b={b_val}, Mc={M_C})';
  var labelGR1   = 'Seg-1 (M{M_C}–{M_BREAK_val}): b={b1_val}  [mb/m]';
  var labelGR2   = 'Seg-2 (M{M_BREAK_val}+): b={b2_val}  [Mw doğal]';
  var labelGRmw  = 'Mw-dönüştürülmüş (Scordilis 2006)';
  var labelDc    = 'GP fit  Dc={Dc}  R²={Dc_r2}';

  function loadChartJS(cb) {{
    if (window.Chart) {{ cb(); return; }}
    var s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js';
    s.onload = cb;
    s.onerror = function() {{
      var s2 = document.createElement('script');
      s2.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js';
      s2.onload = cb; document.head.appendChild(s2);
    }};
    document.head.appendChild(s);
  }}

  var DARK = {{
    obs: {{ bg:'rgba(59,158,255,0.75)', border:'#3b9eff' }},
    gr:  {{ bg:'rgba(100,220,130,0.75)', border:'#44dd88' }},
    fit: {{ border:'#ff8800' }},
    grfit: {{ border:'#ffdd44' }},
    tick: '#94a3b8', grid: 'rgba(255,255,255,0.07)', legend: '#c8d8e8'
  }};

  function makeScatterLine(canvas, obsData, obsLabel, obsBg, obsBorder,
                            fitData, fitLabel, fitColor,
                            xLabel, yLabel, tooltipFn) {{
    return new Chart(canvas, {{
      type: 'scatter',
      data: {{
        datasets: [
          {{ label: obsLabel, data: obsData,
             backgroundColor: obsBg, borderColor: obsBorder,
             pointRadius: 5, pointHoverRadius: 7, type: 'scatter' }},
          {{ label: fitLabel, data: fitData, type: 'line',
             borderColor: fitColor, borderWidth: 2.5,
             backgroundColor: 'transparent', pointRadius: 0, tension: 0 }}
        ]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        scales: {{
          x: {{ type:'linear', title:{{display:true,text:xLabel,color:DARK.tick}},
               ticks:{{color:DARK.tick}}, grid:{{color:DARK.grid}} }},
          y: {{ type:'linear', title:{{display:true,text:yLabel,color:DARK.tick}},
               ticks:{{color:DARK.tick}}, grid:{{color:DARK.grid}} }}
        }},
        plugins: {{
          legend: {{ labels:{{color:DARK.legend,font:{{size:11}},boxWidth:14}} }},
          tooltip: {{ callbacks: {{ label: tooltipFn }} }}
        }}
      }}
    }});
  }}

  // Tab geçisi — scope icinde tum .omori-tab-btn / .omori-tab-pane
  function setupTabs() {{
    var tabs  = document.querySelectorAll('.omori-tab-btn');
    var panes = document.querySelectorAll('.omori-tab-pane');
    tabs.forEach(function(btn) {{
      btn.onclick = function() {{
        tabs.forEach(function(b) {{
          b.style.background='transparent'; b.style.color='#7a9ab5';
          b.style.borderBottom='2px solid transparent';
        }});
        panes.forEach(function(p) {{ p.style.display='none'; }});
        btn.style.background='rgba(59,158,255,.12)';
        btn.style.color='#7ecbff'; btn.style.borderBottom='2px solid #3b9eff';
        document.getElementById(btn.dataset.tab).style.display='block';
        var canv = document.getElementById(btn.dataset.tab).querySelector('canvas');
        if (canv && canv._ci) canv._ci.resize();
      }};
    }});
  }}

  loadChartJS(function() {{
    setupTabs();

    if (canvasOmori) {{
      var c1 = makeScatterLine(canvasOmori,
        obsLog, 'Gözlenen artçı hızı', DARK.obs.bg, DARK.obs.border,
        fitLog, labelOmori, DARK.fit.border,
        'log10(t)  [saat]', 'log10(rate) [dep/saat]',
        function(ctx) {{
          return ctx.datasetIndex===0
            ? 'log t='+ctx.parsed.x.toFixed(2)+'  log rate='+ctx.parsed.y.toFixed(3)
            : 'fit';
        }});
      canvasOmori._ci = c1;
    }}

    if (canvasGR) {{
      var c2 = new Chart(canvasGR, {{
        type: 'scatter',
        data: {{
          datasets: [
            {{ label: 'log N(>=M) — ham', data: grObs,
               backgroundColor: DARK.gr.bg, borderColor: DARK.gr.border,
               pointRadius: 5, pointHoverRadius: 7, type: 'scatter' }},
            {{ label: labelGRmw, data: grObsMw, type: 'scatter',
               backgroundColor: 'rgba(255,160,50,0.55)', borderColor: '#ffa032',
               pointRadius: 4, pointHoverRadius: 6, pointStyle: 'triangle' }},
            {{ label: labelGR, data: grFit, type: 'line',
               borderColor: DARK.grfit.border, borderWidth: 1.8,
               backgroundColor: 'transparent', pointRadius: 0,
               borderDash: [6,4], tension: 0 }},
            {{ label: labelGR1, data: grFit1, type: 'line',
               borderColor: '#44ddff', borderWidth: 2.5,
               backgroundColor: 'transparent', pointRadius: 0, tension: 0 }},
            {{ label: labelGR2, data: grFit2, type: 'line',
               borderColor: '#ff5588', borderWidth: 2.5,
               backgroundColor: 'transparent', pointRadius: 0, tension: 0 }}
          ]
        }},
        options: {{
          responsive: true, maintainAspectRatio: false,
          scales: {{
            x: {{ type:'linear', title:{{display:true,text:'Magnitude M',color:DARK.tick}},
                 ticks:{{color:DARK.tick}}, grid:{{color:DARK.grid}} }},
            y: {{ type:'linear', title:{{display:true,text:'log10 N(>=M)',color:DARK.tick}},
                 ticks:{{color:DARK.tick}}, grid:{{color:DARK.grid}} }}
          }},
          plugins: {{
            legend: {{ labels:{{color:DARK.legend,font:{{size:10}},boxWidth:12}} }},
            tooltip: {{ callbacks: {{ label: function(ctx) {{
              return ctx.datasetIndex < 2
                ? 'M='+ctx.parsed.x.toFixed(1)+'  logN='+ctx.parsed.y.toFixed(2)
                : ctx.dataset.label;
            }} }} }},
            annotation: typeof ChartAnnotation !== 'undefined' ? {{
              annotations: {{ line1: {{
                type:'line', xMin:mBreak, xMax:mBreak,
                borderColor:'rgba(255,200,50,0.5)', borderWidth:1.5,
                borderDash:[4,3],
                label:{{content:'slope break M'+mBreak,display:true,
                        color:'#ffcc32',font:{{size:10}},position:'start'}}
              }} }}
            }} : {{}}
          }}
        }}
      }});
      canvasGR._ci = c2;
    }}

    var canvasDc = document.getElementById('omori-chart-dc');
    if (canvasDc) {{
      // Sol: Dc log-log | Sag: Dt histogram — ikisi yan yana canvas olarak degil,
      // Chart.js dual-dataset ile gostermek yerine ayri canvas kullan
      var c3 = makeScatterLine(canvasDc,
        dcObs, 'C(r)  [korelasyon integrali]',
        'rgba(180,100,255,0.75)', '#b464ff',
        dcFit, labelDc, '#ff44aa',
        'log10(r)  [derece]', 'log10 C(r)',
        function(ctx) {{
          return ctx.datasetIndex===0
            ? 'log r='+ctx.parsed.x.toFixed(2)+'  log C='+ctx.parsed.y.toFixed(3)
            : 'Dc fit';
        }});
      canvasDc._ci = c3;
    }}

    var canvasDt = document.getElementById('omori-chart-dt');
    if (canvasDt) {{
      new Chart(canvasDt, {{
        type: 'bar',
        data: {{
          datasets: [
            {{ label: 'Gözlenen yoğunluk  (Dt={Dt})',
               data: histData, backgroundColor:'rgba(255,180,50,0.65)',
               borderColor:'#ffaa22', borderWidth:1, type:'bar' }},
            {{ label: 'Poisson beklentisi (üstel)',
               data: histExp, type:'line',
               borderColor:'#44ddff', borderWidth:2,
               backgroundColor:'transparent', pointRadius:0, tension:0.4 }}
          ]
        }},
        options: {{
          responsive:true, maintainAspectRatio:false,
          scales: {{
            x: {{ type:'linear', offset:false,
                 title:{{display:true,text:'Artçılar Arası Süre (saat)',color:DARK.tick}},
                 ticks:{{color:DARK.tick}}, grid:{{color:DARK.grid}} }},
            y: {{ title:{{display:true,text:'Yoğunluk',color:DARK.tick}},
                 ticks:{{color:DARK.tick}}, grid:{{color:DARK.grid}} }}
          }},
          plugins:{{
            legend:{{labels:{{color:DARK.legend,font:{{size:11}},boxWidth:14}}}},
            tooltip:{{callbacks:{{label:function(ctx){{
              return ctx.dataset.type==='bar'
                ? 'Δt='+ctx.parsed.x.toFixed(2)+'h  dens='+ctx.parsed.y.toFixed(4)
                : 'Poisson';
            }}}}}}
          }}
        }}
      }});
    }}
  }});
}})();
"""

# ── Grafik HTML blogu (2 tab: Omori + GR) ────────────────────────
OMORI_HTML = f"""<div style="background:linear-gradient(135deg,#12171f,#1a1f2e);border:1px solid rgba(255,136,0,.22);border-radius:14px;padding:20px 22px;margin:0 0 20px;">
  <div style="color:#ffaa44;font-weight:700;font-size:1.05em;margin-bottom:2px">
    📊 Artçı Sismik İstatistikler
  </div>
  <div style="color:#94a3b8;font-size:.82em;margin-bottom:14px">
    Omori-Utsu: p={p_fit}{' '+p_err_str if p_err_str else ''}  K={K_fit}  c={c_fit}h  R²={r2}
    &nbsp;|&nbsp;
    Gutenberg-Richter: b={b_val}  a={a_val}  Mc={M_C}
  </div>
  <!-- Tab butonlari -->
  <div style="display:flex;gap:4px;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,.1);">
    <button class="omori-tab-btn" data-tab="omori-pane-log"
      style="background:rgba(59,158,255,.12);color:#7ecbff;border:none;border-bottom:2px solid #3b9eff;
             padding:6px 16px;border-radius:6px 6px 0 0;cursor:pointer;font-size:.88em;font-weight:700;">
      Omori-Utsu  (log–log)
    </button>
    <button class="omori-tab-btn" data-tab="omori-pane-gr"
      style="background:transparent;color:#7a9ab5;border:none;border-bottom:2px solid transparent;
             padding:6px 16px;border-radius:6px 6px 0 0;cursor:pointer;font-size:.88em;">
      Gutenberg-Richter  (log N – M)
    </button>
    <button class="omori-tab-btn" data-tab="omori-pane-dc"
      style="background:transparent;color:#7a9ab5;border:none;border-bottom:2px solid transparent;
             padding:6px 16px;border-radius:6px 6px 0 0;cursor:pointer;font-size:.88em;">
      Fraktal Boyut  (Dc)
    </button>
  </div>
  <!-- Pane: Omori log-log -->
  <div id="omori-pane-log" class="omori-tab-pane" style="height:300px;position:relative;display:block;">
    <canvas id="omori-chart-log"></canvas>
  </div>
  <!-- Pane: G-R -->
  <div id="omori-pane-gr" class="omori-tab-pane" style="height:300px;position:relative;display:none;">
    <canvas id="omori-chart-gr"></canvas>
  </div>
  <!-- Pane: Dc + Dt yan yana -->
  <div id="omori-pane-dc" class="omori-tab-pane" style="display:none;">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;height:300px;">
      <div style="position:relative;">
        <div style="font-size:.78em;color:#b464ff;font-weight:700;margin-bottom:4px">
          Uzaysal Fraktal — C(r) log–log &nbsp; <b style="color:#ff44aa">Dc={Dc}</b>
        </div>
        <div style="position:relative;height:270px;">
          <canvas id="omori-chart-dc"></canvas>
        </div>
      </div>
      <div style="position:relative;">
        <div style="font-size:.78em;color:#ffaa22;font-weight:700;margin-bottom:4px">
          Zamansal Kümelenme — Inter-event Δt &nbsp; <b style="color:#44ddff">Dt={Dt}</b>
        </div>
        <div style="position:relative;height:270px;">
          <canvas id="omori-chart-dt"></canvas>
        </div>
      </div>
    </div>
  </div>
  <!-- Yorum -->
  <div style="margin-top:12px;font-size:.82em;color:#7a9ab5;line-height:1.8;display:flex;gap:24px;flex-wrap:wrap;">
    <span><b style="color:#e8f0f5">p = {p_fit}</b> → {p_yorum}.</span>
    <span><b style="color:#e8f0f5">b = {b_val}</b> (Mc={M_C}) · Seg-1 b₁={b1_val} · Seg-2 b₂={b2_val} → slope break M{M_BREAK_val} (mb doyumu).</span>
    <span><b style="color:#e8f0f5">Dc = {Dc}</b> → {"güçlü kümeleme — artçılar dar zonda yoğunlaştı" if Dc<1.3 else "orta kümeleme — geniş kırık alanı" if Dc<1.7 else "dağınık artçı dağılımı"}.</span>
    <span><b style="color:#e8f0f5">Dt = {Dt}</b> → {Dt_yorum}.</span>
  </div>
  <div style="font-size:.78em;color:#5a7090;margin-top:4px;line-height:1.6">
    Omori (1894) · Utsu (1957) · Gutenberg &amp; Richter (1944) · Aki MLE (1965) · Grassberger-Procaccia (1983)
  </div>
</div>"""

# ── Post icin tam snippet ──────────────────────────────────────────
top5 = ''
for e in sorted(aftershocks, key=lambda x: x['mag'], reverse=True)[:5]:
    col = '#ff2222' if e['mag']>=6 else '#ff8800' if e['mag']>=5 else '#ffd600' if e['mag']>=4 else '#44aaff'
    top5 += (f'      <tr>\n'
             f'        <td style="color:{col};font-weight:700">M{e["mag"]}</td>\n'
             f'        <td>{e["time"][:16].replace("T"," ")} UTC</td>\n'
             f'        <td>{e["lat"]}°N, {e["lon"]}°E</td>\n'
             f'        <td>{e["depth"]} km</td>\n'
             f'        <td style="font-size:.82em">{e["region"]}</td>\n      </tr>\n')

POST_MAP_HTML = f"""<!-- ── AFTERSHOCK MAP + OMORI ─────────────────────────────────── -->
<div style="background:linear-gradient(135deg,#12171f,#1a1f2e);border:1px solid rgba(59,158,255,.2);border-radius:14px;padding:20px 22px;margin:28px 0 16px;">
  <h3 style="color:#7ecbff;margin:0 0 6px;font-size:1.08em">🗺️ Artçı Sismik Aktivite Haritası</h3>
  <div style="color:#94a3b8;font-size:.84em;margin-bottom:14px">
    7–9 Haziran 2026 · {len(aftershocks)} artçı (M≥3.0) · EMSC-CSEM &nbsp;|&nbsp;
    <span style="color:#ff2222">●</span> M6+({bins["M6+"]})
    <span style="color:#ff8800">●</span> M5+({bins["M5-5.9"]})
    <span style="color:#ffd600">●</span> M4+({bins["M4-4.9"]})
    <span style="color:#44aaff">●</span> M3+({bins["M3-3.9"]})
    &nbsp;|&nbsp; <span style="color:#7ecbff">⛶ tam ekran</span>
  </div>
  <div id="aftershock-map-wrap">
    <div id="aftershock-map" style="height:440px;border-radius:10px;border:1px solid rgba(255,255,255,.1)"></div>
  </div>
  <div style="margin-top:10px;font-size:.83em;color:#7a9ab5">
    ⭐ Ana deprem M{mainshock['mag']} — {mainshock['lat']}°N {mainshock['lon']}°E — {mainshock['depth']} km
    &nbsp;|&nbsp; Daire büyüklüğü magnitude ile orantılı · sağ üst ⛶ → tam ekran
  </div>
</div>

{OMORI_HTML}

<div style="background:rgba(59,158,255,.07);border:1px solid rgba(59,158,255,.2);border-radius:10px;padding:16px 18px;margin:0 0 28px;">
  <div style="color:#7ecbff;font-weight:700;margin-bottom:10px;font-size:.95em">📋 En Büyük 5 Artçı Deprem</div>
  <table style="width:100%;border-collapse:collapse;font-size:.84em">
    <thead><tr style="border-bottom:1px solid rgba(59,158,255,.3)">
      <th style="padding:5px 8px;color:#90caf9;text-align:left">Mag</th>
      <th style="padding:5px 8px;color:#90caf9;text-align:left">Tarih / Saat UTC</th>
      <th style="padding:5px 8px;color:#90caf9;text-align:left">Koordinat</th>
      <th style="padding:5px 8px;color:#90caf9;text-align:left">Derinlik</th>
      <th style="padding:5px 8px;color:#90caf9;text-align:left">Bölge</th>
    </tr></thead>
    <tbody style="color:#ddeeff">
{top5}    </tbody>
  </table>
</div>

<script>
{AFTERSHOCK_MAP_JS}
{OMORI_CHART_JS}
</script>
"""

os.makedirs('OUTPUT', exist_ok=True)
with open('OUTPUT/aftershock_map_snippet.html','w',encoding='utf-8') as f:
    f.write(POST_MAP_HTML)
print(f'\nSnippet: OUTPUT/aftershock_map_snippet.html')
print(f'AFTERSHOCK_MAP_JS: {len(AFTERSHOCK_MAP_JS)} karakter')
print(f'OMORI_CHART_JS   : {len(OMORI_CHART_JS)} karakter')

# ── Hesaplanan parametreleri JSON'a yaz ───────────────────────────
_json_path = os.path.join(os.path.dirname(RAW), os.path.basename(os.path.dirname(RAW)) + '.json')
if os.path.exists(_json_path):
    with open(_json_path, encoding='utf-8') as _f:
        _d = json.load(_f)

    n_total   = len(aftershocks)
    n_m5      = bins['M5-5.9'] + bins['M6+']
    n_m6      = bins['M6+']
    ftls_color = 'KIRMIZI' if b_val < 0.75 else 'SARI' if b_val < 0.90 else 'YEŞİL'
    now_str   = datetime.now(timezone.utc).strftime('%d %B %Y, %H:%M UTC')

    _d['PARAM_P']             = str(p_fit)
    _d['PARAM_P_ERR']         = str(round(p_err, 3)) if p_err else '—'
    _d['PARAM_K']             = str(K_fit)
    _d['PARAM_C']             = str(c_fit)
    _d['PARAM_R2']            = str(r2)
    _d['PARAM_B']             = str(b_val)
    _d['PARAM_MC']            = str(M_C)
    _d['PARAM_DC']            = str(Dc)
    _d['PARAM_DT']            = str(Dt)
    _d['PARAM_N_TOTAL']       = str(n_total)
    _d['PARAM_N_M5']          = str(n_m5)
    _d['PARAM_N_M6']          = str(n_m6)
    _d['PARAM_FTLS']          = ftls_color
    _d['PARAM_UPDATED']       = now_str

    with open(_json_path, 'w', encoding='utf-8') as _f:
        json.dump(_d, _f, ensure_ascii=False, indent=2)
    print(f'Parametreler JSON\'a yazildi: p={p_fit}, b={b_val}, N={n_total}, FTLS={ftls_color}')
else:
    print(f'JSON bulunamadi, parametreler yazilmadi: {_json_path}')
