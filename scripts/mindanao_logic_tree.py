"""
mindanao_logic_tree.py
══════════════════════════════════════════════════════════════════════
Mindanao Mw 7.8 — PSHA Logic Tree (Mantık Ağacı)
══════════════════════════════════════════════════════════════════════
Metodoloji : Baker, Bradley & Stafford (2021) §7.3 — Logic Trees
             McGuire (2004) — PSHA for Engineers §4
GMPE       : Youngs vd. (1988) subdüksiyon arayüzü (sabit)
Belirsizlik dalları (epistemik):
  B1 — b-değeri  : 0.635 / 0.80 / 0.90  (FTLS kriz / geçiş / bölgesel)
  B2 — λ(M≥5)   : 2.0  / 3.0  / 4.5   (düşük / merkez / yüksek aktivite)
  B3 — M_max     : 8.0  / 8.5  / 9.0   (muhafazakâr / merkez / üst sınır)
Toplam : 3 × 3 × 3 = 27 dal kombinasyonu
Çıktı  : Ağırlıklı ortalama tehlike eğrisi + 5/16/50/84/95. yüzdelik dilimler
══════════════════════════════════════════════════════════════════════
"""

import numpy as np
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, sys, itertools
sys.stdout.reconfigure(encoding='utf-8')

# ══════════════════════════════════════════════════════════════════════
# 1. SABİT PARAMETRELER
# ══════════════════════════════════════════════════════════════════════
R_CT  = np.sqrt(46**2 + 35.5**2)   # 58.1 km — santroid
Vs30  = 360.0
Zt    = 0                           # interface (megathrust)
Mmin  = 5.0
dM    = 0.2
x_im  = np.logspace(np.log10(0.005), np.log10(3.0), 200)

# ══════════════════════════════════════════════════════════════════════
# 2. MANTIK AĞACI DALLARI
# ══════════════════════════════════════════════════════════════════════

# B1 — b-değeri  [FTLS kriz | bölgesel | mb-doygunluk sonrası Mw]
# Ağırlıklar: FTLS krizi merkeze alınmış (Baker 2021 §7.3 + Gulia 2024)
B1 = [
    dict(b=0.635, label='b=0.635 (FTLS Kriz)', w=0.60, color='#E53935'),
    dict(b=0.900, label='b=0.900 (Bölgesel)',  w=0.30, color='#3860A0'),
    dict(b=1.120, label='b=1.120 (Mw doyum)',  w=0.10, color='#7B1FA2'),
]

# B2 — GMPE varyasyonu (epistemik: mekanizma + zemin belirsizliği)
# Youngs (1988): Zt=0 interface / +0.5σ epistemic / Zt=1 intraslab
B2 = [
    dict(Zt=0, eps=0.0, label='Interface (Zt=0)',      w=0.70),
    dict(Zt=0, eps=0.5, label='+0.5σ epistemic',       w=0.20),
    dict(Zt=1, eps=0.0, label='Intraslab (Zt=1)',      w=0.10),
]

# B3 — M_max  [gözlenen | FTLS üst | tarihsel limit]
B3 = [
    dict(Mmax=7.8, label='Mmax=7.8 (gözlenen)',   w=0.50),
    dict(Mmax=8.0, label='Mmax=8.0 (FTLS üst)',   w=0.30),
    dict(Mmax=8.2, label='Mmax=8.2 (tarihsel)',   w=0.20),
]

# ══════════════════════════════════════════════════════════════════════
# 3. GMPE + G-R (vektörize)
# ══════════════════════════════════════════════════════════════════════

def youngs88_vec(M_arr, R, Zt=0, Vs30=760.0):
    site  = 0.35 * np.log(760.0 / Vs30) if Vs30 < 760 else 0.0
    ln_mu = (19.16 + 1.045 * M_arr
             - 4.738 * np.log(R + 205.5 * np.exp(0.0968 * M_arr))
             + 0.54  * Zt + site)
    sigma = np.maximum(1.45 - 0.1 * M_arr, 0.35)
    return np.exp(ln_mu), sigma

def hazard_one(b, lam5, Mmax, Zt=0, eps=0.0):
    """
    Tek dal kombinasyonu için tehlike eğrisi (vektörize).
    eps : epistemik GMPE kayması (medyan +eps×σ)
    Zt  : 0=interface, 1=intraslab (Youngs 1988)
    """
    M_bins  = np.arange(Mmin + dM/2, Mmax, dM)
    M_edges = M_bins - dM / 2
    A = 10**(-b * (M_edges - Mmin))
    B_val = 10**(-b * (Mmax - Mmin))
    lam_e = lam5 * (A - B_val) / (1.0 - B_val)
    lam_e = np.where(M_bins <= Mmax, lam_e, 0.0)
    lam_o = np.maximum(-np.diff(np.append(lam_e, 0)), 0.0)

    mu, sig = youngs88_vec(M_bins, R_CT, Zt, Vs30)
    mu_shifted = mu * np.exp(eps * sig)   # epistemik kayma

    ln_x  = np.log(x_im)[np.newaxis, :]
    ln_mu = np.log(mu_shifted)[:, np.newaxis]
    sig2d = sig[:, np.newaxis]

    P_mat = 1.0 - norm.cdf(ln_x, ln_mu, sig2d)
    return lam_o @ P_mat


# ══════════════════════════════════════════════════════════════════════
# 4. 27 DAL HESABI
# ══════════════════════════════════════════════════════════════════════
print("27 dal kombinasyonu hesaplanıyor...", flush=True)

branch_curves  = []   # her dal için λ(x) dizisi
branch_weights = []   # birleşik ağırlık

for b1, b2, b3 in itertools.product(B1, B2, B3):
    w = b1['w'] * b2['w'] * b3['w']
    lx = hazard_one(b1['b'], 3.0, b3['Mmax'], Zt=b2['Zt'], eps=b2['eps'])
    branch_curves.append(lx)
    branch_weights.append(w)

branch_curves  = np.array(branch_curves)    # (27, nIM)
branch_weights = np.array(branch_weights)   # (27,)

assert abs(branch_weights.sum() - 1.0) < 1e-9, "Ağırlıklar toplamı ≠ 1"
print(f"  Toplam ağırlık: {branch_weights.sum():.6f} ✓", flush=True)

# ── Ağırlıklı ortalama tehlike eğrisi ──────────────────────────────
lam_mean = branch_weights @ branch_curves   # (nIM,)

# ── Fraktiller (percentile) ─────────────────────────────────────────
# Her IM değeri için ağırlıklı kümülatif dağılım → yüzdelik dilim
fractiles = [0.05, 0.16, 0.50, 0.84, 0.95]
frac_labels = ['5.', '16.', '50. (medyan)', '84.', '95.']
frac_curves = []

for frac in fractiles:
    fc = np.zeros(len(x_im))
    for j in range(len(x_im)):
        lx_j = branch_curves[:, j]
        # sırala, kümülatif ağırlık hesapla
        idx_sort = np.argsort(lx_j)
        lx_sort  = lx_j[idx_sort]
        w_sort   = branch_weights[idx_sort]
        cdf_w    = np.cumsum(w_sort)
        # interpolasyon
        fc[j] = np.interp(frac, cdf_w, lx_sort)
    frac_curves.append(fc)

frac_curves = np.array(frac_curves)   # (5, nIM)
print("Fraktiller hesaplandı.", flush=True)


# ══════════════════════════════════════════════════════════════════════
# 5. B1 PARAMETRESI KATKISI (b-değeri etkisi görsel)
# ══════════════════════════════════════════════════════════════════════
# b-değerinin tek başına etkisi: diğer parametreler sabit (merkez değerleri)
lam_b_fixed = {}
for b1 in B1:
    lx = hazard_one(b1['b'], 3.0, 8.0)   # λ=3.0, Mmax=8.0 (merkez) sabit
    lam_b_fixed[b1['label']] = (lx, b1['color'])


# ══════════════════════════════════════════════════════════════════════
# 6. TABLO
# ══════════════════════════════════════════════════════════════════════

def loglog_interp(lam_t, lam_c, xc):
    v = lam_c > 1e-12
    if not v.any() or lam_t < lam_c[v][-1] or lam_t > lam_c[v][0]:
        return np.nan
    return np.exp(np.interp(np.log(lam_t),
                            np.log(lam_c[v][::-1]),
                            np.log(xc[v][::-1])))

print("\n" + "═"*70)
print("  Mindanao Logic Tree  |  27 Dal  |  Ağırlıklı PGA Tahminleri")
print("  (General Santos City, R_sant=58.1 km, Vs30=360 m/s)")
print("═"*70)
print(f"  {'Senaryo':<12} {'λ (1/yr)':<13} {'5.':<9} {'16.':<9} {'50.':<9} {'84.':<9} {'95.':}")
print("  " + "-"*62)
for prob, lbl in [(0.50,'%50/50yr'),(0.10,'%10/50yr'),(0.02,'%2/50yr')]:
    lt = -np.log(1-prob)/50
    vals = [loglog_interp(lt, frac_curves[k], x_im) for k in range(5)]
    vm   = loglog_interp(lt, lam_mean, x_im)
    print(f"  {lbl:<12} {lt:<13.5f}", end='')
    for v in vals:
        print(f" {v:<9.3f}" if not np.isnan(v) else f" {'---':<9}", end='')
    print(f"  [ort={vm:.3f}]")
print("═"*70)

# b-değeri etkisi
print(f"\n  b-Değeri Etkisi  (%10/50yr, diğer parametreler merkez):")
lt10 = -np.log(0.90)/50
for b1 in B1:
    lx, _ = lam_b_fixed[b1['label']]
    pga = loglog_interp(lt10, lx, x_im)
    print(f"    {b1['label']:<35} PGA = {pga:.3f} g")
print("═"*70)


# ══════════════════════════════════════════════════════════════════════
# 7. GRAFİKLER
# ══════════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(16, 11))
fig.patch.set_facecolor('white')
gs = fig.add_gridspec(2, 3, hspace=0.45, wspace=0.36)

FRAC_COLORS = ['#B0BEC5','#78909C','#263238','#78909C','#B0BEC5']
FRAC_LW     = [1.0, 1.4, 2.5, 1.4, 1.0]
FRAC_LS     = ['--','--','-','--','--']

# ── (a) Logic Tree tehlike eğrisi — fraktiller ───────────────────────
ax1 = fig.add_subplot(gs[0, :2])

# tüm 27 dal (ince, saydam)
for k in range(len(branch_curves)):
    ax1.loglog(x_im, branch_curves[k], '-',
               color='#B0BEC5', lw=0.4, alpha=0.35, zorder=1)

# fraktil bantları
ax1.fill_between(x_im, frac_curves[1], frac_curves[3],
                 alpha=0.25, color='#3860A0', label='16.–84. yüzdelik')
ax1.fill_between(x_im, frac_curves[0], frac_curves[4],
                 alpha=0.12, color='#3860A0', label='5.–95. yüzdelik')

# fraktil çizgileri
for k, (fc, lbl, col, lw, ls) in enumerate(zip(
        frac_curves, frac_labels, FRAC_COLORS, FRAC_LW, FRAC_LS)):
    ax1.loglog(x_im, fc, ls, color=col, lw=lw,
               label=f'{lbl} yüzdelik', zorder=3)

# ağırlıklı ortalama
ax1.loglog(x_im, lam_mean, '-', color='#E53935', lw=2.8,
           label='Ağırlıklı ortalama', zorder=5)

# referans çizgiler
for prob, ls_ref in [(0.10,'--'),(0.02,':')]:
    lt = -np.log(1-prob)/50
    pga_m = loglog_interp(lt, lam_mean, x_im)
    ax1.axhline(lt, color='gray', ls=ls_ref, lw=0.8, zorder=2)
    if not np.isnan(pga_m):
        ax1.plot(pga_m, lt, 'D', color='#E53935', ms=7, zorder=6)
        label = f'%{int(100*prob)}/50yr\n{pga_m:.2f} g'
        ax1.text(pga_m*1.07, lt*1.35, label, fontsize=8, color='#E53935')

ax1.axvspan(0.20, 0.35, alpha=0.08, color='orange', label='EMS-98 VII–VIII')
ax1.set_xlabel('Tepe Yer İvmesi, PGA [g]', fontsize=10)
ax1.set_ylabel('Yıllık Aşılma Oranı, λ', fontsize=10)
ax1.set_xlim([0.01, 3.0]); ax1.set_ylim([5e-5, 1e1])
ax1.grid(True, which='both', alpha=0.2)
ax1.legend(fontsize=8, loc='lower left', ncol=2)
ax1.set_title(
    '(a) Logic Tree PSHA — 27 Dal, Fraktil Eğrileri\n'
    'Epistemik belirsizlik: b-değeri × λ(M≥5) × M_max  |  '
    'Baker, Bradley & Stafford (2021) §7.3', fontsize=9.5)

# ── (b) Logic Tree şeması ────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
ax2.axis('off')

# Elle çizilmiş mantık ağacı görselleştirmesi
tree_data = [
    # (x_start, x_end, y_branch_list, labels, weights, colors)
    (0.05, 0.35, [0.82, 0.50, 0.18],
     [b['label'].split('(')[0].strip() for b in B1],
     [b['w'] for b in B1],
     [b['color'] for b in B1]),
    (0.38, 0.65, [0.85, 0.50, 0.15],
     ['λ=2.0', 'λ=3.0', 'λ=4.5'],
     [0.25, 0.50, 0.25],
     ['#9E9E9E']*3),
    (0.68, 0.95, [0.85, 0.50, 0.15],
     ['Mmax=8.0', 'Mmax=8.5', 'Mmax=9.0'],
     [0.25, 0.50, 0.25],
     ['#9E9E9E']*3),
]

lv_labels = ['B1\nb-değeri', 'B2\nλ(M≥5)', 'B3\nM_max']
root_y = 0.50

for lv_idx, (x0, x1, ys, lbls, ws, cols) in enumerate(tree_data):
    # Kök noktasından dallara
    ax2.plot([x0, x0], [min(ys), max(ys)], '-', color='#9E9E9E', lw=1.0,
             transform=ax2.transAxes)
    for yi, lbl, w, col in zip(ys, lbls, ws, cols):
        ax2.annotate('', xy=(x1, yi), xytext=(x0, yi),
                     xycoords='axes fraction', textcoords='axes fraction',
                     arrowprops=dict(arrowstyle='->', color=col, lw=1.5))
        ax2.text(x1+0.01, yi, f'{lbl}\n(w={w:.2f})',
                 transform=ax2.transAxes, fontsize=7.5,
                 va='center', color=col)
    ax2.text((x0+x1)/2, 0.97, lv_labels[lv_idx],
             transform=ax2.transAxes, fontsize=8,
             ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.3', fc='#E3F2FD', ec='#3860A0', lw=0.8))

ax2.text(0.50, 0.04, '27 dal × ağırlıklı ortalama\n→ Tehlike Eğrisi + Fraktiller',
         transform=ax2.transAxes, fontsize=8, ha='center',
         bbox=dict(boxstyle='round,pad=0.4', fc='#FFF3E0', ec='#E53935', lw=1.0))
ax2.set_title('(b) Logic Tree Şeması\nEpistemik Belirsizlik Dalları', fontsize=9.5)

# ── (c) b-değeri etkisi (diğerleri sabit) ────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
for b1 in B1:
    lx, col = lam_b_fixed[b1['label']]
    ax3.loglog(x_im, lx, '-', color=col, lw=2.2,
               label=f"{b1['label']} (w={b1['w']})")
ax3.axvspan(0.20, 0.35, alpha=0.09, color='orange')
ax3.axhline(-np.log(0.90)/50, color='gray', ls='--', lw=0.8)
ax3.set_xlabel('PGA [g]', fontsize=9)
ax3.set_ylabel('λ (1/yr)', fontsize=9)
ax3.set_title('(c) b-Değeri Etkisi\n(λ=3.0/yr, Mmax=8.5 sabit)', fontsize=9.5)
ax3.legend(fontsize=8); ax3.grid(True, which='both', alpha=0.2)
ax3.set_xlim([0.01, 3.0]); ax3.set_ylim([5e-5, 1e1])

# ── (d) Belirsizlik katkısı — PGA farkı ─────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
lt10 = -np.log(0.90)/50
pga_5  = loglog_interp(lt10, frac_curves[0], x_im)
pga_16 = loglog_interp(lt10, frac_curves[1], x_im)
pga_50 = loglog_interp(lt10, frac_curves[2], x_im)
pga_84 = loglog_interp(lt10, frac_curves[3], x_im)
pga_95 = loglog_interp(lt10, frac_curves[4], x_im)

bars   = [pga_5, pga_16, pga_50, pga_84, pga_95]
labels = ['5.', '16.', '50.', '84.', '95.']
bcolors= ['#B0BEC5','#78909C','#E53935','#78909C','#B0BEC5']
ax4.barh(labels, bars, color=bcolors, edgecolor='white', height=0.6)
ax4.axvline(loglog_interp(lt10, lam_mean, x_im),
            color='#E53935', lw=2, ls='--', label='Ağırlıklı ort.')
ax4.set_xlabel('PGA [g]  (%10/50yr)', fontsize=9)
ax4.set_title('(d) Epistemik Belirsizlik Dağılımı\nYüzdelik Dilimler @ %10/50yr', fontsize=9.5)
ax4.legend(fontsize=8); ax4.grid(True, axis='x', alpha=0.25)

# ── (e) Dal ağırlığı dağılımı (pasta grafik) ─────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
b1_labels  = [b['label'].split('(')[0].strip() for b in B1]
b1_weights = [b['w'] for b in B1]
b1_colors  = [b['color'] for b in B1]
b2_labels  = ['Interface', '+0.5σ epist.', 'Intraslab']
b2_weights = [0.70, 0.20, 0.10]
b3_labels  = ['Mmax=7.8', 'Mmax=8.0', 'Mmax=8.2']
b3_weights = [0.50, 0.30, 0.20]

# Halka grafik — üç katman
def ring(ax, vals, labels, colors, r_in, r_out, title=''):
    vals = np.array(vals, dtype=float) / sum(vals)
    angles = np.cumsum([0] + list(vals * 2 * np.pi))
    for i, (v, lbl, c) in enumerate(zip(vals, labels, colors)):
        theta = np.linspace(angles[i], angles[i+1], 50)
        x_out = r_out * np.cos(theta)
        y_out = r_out * np.sin(theta)
        x_in  = r_in  * np.cos(theta[::-1])
        y_in  = r_in  * np.sin(theta[::-1])
        ax.fill(np.append(x_out, x_in), np.append(y_out, y_in),
                color=c, edgecolor='white', lw=0.8, alpha=0.85)
        mid_angle = (angles[i] + angles[i+1]) / 2
        rx = (r_in + r_out) / 2 * np.cos(mid_angle)
        ry = (r_in + r_out) / 2 * np.sin(mid_angle)
        if v > 0.12:
            ax.text(rx, ry, f'{v*100:.0f}%', ha='center', va='center',
                    fontsize=7, fontweight='bold', color='white')

ring(ax5, b1_weights, b1_labels, b1_colors, 0.55, 0.85)
ring(ax5, b2_weights, b2_labels, ['#90A4AE','#546E7A','#263238'], 0.30, 0.53)
ring(ax5, b3_weights, b3_labels, ['#FFCC80','#FFA726','#E65100'], 0.05, 0.28)

ax5.set_xlim(-1, 1); ax5.set_ylim(-1, 1); ax5.set_aspect('equal')
ax5.axis('off')
ax5.text(0, 1.02, '(e) Dal Ağırlık Dağılımı\n(dış→B1 b-değer | orta→B2 λ | iç→B3 Mmax)',
         ha='center', va='bottom', fontsize=8.5, transform=ax5.transAxes)

# Efsane
patches = []
for b1 in B1:
    patches.append(mpatches.Patch(color=b1['color'],
                                  label=b1['label'].split('(')[0].strip()))
ax5.legend(handles=patches, fontsize=7.5, loc='lower center',
           bbox_to_anchor=(0.5, -0.12), ncol=1)

fig.suptitle(
    'Mindanao Mw 7.8 (2026) — Logic Tree PSHA  |  27 Dal, Epistemik Belirsizlik\n'
    'Baker, Bradley & Stafford (2021) §7.3  |  McGuire (2004) §4  |  '
    'GMPE: Youngs vd. (1988)',
    fontsize=10.5, y=1.005
)

os.makedirs('OUTPUT/PSHA', exist_ok=True)
out = 'OUTPUT/PSHA/Mindanao_LogicTree.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
print(f'\nGrafik: {out}')
