"""
mindanao_psha.py  —  v3  (vektörize, hızlı)
══════════════════════════════════════════════════════════════════════
Mindanao Mw 7.8 (7 Haziran 2026) — Olasılıksal Sismik Tehlike Analizi
Metodoloji : Baker, Bradley & Stafford (2021) §6
GMPE       : Youngs vd. (1988) subdüksiyon arayüzü
Tüm iç içe döngüler → NumPy broadcasting (M×IM matrisi)
══════════════════════════════════════════════════════════════════════
"""

import numpy as np
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')          # ekransız render (hız)
import matplotlib.pyplot as plt
import os, sys
sys.stdout.reconfigure(encoding='utf-8')

# ══════════════════════════════════════════════════════════════════════
# 1. PARAMETRELER
# ══════════════════════════════════════════════════════════════════════
R_CT   = np.sqrt(46**2 + 35.5**2)   # 58.1 km — santroid bazlı
R_HC   = np.sqrt(46**2 + 55.2**2)   # 71.9 km — hipocenter bazlı
Vs30   = 360.0                        # m/s

x_im   = np.logspace(np.log10(0.005), np.log10(3.0), 200)   # PGA [g]

dM     = 0.2
M_bins = np.arange(5.1, 8.5, dM)    # 17 bin

# ── Kaynaklar ──────────────────────────────────────────────────────
SOURCES = [
    dict(name='Cotabato Megathrust', R=R_CT, h=35.5, b=0.90,
         lam5=3.0, Mmin=5.0, Mmax=8.5, Zt=0, color='#3860A0'),
    dict(name='Davao Fay Zonu',      R=np.sqrt(120**2+25**2),
         h=25.0, b=0.90, lam5=1.0, Mmin=5.0, Mmax=7.5, Zt=0, color='#CF5921'),
]
SRC_FTLS = dict(name='FTLS b=0.635', R=R_CT, h=35.5,
                b=0.635,
                lam5=500 * 10**(-0.635*(5-3.5)) * (365/90),
                Mmin=5.0, Mmax=7.8, Zt=0, color='#E53935')


# ══════════════════════════════════════════════════════════════════════
# 2. GMPE — Youngs vd. (1988), vektörize
# ══════════════════════════════════════════════════════════════════════

def youngs88_vec(M_arr, R, Zt=0, Vs30=760.0):
    """
    M_arr : 1-D array  (büyüklükler)
    Dönüş : mu_arr [g], sigma_arr (her M için ayrı)
    """
    site  = 0.35 * np.log(760.0 / Vs30) if Vs30 < 760 else 0.0
    ln_mu = (19.16 + 1.045 * M_arr
             - 4.738 * np.log(R + 205.5 * np.exp(0.0968 * M_arr))
             + 0.54  * Zt + site)
    sigma = np.maximum(1.45 - 0.1 * M_arr, 0.35)
    return np.exp(ln_mu), sigma     # shape: (nM,)


# ══════════════════════════════════════════════════════════════════════
# 3. G-R KESİK DAĞILIM
# ══════════════════════════════════════════════════════════════════════

def gr_occur(src):
    """Oluşma oranı dizisi — shape (nM,)"""
    M_edges = M_bins - dM/2
    A = 10**(-src['b'] * (M_edges  - src['Mmin']))
    B = 10**(-src['b'] * (src['Mmax'] - src['Mmin']))
    lam_e = src['lam5'] * (A - B) / (1.0 - B)
    lam_e = np.where(M_bins <= src['Mmax'], lam_e, 0.0)
    lam_o = np.diff(np.append(lam_e, 0)) * -1
    return np.maximum(lam_o, 0.0)


# ══════════════════════════════════════════════════════════════════════
# 4. PSHA — broadcasting (nM × nIM)
# ══════════════════════════════════════════════════════════════════════

def hazard_curve(src, n_sigma=0):
    """
    n_sigma = 0 → medyan GMPE
    n_sigma > 0 → +n·σ bias (epistemic üst bant)
    """
    lam_o       = gr_occur(src)              # (nM,)
    mu, sigma   = youngs88_vec(M_bins, src['R'], src['Zt'], Vs30)
    mu_shifted  = mu * np.exp(n_sigma * sigma)

    # Broadcasting: (nM,1) vs (1,nIM)
    ln_x   = np.log(x_im)[np.newaxis, :]    # (1, nIM)
    ln_mu  = np.log(mu_shifted)[:, np.newaxis]  # (nM, 1)
    sig2d  = sigma[:, np.newaxis]           # (nM, 1)

    P_mat  = 1.0 - norm.cdf(ln_x, ln_mu, sig2d)   # (nM, nIM)
    return lam_o @ P_mat                            # (nIM,)


def disagg_M(src, lam_target, lam_curve):
    """Büyüklük disaggregasyonu, hedef λ noktasında."""
    j     = np.argmin(np.abs(lam_curve - lam_target))
    xj    = x_im[j]
    lam_o = gr_occur(src)
    mu, sig = youngs88_vec(M_bins, src['R'], src['Zt'], Vs30)
    p_M   = 1.0 - norm.cdf(np.log(xj), np.log(mu), sig)
    w     = lam_o * p_M
    denom = max(w.sum(), 1e-30)
    return w / denom, float((M_bins * w).sum() / denom), xj


# ── Hesapla ─────────────────────────────────────────────────────────
print("Hesaplanıyor...", flush=True)

c1_med  = hazard_curve(SOURCES[0], n_sigma=0)
c1_1sig = hazard_curve(SOURCES[0], n_sigma=1)
c1_2sig = hazard_curve(SOURCES[0], n_sigma=2)
c2_med  = hazard_curve(SOURCES[1], n_sigma=0)
c_ftls  = hazard_curve(SRC_FTLS,   n_sigma=0)
c_comb  = c1_med + c2_med

lam_10  = -np.log(0.90) / 50
lam_02  = -np.log(0.98) / 50

d10, Mbar10, pga10 = disagg_M(SOURCES[0], lam_10, c1_med)
d02, Mbar02, pga02 = disagg_M(SOURCES[0], lam_02, c1_med)
print("Tamamlandı.", flush=True)


# ══════════════════════════════════════════════════════════════════════
# 5. TABLO
# ══════════════════════════════════════════════════════════════════════

def loglog_interp(lam_t, lam_c, xc):
    v = lam_c > 1e-12
    if lam_t < lam_c[v][-1] or lam_t > lam_c[v][0]:
        return np.nan
    return np.exp(np.interp(np.log(lam_t),
                            np.log(lam_c[v][::-1]),
                            np.log(xc[v][::-1])))

print("\n" + "═"*60)
print("  Mindanao PSHA  |  General Santos City  |  Youngs (1988)")
print("═"*60)
for prob, lbl in [(0.50,'%50/50yr'),(0.10,'%10/50yr'),(0.02,'%2/50yr')]:
    lt  = -np.log(1-prob)/50
    p0  = loglog_interp(lt, c1_med,  x_im)
    p1  = loglog_interp(lt, c1_1sig, x_im)
    p2  = loglog_interp(lt, c1_2sig, x_im)
    print(f"  {lbl:<10}  med={p0:.3f} g   +1σ={p1:.3f} g   +2σ={p2:.3f} g")
print(f"\n  Disaggregasyon (Cotabato):")
print(f"    %10/50yr → PGA≈{pga10:.3f} g  M̄={Mbar10:.2f}")
print(f"    %2/50yr  → PGA≈{pga02:.3f} g  M̄={Mbar02:.2f}")
print("═"*60)


# ══════════════════════════════════════════════════════════════════════
# 6. GRAFİKLER
# ══════════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('white')
gs  = fig.add_gridspec(2, 3, hspace=0.44, wspace=0.36)

C = dict(s1='#3860A0', s2='#CF5921', ftls='#E53935',
         comb='#388E3C', b1='#90CAF9', b2='#BBDEFB', gr='#888888')

# ── (a) Tehlike eğrisi ───────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
ax1.fill_between(x_im, c1_2sig, 1e-6, alpha=0.12, color=C['b2'])
ax1.fill_between(x_im, c1_1sig, 1e-6, alpha=0.22, color=C['b1'])
ax1.loglog(x_im, c1_2sig, '--', color=C['s1'], lw=1.0, alpha=0.55, label='Cotabato +2σ')
ax1.loglog(x_im, c1_1sig, '--', color=C['s1'], lw=1.4,              label='Cotabato +1σ')
ax1.loglog(x_im, c1_med,  '-',  color=C['s1'], lw=2.5,              label='Cotabato medyan')
ax1.loglog(x_im, c2_med,  '-',  color=C['s2'], lw=1.8, alpha=0.85,  label='Davao Fay Zonu')
ax1.loglog(x_im, c_comb,  '-',  color=C['comb'], lw=2.0,            label='Toplam (iki kaynak)')
ax1.loglog(x_im, c_ftls,  ':',  color=C['ftls'], lw=2.2,            label='FTLS b=0.635 (90 gün)')

for prob, ls in [(0.10,'--'),(0.02,':')]:
    lt  = -np.log(1-prob)/50
    pga = loglog_interp(lt, c1_med, x_im)
    ax1.axhline(lt, color=C['gr'], linestyle=ls, lw=0.8)
    if not np.isnan(pga):
        ax1.plot(pga, lt, 'o', color=C['s1'], ms=7, zorder=5)
        ax1.text(pga*1.07, lt*1.35,
                 f'%{int((1-(1-prob)**1)*100)}/50yr\n{pga:.2f} g',
                 fontsize=7.5, color=C['s1'])

ax1.axvspan(0.20, 0.35, alpha=0.09, color='orange', label='EMS-98 VII–VIII')
ax1.set_xlabel('Tepe Yer İvmesi, PGA [g]', fontsize=10)
ax1.set_ylabel('Yıllık Aşılma Oranı, λ', fontsize=10)
ax1.set_xlim([0.01, 3.0]); ax1.set_ylim([5e-5, 1e1])
ax1.grid(True, which='both', alpha=0.2)
ax1.legend(fontsize=8, loc='lower left', ncol=2)
ax1.set_title('(a) PGA Sismik Tehlike Eğrisi — Youngs vd. (1988)  |  '
              'Baker, Bradley & Stafford (2021) §6\n'
              f'General Santos City | Vs30={Vs30} m/s | '
              f'R_santroid={R_CT:.1f} km | R_hipo={R_HC:.1f} km', fontsize=9.5)

# ── (b) G-R karşılaştırması ──────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
Mr = np.linspace(5.0, 8.5, 300)
for src, ls in [(SOURCES[0],'-'),(SRC_FTLS,'--')]:
    A = 10**(-src['b']*(Mr-src['Mmin']))
    B = 10**(-src['b']*(src['Mmax']-src['Mmin']))
    lr = src['lam5'] * (A-B)/(1-B)
    lr = np.where(Mr <= src['Mmax'], lr, np.nan)
    ax2.semilogy(Mr, lr, ls, color=src['color'], lw=2, label=f"b={src['b']}")
ax2.axvline(7.8, color='k', lw=1.2, ls=':', label='Mw 7.8')
ax2.set_xlabel('M', fontsize=9); ax2.set_ylabel('λ(M≥m) [/yıl]', fontsize=9)
ax2.set_title('(b) G-R: b=0.90 vs b=0.635\n(FTLS Kırmızı etkisi)', fontsize=9.5)
ax2.legend(fontsize=8); ax2.grid(True, which='both', alpha=0.2)
ax2.set_xlim([5, 8.6])

# ── (c) Disagg %10/50yr ──────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
ax3.bar(M_bins, d10, width=dM*0.85, color=C['b1'], edgecolor='white', lw=0.5)
ax3.axvline(Mbar10, color=C['s1'], lw=2, ls='--', label=f'M̄={Mbar10:.2f}')
ax3.axvline(7.8, color=C['ftls'], lw=1.5, ls=':', label='Mw 7.8')
ax3.set_xlabel('Büyüklük, M', fontsize=9)
ax3.set_ylabel('P(m | PGA > x)', fontsize=9)
ax3.set_title(f'(c) Disagg — %10/50yr\nPGA≈{pga10:.2f} g', fontsize=9.5)
ax3.legend(fontsize=8); ax3.set_xlim([4.8,8.8]); ax3.grid(True,axis='y',alpha=0.25)

# ── (d) Disagg %2/50yr ───────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
ax4.bar(M_bins, d02, width=dM*0.85, color='#FFCC80', edgecolor='white', lw=0.5)
ax4.axvline(Mbar02, color=C['s2'], lw=2, ls='--', label=f'M̄={Mbar02:.2f}')
ax4.axvline(7.8, color=C['ftls'], lw=1.5, ls=':', label='Mw 7.8')
ax4.set_xlabel('Büyüklük, M', fontsize=9)
ax4.set_ylabel('P(m | PGA > x)', fontsize=9)
ax4.set_title(f'(d) Disagg — %2/50yr\nPGA≈{pga02:.2f} g', fontsize=9.5)
ax4.legend(fontsize=8); ax4.set_xlim([4.8,8.8]); ax4.grid(True,axis='y',alpha=0.25)

# ── (e) GMPE mesafe eğrisi ────────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
R_r = np.logspace(np.log10(20), np.log10(500), 200)
for M_ref, col in [(6.0,'#90CAF9'),(7.0,'#3860A0'),(7.8,'#E53935'),(8.5,'#6D4C41')]:
    mu_r, sig_r = youngs88_vec(np.full_like(R_r, M_ref), R_r, Zt=0, Vs30=Vs30)
    ax5.fill_between(R_r, mu_r*np.exp(-sig_r), mu_r*np.exp(sig_r),
                     alpha=0.12, color=col)
    ax5.loglog(R_r, mu_r, '-', color=col, lw=1.8, label=f'M{M_ref}')

ax5.axvline(R_CT, color=C['gr'], lw=1,   ls='--', label=f'R_sant={R_CT:.0f}km')
ax5.axvline(R_HC, color=C['gr'], lw=1,   ls=':',  label=f'R_hipo={R_HC:.0f}km')
ax5.axhspan(0.20, 0.35, alpha=0.10, color='orange')
ax5.set_xlabel('Hiposantral Mesafe [km]', fontsize=9)
ax5.set_ylabel('PGA [g]', fontsize=9)
ax5.set_title('(e) GMPE Medyan ± 1σ\nYoungs (1988), Vs30=360 m/s', fontsize=9.5)
ax5.legend(fontsize=7.5, ncol=2)
ax5.set_xlim([20,500]); ax5.grid(True,which='both',alpha=0.2)

fig.suptitle(
    'Mindanao Mw 7.8 (7 Haziran 2026) — Çift Kaynaklı PSHA  |  '
    'Baker, Bradley & Stafford (2021) §6  |  GMPE: Youngs vd. (1988)',
    fontsize=11, y=1.005
)

os.makedirs('OUTPUT/PSHA', exist_ok=True)
out = 'OUTPUT/PSHA/Mindanao_PSHA_v3.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
print(f'Grafik: {out}')
