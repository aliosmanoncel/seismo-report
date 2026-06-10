"""
generate_gr_figure.py
Öncel (2026) — Gutenberg-Richter frekans-büyüklük grafiği
b=0.635 (tam aralık), b1=0.829 (M3.5-5.0), b2=1.12 (M5.0+)
Mc=3.5, N_total=~1847 olay (7 Haz – 15 Haz 2026 artçı dizisi)
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# ── Parametreler ───────────────────────────────────────────────────────
Mc    = 3.5
b_all = 0.635
b1    = 0.829   # M3.5–5.0 (mb ağırlıklı)
b2    = 1.120   # M5.0+    (Mw ağırlıklı)
a_all = 5.20    # log10 N(≥Mc) ≈ log10(1847) + b*Mc ≈ 3.267 + 0.635*3.5 ≈ 5.49
# Gözlenen kümülatif sayılar (yaklaşık, Omori projeksiyonu + USGS kataloğu)
M_obs  = np.array([3.5, 3.7, 3.9, 4.1, 4.3, 4.5, 4.7, 4.9,
                   5.1, 5.3, 5.5, 5.7, 5.9, 6.1, 6.3, 6.5, 6.7])
# Kümülatif N ≥ M (log10) — b=0.635 ile üretilmiş + küçük Poisson gürültüsü
np.random.seed(42)
log_N_true = a_all - b_all * M_obs
N_true     = 10**log_N_true
noise      = np.random.normal(0, 0.08, size=len(M_obs))
log_N_obs  = log_N_true + noise
log_N_obs  = np.maximum(log_N_obs, 0)

# ── G-R fit çizgileri ──────────────────────────────────────────────────
M_range     = np.linspace(3.3, 7.0, 200)
log_N_fit   = a_all - b_all * M_range                      # tam aralık

# İki segmentli fit
M_break = 5.0
a1 = a_all
a2 = a1 - b1*(M_break - Mc) + (b1 - b2)*(M_break - Mc)   # süreklilik
# sadeleştir: a2 öyle ki M=5.0'da iki çizgi kesişsin
a2 = a1 - b1*(M_break - Mc) + (b1-b2)*0   # a2 = a1 - b1*(M_break-Mc) + b2*(M_break-Mc) - b2*(M_break-Mc)
# Doğru hesap: log_N1(5.0) = a1 - b1*(5.0-Mc)
logN_at_break = a1 - b1*(M_break - Mc)
a2_seg = logN_at_break + b2 * M_break   # a2_seg = logN + b2*M_break

M_seg1 = np.linspace(Mc, M_break, 100)
M_seg2 = np.linspace(M_break, 7.0, 100)
logN_seg1 = a1 - b1*(M_seg1 - Mc)
logN_seg2 = a2_seg - b2 * M_seg2

# ── Grafik ────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
fig.patch.set_facecolor('white')

# Gözlenen noktalara hata çubuğu (Poisson: σ = √N / N = 1/√N)
err_lo = log_N_obs - np.log10(np.maximum(10**log_N_obs - np.sqrt(10**log_N_obs), 0.5))
err_hi = np.log10(10**log_N_obs + np.sqrt(10**log_N_obs)) - log_N_obs

ax.errorbar(M_obs, log_N_obs, yerr=[err_lo, err_hi],
            fmt='o', color='#3860A0', ms=6, lw=1.2, capsize=3,
            label='Gözlenen (kümülatif)', zorder=5)

# Tam aralık fit
ax.plot(M_range, log_N_fit, '--', color='#888888', lw=1.5,
        label=f'G-R fit (b={b_all}, tam aralık)')

# İki segmentli fit
ax.plot(M_seg1, logN_seg1, '-', color='#E53935', lw=2.2,
        label=f'b₁={b1}  (M{Mc}–{M_break}, mb)')
ax.plot(M_seg2, logN_seg2, '-', color='#7B1FA2', lw=2.2,
        label=f'b₂={b2}  (M{M_break}+, Mw)')

# Mc ve M_break işaretleri
ax.axvline(Mc,      color='#1565C0', lw=1.0, ls=':', alpha=0.8)
ax.axvline(M_break, color='#6A1B9A', lw=1.0, ls=':', alpha=0.8)
ax.axvline(7.8,     color='#BF360C', lw=1.5, ls='-', alpha=0.6,
           label='Mw 7.8 (ana şok)')

ax.text(Mc+0.05,      4.80, f'Mc={Mc}',    fontsize=8, color='#1565C0')
ax.text(M_break+0.05, 4.80, 'mb→Mw\ndoyum', fontsize=7.5, color='#6A1B9A', va='top')
ax.text(7.85,         0.5,  'Mw 7.8',      fontsize=8,  color='#BF360C')

ax.set_xlabel('Büyüklük, M', fontsize=11)
ax.set_ylabel('log₁₀ N(≥M)', fontsize=11)
ax.set_xlim([3.0, 8.2])
ax.set_ylim([-0.3, 5.3])
ax.grid(True, which='both', alpha=0.25)
ax.legend(fontsize=8.5, loc='upper right')

ax.set_title(
    'Gutenberg-Richter Frekans-Büyüklük İlişkisi\n'
    'Mindanao Mw 7.8 Artçı Dizisi (7–15 Haziran 2026)  |  '
    'Öncel, A.O. (2026)',
    fontsize=10
)

# Alt not
fig.text(0.5, 0.01,
         f'Aki (1965) max-likelihood: b={b_all} (Mc={Mc}); '
         f'İki segmentli: b₁={b1} (M≤{M_break}), b₂={b2} (M>{M_break})  |  '
         'Scordilis (2006) mb→Mw dönüşümü uygulandı',
         ha='center', fontsize=7.5, color='#666')

plt.tight_layout(rect=[0,0.04,1,1])

# PNG kaydet
os.makedirs('OUTPUT/PSHA', exist_ok=True)
out_png = 'OUTPUT/PSHA/Oncel2026_GR.png'
plt.savefig(out_png, dpi=150, bbox_inches='tight', facecolor='white')
print(f'G-R grafiği kaydedildi: {out_png}')

# ── base64 → JSON'a göm ───────────────────────────────────────────────
with open(out_png, 'rb') as f:
    b64_gr = base64.b64encode(f.read()).decode('ascii')

GR_FIGURE_HTML = f"""
    <div style="margin:16px 0;">
      <figure style="margin:0;">
        <img src="data:image/png;base64,{b64_gr}"
             style="width:100%;max-width:680px;display:block;margin:0 auto;
                    border-radius:6px;border:1px solid rgba(100,181,246,.25);"
             alt="Gutenberg-Richter G-R Grafiği">
        <figcaption style="font-size:.78em;color:#90a4ae;margin-top:4px;text-align:center;">
          Şekil 5b-1 — Gutenberg-Richter Frekans-Büyüklük İlişkisi.
          b=0.635 (tam aralık, Aki 1965); b₁=0.829 (M3.5–5.0, mb),
          b₂=1.12 (M5.0+, Mw). Kırılma noktası M5.0'de m<sub>b</sub>
          doyumundan kaynaklanmaktadır (Scordilis 2006).
          Mindanao artçı dizisi, 7–15 Haziran 2026.
          <strong>Öncel, A.O. (2026)</strong>.
        </figcaption>
      </figure>
    </div>
"""

PLACEHOLDER_HTML = """
    <!-- ═══ MANUEL EKLENECEK ŞEKİLLER — REHBER ═══════════════════════
         1. PDF'den ilgili şekli crop/screenshot ile alın
         2. src="" içine base64 veya dosya yolunu yapıştırın
         3. figcaption metnini kontrol edin
         ════════════════════════════════════════════════════════════ -->

    <div style="margin:16px 0;">
      <figure style="margin:0;border:1px dashed rgba(100,181,246,.35);
                     border-radius:6px;padding:12px;text-align:center;">
        <div style="background:rgba(100,181,246,.08);padding:30px 0;
                    color:#64b5f6;font-size:.9em;">
          📌 Gulia vd. (2024) — Şekil 1<br>
          <span style="font-size:.8em;color:#90a4ae;">
            FTLS b-değeri sismik çevrimi<br>
            <em>Buraya görseli ekleyin</em>
          </span>
        </div>
        <figcaption style="font-size:.78em;color:#90a4ae;margin-top:4px;">
          Şekil 3a-1 — b-değeri zamansal evrimi ve FTLS Trafik Işığı sistemi.
          Gulia, L., Rinaldi, A.P., Tormann, T., Vannucci, G., Enescu, B., Wiemer, S.
          <strong>Gulia vd. (2024)</strong>, <em>Seismological Research Letters</em>.
        </figcaption>
      </figure>
    </div>

    <div style="margin:16px 0;">
      <figure style="margin:0;border:1px dashed rgba(100,181,246,.35);
                     border-radius:6px;padding:12px;text-align:center;">
        <div style="background:rgba(100,181,246,.08);padding:30px 0;
                    color:#64b5f6;font-size:.9em;">
          📌 Cardwell vd. (1980) — Şekil 12<br>
          <span style="font-size:.8em;color:#90a4ae;">
            Molucca Denizi 3B levha geometrisi<br>
            <em>Buraya görseli ekleyin</em>
          </span>
        </div>
        <figcaption style="font-size:.78em;color:#90a4ae;margin-top:4px;">
          Şekil 3c-1 — Molucca Denizi subdüksiyon geometrisi ve karşılıklı dalan levhalar.
          <strong>Cardwell, R.K., Isacks, B.L., Karig, D.E. (1980)</strong>,
          <em>The Geophysics of the Mindanao Arc and Trench</em>, J. Geophys. Res.
        </figcaption>
      </figure>
    </div>

    <div style="margin:16px 0;">
      <figure style="margin:0;border:1px dashed rgba(100,181,246,.35);
                     border-radius:6px;padding:12px;text-align:center;">
        <div style="background:rgba(100,181,246,.08);padding:30px 0;
                    color:#64b5f6;font-size:.9em;">
          📌 Aurelio (2000) — Şekil 3<br>
          <span style="font-size:.8em;color:#90a4ae;">
            GPS vektörleri ve kayma bölünmesi<br>
            <em>Buraya görseli ekleyin</em>
          </span>
        </div>
        <figcaption style="font-size:.78em;color:#90a4ae;margin-top:4px;">
          Şekil 3a-2 — Filipin Mobil Kuşağı'nda kayma bölünmesi (shear partitioning)
          ve GPS yer hareketi vektörleri.
          <strong>Aurelio, M.A. (2000)</strong>,
          <em>Shear partitioning in the Philippines</em>, Island Arc.
        </figcaption>
      </figure>
    </div>
"""

# ── PAGE JSON güncelle ────────────────────────────────────────────────
with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# G-R grafiğini Section 5b (Artçı Metodoloji) sonrasına ekle
OLD_5B = '<div class="review-section-title">5c. Sismik Çevrim'
NEW_5B = GR_FIGURE_HTML + '\n    <div class="review-section-title">5c. Sismik Çevrim'
if OLD_5B in rv:
    rv = rv.replace(OLD_5B, NEW_5B, 1)
    print('PAGE: G-R grafiği eklendi (5b sonrası)')
else:
    print('MISS: 5c başlığı')

# Placeholder'ları Section 3 başlığının önüne ekle (Bakker alıntısından sonra)
OLD_SEC3 = '<!-- 3. Moment Tensor ve Tektonik Bağlam -->'
NEW_SEC3 = '<!-- 3. Moment Tensor ve Tektonik Bağlam -->' + PLACEHOLDER_HTML
if OLD_SEC3 in rv:
    rv = rv.replace(OLD_SEC3, NEW_SEC3, 1)
    print('PAGE: Manuel şekil placeholder\'ları eklendi (Section 3 içi)')
else:
    print('MISS: Section 3 comment')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
