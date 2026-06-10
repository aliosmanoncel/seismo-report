import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

FORECAST_SECTION = '''
    <!-- 6b. 90 Gunluk Risk Ongorüsü -->
    <div class="review-section-title">6b. Gelecek 90 Günlük Sismik Risk Öngörüsü</div>
    <p class="review-body-text">
      Hesaplanan parametre seti (Omori-Utsu K=14.10, p=0.619; G-R b=0.635, Mc=3.5;
      FTLS <span style="color:#ef9a9a;font-weight:600;">🔴 KIRMIZI</span>) kullanılarak
      artçı sarsıntı dizisinin 90 günlük beklentisi niceliksel olarak modellenmiştir.
    </p>

    <!-- Omori Hız Projeksiyonu -->
    <div class="method-card">
      <h4>📉 Omori-Utsu Hız Projeksiyonu — p = 0.619</h4>
      <table class="review-table" style="font-size:.87em;table-layout:fixed;margin-top:8px;">
        <colgroup><col style="width:22%"><col style="width:22%"><col style="width:22%"><col style="width:34%"></colgroup>
        <thead>
          <tr><th>Zaman</th><th>Anlık hız (dep/gün)</th><th>Dönem toplamı (M≥3.5)</th><th>Değerlendirme</th></tr>
        </thead>
        <tbody>
          <tr><td>3. gün (bugün)</td><td style="color:#ef5350;font-weight:700;">~24</td>
              <td>—</td><td>Yüksek aktivite devam ediyor</td></tr>
          <tr><td>7. gün</td><td style="color:#ff8f00;">~14</td>
              <td>~72 (3–7. gün)</td><td>Hâlâ yoğun faz</td></tr>
          <tr><td>30. gün</td><td style="color:#ffb74d;">~6</td>
              <td>~193 (7–30. gün)</td><td>Azalıyor, tehlike sürüyor</td></tr>
          <tr><td>60. gün</td><td style="color:#81c784;">~4</td>
              <td>~137 (30–60. gün)</td><td>Kronik arka plan artışı</td></tr>
          <tr><td>90. gün</td><td style="color:#81c784;">~3</td>
              <td>~98 (60–90. gün)</td><td>Arka plana yaklaşıyor</td></tr>
          <tr style="font-weight:600;background:rgba(255,255,255,.04);">
              <td>Toplam (3–90. gün)</td><td>—</td>
              <td style="color:#f5a623;">~500 olay</td>
              <td>M≥3.5 kümülatif</td></tr>
        </tbody>
      </table>
      <p style="font-size:.83em;color:#94a3b8;margin-top:8px;">
        p=0.619 &lt; 0.7 → sönümlenme normalin <strong>%36 altında</strong>.
        p=1.0 (normal) senaryosunda aynı dönem için ~180 olay beklenirdi;
        yavaş sönümlenme ~2.8× daha uzun tehlike penceresi yaratmaktadır.
      </p>
    </div>

    <!-- Buyukluk Olasilik Tahmini -->
    <div class="method-card">
      <h4>📊 Büyüklük-Frekans Projeksiyonu — 90 Günlük Beklenti</h4>
      <table class="review-table" style="font-size:.87em;table-layout:fixed;margin-top:8px;">
        <colgroup><col style="width:14%"><col style="width:20%"><col style="width:20%"><col style="width:46%"></colgroup>
        <thead>
          <tr><th>M eşiği</th><th>b=0.635 beklenti</th><th>b₂=1.12 beklenti</th><th>Sismik bağlam</th></tr>
        </thead>
        <tbody>
          <tr><td>M ≥ 4.0</td><td>~241</td><td>~175</td><td>Yapı hasarı için alt sınır; çok sık</td></tr>
          <tr><td>M ≥ 5.0</td><td>~56</td><td>~30</td><td>Zayıf yapılarda ek hasar; haftalık</td></tr>
          <tr><td>M ≥ 5.5</td><td>~27</td><td>~11</td><td>Orta hasar; gerilme birikimi göstergesi</td></tr>
          <tr style="color:#ffb74d;"><td>M ≥ 6.0</td><td>~13</td><td>~4</td>
              <td>Ciddi hasar riski; yaklaşık 2 haftada bir</td></tr>
          <tr style="color:#ef5350;font-weight:600;"><td>M ≥ 6.5</td><td>~6</td><td>~1–2</td>
              <td>Ağır hasar; Bath sınırına yakın</td></tr>
          <tr style="color:#ef5350;font-weight:700;background:rgba(244,67,54,.08);">
              <td>M ≥ 7.0</td><td>~3</td><td>&lt; 1</td>
              <td>Olası; b₂ ile &lt;1; izleme kritik</td></tr>
        </tbody>
      </table>
      <div style="font-size:.83em;color:#94a3b8;margin-top:8px;line-height:1.6;">
        <strong>b=0.635</strong> (tüm aralık, üst tahmin) ·
        <strong>b₂=1.12</strong> (M5.0+ segmenti, alt tahmin) ·
        İki sütun aralığı gerçek beklentiyi kapsamaktadır.
        Halihazırda gözlenen <strong>3 adet M6+</strong>,
        <a href="https://en.wikipedia.org/wiki/Bath%27s_law" target="_blank"
           style="color:#90caf9;">Bath Yasası</a>
        beklentisini (en büyük artçı ≈ Mw 7.8 − 1.2 = <strong>Mw 6.6</strong>) karşılamıştır;
        ancak b=0.635 ve FTLS KIRMIZI statüsü ek büyük artçıların olabileceğine işaret etmektedir.
      </div>
    </div>

    <!-- Risk Ozeti -->
    <div class="rec-card" style="border-color:rgba(244,67,54,.4);">
      <h4>⚠️ 90 Günlük Sismik Risk Özeti</h4>
      <ul>
        <li><strong>Kısa dönem (0–30 gün):</strong> Günde 6–24 M≥3.5 artçı bekleniyor.
          Zayıflamış yapılar için tekrarlayan sarsıntı tehlikesi kritik düzeyde.
          M6.0+ olasılığı aylık ≈ 4–6 olay.</li>
        <li><strong>Orta dönem (30–90 gün):</strong> Günlük hız 3–6 seviyesine gerilerken
          toplam ek 235 olay (M≥3.5) bekleniyor.
          p=0.619 nedeniyle arka plan seviyesine dönüş gecikmeli — normal depremlere kıyasla
          yaklaşık 3× daha yavaş sönümlenme.</li>
        <li><strong>Bath Yasası durumu:</strong> Mevcut en büyük artçı M6.7 (Bath beklentisi M6.6) —
          bu eşik karşılandı. Ancak FTLS KIRMIZI + düşük b + düşük p kombinasyonu
          yeni M6.5+ olay riskini dışlamıyor.</li>
        <li><strong>FTLS izleme:</strong> Gerçek zamanlı b-değeri b_ref'in %90'ına ulaşana dek
          (b/b_ref ≥ 0.90 → SARI geçiş) KIRMIZI durum geçerlidir.
          Günlük artçı katalog güncellemesi ile izleme önerilir.</li>
        <li><strong>Öncelik bölgesi:</strong> Cotabato arayüzü boyunca
          General Santos, Koronadal, Digos; tsunami riski Sarangani Körfezi kıyıları.</li>
      </ul>
    </div>

'''

# Section 7 (Referanslar) oncesine ekle
NEEDLE = '    <!-- Referanslar -->'
if NEEDLE in rv:
    rv = rv.replace(NEEDLE, FORECAST_SECTION + NEEDLE, 1)
    print('90 günlük öngörü bölümü eklendi')
else:
    print('HATA: insertion point bulunamadı')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
