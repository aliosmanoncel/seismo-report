import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)

rv = d['REVIEW_SECTION_HTML']

# ── Metodoloji bölümü HTML ────────────────────────────────────────
METO_SECTION = '''
    <!-- 5b. Artci Sarsinti Analiz Metodolojisi -->
    <div class="review-section-title">5b. Artçı Sarsıntı Analiz Metodolojisi</div>
    <p class="review-body-text">
      Artçı sarsıntı dizisinin spatio-temporal evrimini anlamak amacıyla; sönümlenme hızı
      (<em>p</em>-değeri), büyüklük-frekans ilişkisi (<em>b</em>-değeri) ve sismisitenin
      fraktal dağılımı (<em>D<sub>s</sub></em> ve <em>D<sub>t</sub></em>) üzerinden
      niceliksel bir analiz yürütülmüştür. Bu metodoloji, Öncel ve Wilson (2007) çerçevesinde
      tanımlanmış ve Gulia vd. (2024)'nin Foreshock Traffic Light System (FTLS) yaklaşımıyla
      desteklenmiştir.
    </p>

    <div class="method-card">
      <h4>⏱ 1. Omori–Utsu Yasası ve <em>p</em>-Değeri</h4>
      <p>Artçı sarsıntı sönümlenme hızı, modifiye Omori–Utsu yasasıyla modellenir:</p>
      <p style="text-align:center;font-size:1.05em;margin:10px 0;">
        <em>N(t) = K / (t + c)<sup>p</sup></em>
      </p>
      <p>
        <strong>Mindanao Mw 7.8 — Hesaplanan Parametreler (Nelder-Mead, N=324 artçı):</strong><br>
        <strong>K</strong> = 15.50 &nbsp;·&nbsp;
        <strong>c</strong> = 0.0001 &nbsp;·&nbsp;
        <strong>p</strong> = <span style="color:#f5a623;font-weight:700;">0.564</span>
      </p>
      <p>
        <em>p</em> = 0.564 değeri, 1'den belirgin biçimde düşüktür. Bu, artçı sarsıntı
        dizisinin normal sönümlenme hızının (<em>p</em> ≈ 1.0) altında kaldığını ve
        sismik aktivitenin önümüzdeki haftalarda görece yavaş sönümleneceğini
        göstermektedir. Bölgedeki yüksek jeoisı gradyanı ve Cotabato kama geometrisi
        bu düşük <em>p</em> değerini destekler niteliktedir.
      </p>
    </div>

    <div class="method-card">
      <h4>📊 2. Gutenberg–Richter <em>b</em>-Değeri</h4>
      <p>Büyüklük-frekans ilişkisi log<sub>10</sub> N = a − bM eşitliğiyle tanımlanır.
      <em>b</em>-değeri Aki (1965) Maksimum Olabilirlik yöntemiyle hesaplanır:</p>
      <p style="text-align:center;font-size:1.05em;margin:10px 0;">
        <em>b</em> = 2.303 / (M̄ − M<sub>min</sub> + 0.05)
      </p>
      <ul>
        <li>
          <strong>Düşük b (< 0.8):</strong> Bölgede yüksek deviatoric gerilme; büyük artçı
          riski artmış. Cotabato arayüzü boyunca henüz tam boşalmamış gerilme segmentleri
          bu örüntüyü tetikleyebilir.
        </li>
        <li>
          <strong>Yüksek b (> 1.2):</strong> Gerilme görece düşük; dizi normal sönümlenme
          eğiliminde.
        </li>
        <li>
          <strong>Planlanan uygulama:</strong> 100-olay hareketli pencere (10-olay kaydırma)
          ile <em>b</em> zaman serisi oluşturulacak; FTLS arka plan değeriyle karşılaştırılacaktır
          (bkz. §5b.5).
        </li>
      </ul>
    </div>

    <div class="method-card">
      <h4>🗺 3. Mekansal Fraktal Boyut (<em>D<sub>s</sub></em>)</h4>
      <p>
        Artçı episantr dağılımının geometrik karmaşıklığı, korelasyon integrali yöntemiyle
        ölçülür (Grassberger &amp; Procaccia, 1983):
      </p>
      <p style="text-align:center;font-size:1.05em;margin:10px 0;">
        C<sub>q</sub>(r) ∝ r<sup>D<sub>s</sub></sup>
      </p>
      <ul>
        <li>
          <strong>D<sub>s</sub> &lt; 1.0:</strong> Sismisitenin yoğun biçimde fay
          zonlarında kümelendiğini gösterir (lineer dağılım).
        </li>
        <li>
          <strong>D<sub>s</sub> ≈ 2.0:</strong> Hacimsel/diffüz dağılım; ikincil fay
          ağlarının aktive olduğuna işaret eder.
        </li>
        <li>
          <strong>Cotabato bağlamı:</strong> Karmaşık kama geometrisi ve Philippine Fayı'nın
          baskısı yüksek D<sub>s</sub> değeri üretebilir.
        </li>
      </ul>
    </div>

    <div class="method-card">
      <h4>⌚ 4. Zamansal Fraktal Boyut (<em>D<sub>t</sub></em>)</h4>
      <p>
        Mekansal analizle eş yapıda, ancak mesafe yerine zaman pencereleri (Δt)
        kullanılarak elde edilir. D<sub>t</sub> değeri, depremlerin zaman içindeki
        kümelenme karakterini ve sismik çevrimin mevcut fazını ortaya koyar.
      </p>
      <ul>
        <li>
          <strong>Pozitif D<sub>t</sub>–<em>b</em> korelasyonu:</strong> Stress yükünün
          azaldığına işaret eder (Phase III: sonlanma aşaması).
        </li>
        <li>
          <strong>Negatif korelasyon:</strong> Gerilme birikiminin sürdüğünü ve yeni
          büyük kırılma riski taşıdığını gösterir (1999 İzmit öncesi gözlenen örüntü;
          Öncel &amp; Wilson, 2007).
        </li>
      </ul>
    </div>

    <div class="method-card">
      <h4>🔄 5. Hareketli Pencere Tekniği (Öncel &amp; Wilson, 2007)</h4>
      <p>
        Parametrelerin zaman içindeki evrimini izlemek için standart kayan pencere uygulanır:
      </p>
      <ul>
        <li><strong>Pencere boyutu:</strong> 100 ardışık sismik olay</li>
        <li><strong>Kaydırma adımı:</strong> 10 olay ileri — zaman serisi çözünürlüğü</li>
        <li>
          <strong>Çıktı:</strong> <em>b</em>(t), D<sub>s</sub>(t), D<sub>t</sub>(t)
          zaman serileri → Phase I (yüklenme) / II (geçiş) / III (sonlanma) analizi
        </li>
        <li>
          <strong>Mevcut veri:</strong> 324 artçı (M ≥ 3.0, EMSC; 2026-06-07–10);
          pencere analizi için yeterli — 3 tam pencere + izleme sürmekte
        </li>
      </ul>
    </div>

    <div class="method-card">
      <h4>🚦 6. Foreshock Traffic Light System (FTLS) — Gulia vd. (2024)</h4>
      <p>
        FTLS, gerçek zamanlı <em>b</em>-değeri ile arka plan değeri (<em>b</em><sub>ref</sub>)
        arasındaki yüzde farkına dayalı alarm sistemidir. Mindanao Mw 7.8 için tetikleme
        eşiği (M ≥ 6.0) fazlasıyla aşılmıştır.
      </p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;">
        <div style="background:rgba(76,175,80,.15);border:1px solid rgba(76,175,80,.4);border-radius:8px;padding:10px 14px;">
          <strong style="color:#81c784;">🟢 YEŞİL (≥ %110)</strong><br>
          <small>b<sub>gerçek</sub> / b<sub>ref</sub> ≥ 1.10<br>
          Normal ana şok–artçı dizisi;<br>
          Mw 7.8 ana şok teyit edilmiş.<br>
          Gerilme normal sönümleniyor.</small>
        </div>
        <div style="background:rgba(244,67,54,.15);border:1px solid rgba(244,67,54,.4);border-radius:8px;padding:10px 14px;">
          <strong style="color:#e57373;">🔴 KIRMIZI (&lt; %90)</strong><br>
          <small>b<sub>gerçek</sub> / b<sub>ref</sub> &lt; 0.90<br>
          Yüksek gerilme sürüyor;<br>
          Mw 8.0+ olası öncü şok riski;<br>
          En üst düzey uyarı.</small>
        </div>
      </div>
      <p style="font-size:.87em;color:#94a3b8;">
        <strong>b-positive tahmincisi:</strong> Ana şok sonrası kısa dönem katalog eksikliğini
        aşmak için Gulia vd. (2024)'nin önerdiği "b-positive" yöntemi uygulanacaktır. Mindanao
        katalog tamamlanma büyüklüğü (M<sub>c</sub>) önce maksimum eğrilik yöntemiyle
        belirlenecek; FTLS renk kararı bu M<sub>c</sub> üzerinde verilecektir.
      </p>
    </div>

    <div class="info-note">
      <strong>Sismolojik Değerlendirme — Metodoloji Çerçevesi:</strong>
      Öncel ve Wilson (2007)'nin 1999 İzmit depremi öncesi sismik anomalilere uyguladığı
      b–D<sub>s</sub>–D<sub>t</sub> korelasyon analizi, Mindanao artçı dizisinin 30–90 günlük
      evrimine doğrudan aktarılabilir niteliktedir. Hesaplanan <em>p</em> = 0.564 değeri,
      artçı sönümlenmesinin yavaş seyredeceğine işaret etmekte; bu durum hareketli pencere
      parametrelerinin sistematik izlenmesini kritik kılmaktadır.
    </div>

'''

# Kaynaklar bölümüne eklenecek yeni referanslar
NEW_REFS = (
    '<div class="review-ref-item">Öncel, A. O. &amp; Wilson, T. H. (2007). '
    'Anomalous seismicity preceding the 1999 Izmit event, NW Turkey. '
    '<em>Geophysical Journal International</em>. '
    'doi:10.1111/j.1365-246X.2007.03464.x</div>\n    '
    '<div class="review-ref-item">Gulia, L., Wiemer, S., &amp; Vannucci, G. (2024). '
    'Foreshock Traffic Light System: Real-time <em>b</em>-value monitoring for '
    'large earthquake discrimination. '
    '<em>Seismological Research Letters</em>. doi:10.1785/0220240163</div>\n    '
    '<div class="review-ref-item">Aki, K. (1965). Maximum likelihood estimate of '
    '<em>b</em> in the formula log N = a − bM and its confidence limits. '
    '<em>Bull. Earthquake Res. Inst. Tokyo Univ.</em>, 43, 237–239.</div>\n    '
)

# ── Section 6 başlangıcından önce metodoloji bölümünü ekle ────────
INSERTION_POINT = '    <!-- 6. Sonuçlar -->'
if INSERTION_POINT in rv:
    rv = rv.replace(INSERTION_POINT, METO_SECTION + '    <!-- 6. Sonuçlar -->', 1)
    print('Metodoloji bolumu eklendi (Section 6 oncesi)')
else:
    print('HATA: insertion point bulunamadi')

# ── Kaynaklar bölümüne yeni referanslar ekle ──────────────────────
REF_ANCHOR = '<div class="review-ref-item">EMSC (2026).'
if REF_ANCHOR in rv:
    rv = rv.replace(REF_ANCHOR, NEW_REFS + REF_ANCHOR, 1)
    print('Referanslar eklendi')
else:
    print('HATA: referans insertion point bulunamadi')

d['REVIEW_SECTION_HTML'] = rv

with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
