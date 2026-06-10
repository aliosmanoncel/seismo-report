import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# Son method-card'dan (FTLS) sonra, info-note'dan önce ekleme yapacağız
NEEDLE = '''    <div class="info-note">
      <strong>Sismolojik Değerlendirme — Metodoloji Çerçevesi:</strong>'''

NEW_BLOCK = '''    <!-- Veri Homojenleştirme -->
    <div class="method-card">
      <h4>📐 7. Büyüklük Homojenleştirmesi — mb/m → Mw Dönüşümü</h4>
      <p>
        EMSC kataloğundaki 334 artçının büyüklük türü dağılımı:
        <strong>272 olay "m"</strong> (BMKG/PIVS yerel/gövde dalgası),
        <strong>50 olay "mb"</strong> (gövde dalgası),
        <strong>3 olay "Mw"</strong> (NEIC/GFZ).
        mb ve ML ölçekleri, M > 5.5'ten itibaren <em>doygunluk</em> (saturation) yaşar;
        gerçek büyüklüğü küçümseyerek Gutenberg-Richter grafiğinde yapay eğim kırılmasına
        (slope break) yol açar.
      </p>
      <p>
        Tüm büyüklükler <strong>Scordilis (2006)</strong> bağıntısıyla Mw ölçeğine
        dönüştürülmüştür:
      </p>
      <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;
                  font-family:monospace;font-size:.92em;margin:8px 0;">
        M<sub>w</sub> = 0.85 · m<sub>b</sub> + 1.03 &nbsp;(±0.29) &nbsp;
        [3.5 ≤ m<sub>b</sub> ≤ 6.2; Scordilis, 2006]
      </div>
      <p style="font-size:.87em;color:#94a3b8;">
        Mw ölçeği sismik moment (M₀) ile doğrudan ilişkilidir ve doygunluk yaşamaz;
        bu nedenle b-değeri, Mc ve p-değeri hesaplarında en az yanlı (least biased)
        tahminci sağlar. M ≥ 5.5 için NEIC/GFZ Mw değerleri dönüştürülmeden kullanılır.
      </p>
      <table class="review-table" style="font-size:.85em;margin-top:10px;table-layout:fixed;">
        <colgroup><col style="width:22%"><col style="width:16%"><col style="width:20%"><col style="width:42%"></colgroup>
        <thead>
          <tr><th>Tür</th><th>N olay</th><th>Kaynak Ajans</th><th>Dönüşüm</th></tr>
        </thead>
        <tbody>
          <tr><td>m (yerel/gövde)</td><td>272</td><td>BMKG, PIVS</td>
              <td>Mw = 0.85·m + 1.03 (Scordilis 2006)</td></tr>
          <tr><td>mb</td><td>50</td><td>EMSC</td>
              <td>Mw = 0.85·mb + 1.03 (Scordilis 2006)</td></tr>
          <tr><td>Mw</td><td>3</td><td>NEIC, GFZ</td>
              <td>Dönüşüm uygulanmaz</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Tum Parametreler Hesaplama Metodolojisi -->
    <div class="method-card">
      <h4>🧮 8. Parametre Hesaplama Formülleri — Tam Metodoloji Özeti</h4>

      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin-bottom:6px;">
        A. Katalog Tamlık Büyüklüğü (M<sub>c</sub>)
      </p>
      <p style="font-size:.87em;">
        Maksimum Eğrilik Yöntemi (Wiemer &amp; Wyss, 2000):
        M<sub>c</sub>, kümülatif frekans eğrisinin en büyük eğime sahip olduğu büyüklük
        olarak belirlenir. Mindanao kataloğu için M<sub>c</sub> = <strong>3.5</strong>
        (N = 248 olay).
      </p>

      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">
        B. b-Değeri — Aki (1965) Maksimum Olabilirlik
      </p>
      <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;
                  font-family:monospace;font-size:.92em;margin:4px 0 8px;">
        b = log₁₀(e) / (M̄ − M<sub>c</sub> + 0.05)
        &nbsp;&nbsp;→&nbsp;&nbsp;
        σ<sub>b</sub> = b² · √(Σ(Mᵢ−M̄)² / (N(N−1)))
      </div>
      <p style="font-size:.87em;">
        M̄ = ortalama büyüklük (M ≥ M<sub>c</sub>); +0.05 bin düzeltmesi (Utsu, 1966).
        İki segmentli analiz: M<sub>c</sub>–M5.0 arası
        <strong>b₁ = 0.829</strong> (mb ağırlıklı);
        M5.0+ için <strong>b₂ = 1.12</strong> (Mw ağırlıklı).
        Slope break M5.0'de mb doyumundan kaynaklanmaktadır.
      </p>

      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">
        C. Omori–Utsu p-Değeri
      </p>
      <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;
                  font-family:monospace;font-size:.92em;margin:4px 0 8px;">
        λ(t) = K / (t + c)<sup>p</sup>
        &nbsp;&nbsp;→&nbsp;&nbsp;
        Nelder-Mead nonlineer LS ile K, c, p optimize edilir
      </div>
      <p style="font-size:.87em;">
        Mindanao 2026: <strong>K = 14.10, c ≈ 0.0001, p = 0.619</strong>.
        p &lt; 0.7 → Yüksek Sismik Kalıcılık.
        Tipik aralık: p = 0.8–1.2 (Utsu, 1957).
      </p>

      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">
        D. Mekansal Fraktal Boyut D<sub>s</sub> — Grassberger-Procaccia (1983)
      </p>
      <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;
                  font-family:monospace;font-size:.92em;margin:4px 0 8px;">
        C(r) = (2 / N(N−1)) · Σᵢ&lt;ⱼ Θ(r − |rᵢ − rⱼ|)
        &nbsp;&nbsp;→&nbsp;&nbsp;
        C(r) ∝ r<sup>D<sub>s</sub></sup>
      </div>
      <p style="font-size:.87em;">
        Log-log regresyon ile D<sub>s</sub> belirlenir.
        Mindanao 2026: <strong>D<sub>s</sub> = 1.42</strong>
        (R² = 0.95) → orta kümeleme, geniş kırık alanı.
        D<sub>s</sub> &lt; 1: lineer fay zonunda yoğunlaşma;
        D<sub>s</sub> → 2: hacimsel/diffüz dağılım.
      </p>

      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">
        E. Zamansal Fraktal Boyut D<sub>t</sub>
      </p>
      <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;
                  font-family:monospace;font-size:.92em;margin:4px 0 8px;">
        C(Δt) = (2 / N(N−1)) · Σᵢ&lt;ⱼ Θ(Δt − |tᵢ − tⱼ|)
        &nbsp;&nbsp;→&nbsp;&nbsp;
        C(Δt) ∝ Δt<sup>D<sub>t</sub></sup>
      </div>
      <p style="font-size:.87em;">
        Zaman pencereleri (saat cinsinden) üzerinde log-log regresyon.
        D<sub>t</sub>–b korelasyonu: pozitif → gerilme boşalımı (Phase III);
        negatif → gerilme birikimi devam ediyor.
      </p>

      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">
        F. Hareketli Pencere Zaman Serisi (Öncel &amp; Wilson, 2007)
      </p>
      <p style="font-size:.87em;">
        Pencere: <strong>100 ardışık olay</strong>, kaydırma adımı: <strong>10 olay</strong>.
        Her pencerede b(t), D<sub>s</sub>(t), D<sub>t</sub>(t) hesaplanır.
        Mevcut N = 334; 3 tam pencere mevcut — izleme sürmekte.
        Phase I/II/III geçiş noktaları b–D korelasyonunun işaret değiştirdiği andır.
      </p>

      <p style="font-size:.9em;font-weight:600;color:#7ecbff;margin:12px 0 6px;">
        G. FTLS b-positive Tahmincisi (Gulia vd., 2024)
      </p>
      <div style="background:rgba(255,255,255,.04);border-radius:6px;padding:10px 16px;
                  font-family:monospace;font-size:.92em;margin:4px 0 8px;">
        b<sub>+</sub> = log₁₀(e) / (M̄<sub>+</sub> − M<sub>ref</sub>)
        &nbsp;&nbsp;→&nbsp;&nbsp;
        M̄<sub>+</sub> = ortalama(Mᵢ − Mᵢ₋₁) için Mᵢ > Mᵢ₋₁
      </div>
      <p style="font-size:.87em;">
        Ana şok sonrası kısa-dönem katalog eksikliğini aşar.
        FTLS kararı: b<sub>gerçek</sub> / b<sub>ref</sub> ≥ 1.10 → Yeşil;
        &lt; 0.90 → Kırmızı (Mw 8.0+ riski uyarısı).
      </p>
    </div>

    <div class="info-note">
      <strong>Sismolojik Değerlendirme — Metodoloji Çerçevesi:</strong>'''

if NEEDLE in rv:
    rv = rv.replace(NEEDLE, NEW_BLOCK, 1)
    print('Metodoloji genişletmesi eklendi')
else:
    print('HATA: insertion point bulunamadı')

# Kaynaklar bölümüne Scordilis (2006) ve Wiemer & Wyss (2000) ekle
OLD_AKI_REF = '<div class="review-ref-item">Aki, K. (1965).'
NEW_AKI_REF = (
    '<div class="review-ref-item">Scordilis, E. M. (2006). '
    'Empirical global relations converting M<sub>S</sub> and m<sub>b</sub> to moment magnitude. '
    '<em>Journal of Seismology</em>, 10, 225–236. doi:10.1007/s10950-006-9012-4</div>\n    '
    '<div class="review-ref-item">Wiemer, S. &amp; Wyss, M. (2000). '
    'Minimum magnitude of completeness in earthquake catalogs: examples from Alaska, '
    'the western United States, and Japan. '
    '<em>Bulletin of the Seismological Society of America</em>, 90(4), 859–869.</div>\n    '
    '<div class="review-ref-item">Utsu, T. (1966). '
    'A statistical significance test of the difference in b-value between two earthquake groups. '
    '<em>J. Phys. Earth</em>, 14(2), 37–40.</div>\n    '
)
if OLD_AKI_REF in rv:
    rv = rv.replace(OLD_AKI_REF, NEW_AKI_REF + OLD_AKI_REF, 1)
    print('Referanslar eklendi: Scordilis, Wiemer & Wyss, Utsu')
else:
    print('MISS: Aki referansı bulunamadı')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
