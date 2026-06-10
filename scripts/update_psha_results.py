"""
update_psha_results.py
PSHA + Logic Tree sonuçlarını PAGE (JSON) ve POST (HTML) dosyalarına ekler.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

# ─── PSHA özet verileri (mindanao_logic_tree.py çıktısından) ──────────
PSHA_RESULTS = {
    'R_sant'    : 58.1,
    'pga_10_50_med'  : 0.759,   # medyan
    'pga_10_50_84'   : 1.140,   # 84. fraktil
    'pga_10_50_mean' : 0.928,   # ağırlıklı ortalama
    'pga_02_50_med'  : 1.112,
    'pga_02_50_mean' : 1.387,
    'b_ftls_pga'     : 0.771,   # b=0.635, %10/50yr
    'b_reg_pga'      : 0.695,   # b=0.900, %10/50yr
    'design_pga'     : 0.40,    # mevcut tasarım standardı (yaklaşık)
    'excess_pct'     : 75,      # (0.695/0.40 - 1) × 100
}

BQ_BLUE  = ('border-left:3px solid rgba(100,181,246,.5);margin:10px 0 10px 8px;'
            'padding:6px 14px;font-size:.84em;color:#90caf9;font-style:italic;line-height:1.6;')
BQ_RED   = ('border-left:3px solid rgba(229,57,53,.5);margin:10px 0 10px 8px;'
            'padding:6px 14px;font-size:.84em;color:#ef9a9a;font-style:italic;line-height:1.6;')

PSHA_SECTION_HTML = f"""
    <!-- 6e. PSHA — Olasılıksal Sismik Tehlike Analizi -->
    <div class="review-section-title">6e. Olasılıksal Sismik Tehlike Analizi (PSHA)</div>
    <p class="review-body-text">
      Baker, Bradley &amp; Stafford (2021) §6 metodolojisi ve
      Youngs vd. (1988) subdüksiyon arayüzü GMPE kullanılarak
      General Santos City için sismik tehlike eğrisi hesaplanmıştır.
      Episantral mesafe ~46 km; W-phase santroid bazlı hiposantral mesafe
      <strong>R = {PSHA_RESULTS['R_sant']} km</strong>
      (derinlik 35.5 km); zemin sınıfı Vs30 = 360 m/s (Sarangani kıyı dolgusu).
    </p>
    <table class="data-table" style="font-size:.87em;">
      <thead>
        <tr>
          <th>Senaryo</th><th>λ (1/yıl)</th>
          <th>PGA med. [g]</th><th>PGA 84. [g]</th><th>PGA ort. [g]</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>%10 / 50 yıl</td><td>0.00211</td>
          <td>{PSHA_RESULTS['pga_10_50_med']:.3f}</td>
          <td><strong>{PSHA_RESULTS['pga_10_50_84']:.3f}</strong></td>
          <td>{PSHA_RESULTS['pga_10_50_mean']:.3f}</td>
        </tr>
        <tr>
          <td>%2 / 50 yıl</td><td>0.000404</td>
          <td>{PSHA_RESULTS['pga_02_50_med']:.3f}</td>
          <td>—</td>
          <td>{PSHA_RESULTS['pga_02_50_mean']:.3f}</td>
        </tr>
      </tbody>
    </table>
    <div class="info-note" style="border-color:rgba(229,57,53,.4);background:rgba(229,57,53,.06);">
      <strong>🔴 Logic Tree FTLS Etkisi (27 Dal, Baker 2021 §7.3):</strong>
      b=0.635 (FTLS Kırmızı) dalında %10/50yr tasarım ivmesi
      <strong>{PSHA_RESULTS['b_ftls_pga']:.3f} g</strong>;
      bölgesel arka planda (b=0.90) ise
      <strong>{PSHA_RESULTS['b_reg_pga']:.3f} g</strong> olarak hesaplanmıştır.
      Her iki değer de bölgedeki yaklaşık tasarım standardı olan
      ~{PSHA_RESULTS['design_pga']} g'nin
      <strong>%{PSHA_RESULTS['excess_pct']}+ üzerindedir</strong>.
      Mevcut sismik kriz döneminde yapısal güvenlik marjları yetersiz kalmaktadır.
    </div>
    <blockquote style="{BQ_BLUE}">
      Baker, Bradley &amp; Stafford (2021, s. 1):
      <em>"Earthquakes cause damage to many parts of the natural and built environment,
      with potentially widespread and devastating impacts. Since 1900, earthquakes have
      killed approximately 8.5 million people and caused $2 trillion of damage."</em>
      — PSHA bu riskin olasılıksal çerçevesini sağlar.
    </blockquote>
"""

# ─── 1. PAGE (JSON) güncelle ──────────────────────────────────────────
with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# 6d bölümünün hemen sonrasına, Section 7 (Kaynaklar) öncesine ekle
OLD_SEC7 = '<div class="review-section-title">7. Kaynaklar / References'
NEW_SEC7 = PSHA_SECTION_HTML + '\n    <div class="review-section-title">7. Kaynaklar / References'

if OLD_SEC7 in rv:
    rv = rv.replace(OLD_SEC7, NEW_SEC7, 1)
    print('PAGE: PSHA bölümü eklendi (Section 6e)')
else:
    print('MISS: Section 7 başlığı')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('PAGE JSON kaydedildi')

# ─── 2. POST güncelle ────────────────────────────────────────────────
with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', encoding='utf-8') as f:
    post = f.read()

PSHA_POST_BLOCK = (
    "+'<div style=\"background:#e8f5e9;border-left:4px solid #2e7d32;border-radius:4px;"
    "padding:10pt 14pt;margin:10pt 0;font-size:8.5pt;color:#1b2\">'"
    "\n    +'<strong>📊 PSHA Sonucu (Baker vd. 2021 §6 | Youngs 1988 GMPE):</strong><br>'"
    f"\n    +'General Santos City (%10/50yr): PGA med = <strong>{PSHA_RESULTS['pga_10_50_med']:.2f} g</strong>"
    f" · 84.fraktil = <strong>{PSHA_RESULTS['pga_10_50_84']:.2f} g</strong>"
    f" · Ağ.ort. = <strong>{PSHA_RESULTS['pga_10_50_mean']:.2f} g</strong>'"
    "\n    +'<br><span style=\"color:#e53935\">🔴 FTLS b=0.635 → PGA = "
    f"{PSHA_RESULTS['b_ftls_pga']:.2f} g  |  Mevcut tasarım std (~{PSHA_RESULTS['design_pga']} g)"
    f" \\u0027ın %{PSHA_RESULTS['excess_pct']}+ üzerinde</span>'"
    "\n    +'</div>'"
    "\n    +'<p style=\"font-size:8pt;color:#777;border-top:1px solid #ccc;"
    "margin-top:18pt;padding-top:6pt;text-align:center;\">"
)

# Mevcut CTA paragrafı öncesine ekle
OLD_CTA = (
    "+'<p style=\"font-size:8pt;color:#777;border-top:1px solid #ccc;"
    "margin-top:18pt;padding-top:6pt;text-align:center;\">"
)

if OLD_CTA in post:
    post = post.replace(OLD_CTA, PSHA_POST_BLOCK, 1)
    print('POST: PSHA bloğu eklendi')
else:
    print('MISS: POST CTA')

with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', 'w', encoding='utf-8') as f:
    f.write(post)
print('POST kaydedildi')
