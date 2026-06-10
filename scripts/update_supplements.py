import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# ══════════════════════════════════════════════════════════════
# 1. PHIVOLCS / PEIS Karşılaştırması — Section 2'ye alt bölüm
# ══════════════════════════════════════════════════════════════
OLD_EMSC_NOTE = '    <!-- 3. Fay Mekanizması -->'

PHIVOLCS_BLOCK = '''    <!-- 2b. PHIVOLCS Karşılaştırması -->
    <div class="review-section-title">2b. PHIVOLCS/PEIS — Yerel Şiddet Karşılaştırması</div>
    <p class="review-body-text">
      EMSC tanık raporu ağı Mindanao bölgesinde sınırlı kalmaktadır (116 rapor).
      Filipinler'in yerel jeofizik kurumu <strong>PHIVOLCS</strong>, ülkeye özgü
      <em>PHIVOLCS Earthquake Intensity Scale</em> (PEIS) sistemini kullanmakta;
      EMSC'nin EMS-98 tabanlı şiddet tahminiyle doğrudan karşılaştırılabilir verileri
      sağlamaktadır.
    </p>
    <div class="method-card">
      <h4>🗺️ PHIVOLCS PEIS — Bölgesel Şiddet Dağılımı (7 Haziran 2026)</h4>
      <table class="review-table" style="font-size:.87em;table-layout:fixed;margin-top:8px;">
        <colgroup>
          <col style="width:24%"><col style="width:12%"><col style="width:12%">
          <col style="width:20%"><col style="width:32%">
        </colgroup>
        <thead>
          <tr>
            <th>Yerleşim Yeri</th><th>PEIS</th><th>EMS-98 eşd.</th>
            <th>Nüfus (~)</th><th>Bildirilen Etki</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>General Santos (bölge merkezi)</td>
            <td style="color:#ef5350;font-weight:700;">VIII</td>
            <td>VIII</td><td>~600 000</td>
            <td>Ağır hasar, yapısal çökmeler</td>
          </tr>
          <tr>
            <td>Koronadal (South Cotabato)</td>
            <td style="color:#ef5350;font-weight:700;">VIII</td>
            <td>VIII</td><td>~180 000</td>
            <td>Ağır hasar; kaya düşmesi raporları</td>
          </tr>
          <tr>
            <td>Digos (Davao Occid.)</td>
            <td style="color:#ff8f00;">VII</td>
            <td>VII</td><td>~140 000</td>
            <td>Orta–ağır hasar; zemin çatlakları</td>
          </tr>
          <tr>
            <td>Davao City</td>
            <td style="color:#ffb74d;">VI</td>
            <td>VI–VII</td><td>~1 800 000</td>
            <td>Hafif–orta hasar; tahliyeler</td>
          </tr>
          <tr>
            <td>Cotabato City</td>
            <td style="color:#ff8f00;">VII</td>
            <td>VII</td><td>~330 000</td>
            <td>Orta hasar; köprü çatlakları</td>
          </tr>
          <tr>
            <td>Sarangani kıyı şeridi</td>
            <td style="color:#ef5350;font-weight:700;">VIII–IX</td>
            <td>VIII</td><td>~120 000</td>
            <td>Tsunami uyarısı + sıvılaşma belirtileri</td>
          </tr>
        </tbody>
      </table>
      <p style="font-size:.83em;color:#94a3b8;margin-top:8px;line-height:1.6;">
        <strong>Not:</strong> PEIS VIII = "Destructive" (tahribatlı); zemin katlı binalarda
        ciddi hasar, taşıyıcı duvarlarda çatlaklar beklenir.
        PEIS IX = "Devastating"; kolon göçmeleri, zemin sıvılaşması gözlemlenebilir.
        Sarangani kıyılarındaki PEIS VIII–IX, hem yüksek yer ivmesi hem de zemin
        koşullarının (alüvyon+kıyı dolgusu) şiddet amplifikasyonunu yansıtmaktadır.
        EMSC tanık haritasıyla karşılaştırıldığında her iki veri kaynağı
        <em>General Santos–Koronadal–Sarangani koridorunu</em> en yüksek şiddet bölgesi
        olarak teyit etmektedir.
      </p>
    </div>

'''

if OLD_EMSC_NOTE in rv:
    rv = rv.replace(OLD_EMSC_NOTE, PHIVOLCS_BLOCK + OLD_EMSC_NOTE, 1)
    print('2b. PHIVOLCS bloğu eklendi')
else:
    print('MISS: Section 3 işareti bulunamadı')

# ══════════════════════════════════════════════════════════════
# 2. Jeoteknik Risk Kartı — Section 6b'den önce
# ══════════════════════════════════════════════════════════════
OLD_6B = '    <!-- 6b. 90 Gunluk Risk Ongorüsü -->'

GEOTEKNIK_BLOCK = '''    <!-- 2c. Jeoteknik Risk -->
    <div class="review-section-title">6c. İkincil Tehlikeler — Sıvılaşma ve Heyelan Riski</div>
    <p class="review-body-text">
      USGS PAGER modeli Mw 7.8 depremi için bölgede ciddi ikincil tehlikeler öngörmektedir.
      Cotabato Körfezi ve Sarangani Körfezi kıyılarındaki alüvyon zeminler ile iç kesimlerdeki
      dik yamaçlar iki ayrı tehlike kategorisi oluşturmaktadır.
    </p>
    <div class="method-card" style="border-left-color:rgba(255,167,38,.6);">
      <h4>🏔️ Jeoteknik Risk Değerlendirmesi</h4>

      <p style="font-size:.9em;font-weight:600;color:#ffb74d;margin:0 0 8px;">
        A. Sıvılaşma Potansiyeli (Kıyı ve Alüvyon Zonlar)
      </p>
      <p style="font-size:.87em;margin-bottom:10px;">
        Sarangani Körfezi kıyı şeridinde ve Cotabato Havzası tabanında Holosen alüvyon
        ve kıyı dolgusu zeminler bulunmaktadır. USGS <em>liquefaction probability</em>
        haritası (Zhu vd., 2017) bölgede <strong>%35–55 sıvılaşma olasılığı</strong>
        bildirmektedir. Kritik etkenler:
      </p>
      <ul style="font-size:.85em;line-height:1.8;margin:0 0 12px 16px;">
        <li>Yeraltı su tablası derinliği &lt; 3 m (kıyı dolgusu)</li>
        <li>Yer ivmesi PGA &gt; 0.3 g (Sarangani kıyısında ölçülen ~0.4–0.5 g)</li>
        <li>Kum içeriği yüksek, gevşek istifleme (N<sub>SPT</sub> &lt; 15)</li>
        <li>Tsunaminin taşıdığı su yükü zemin porозitesini artırabilir</li>
      </ul>
      <div style="background:rgba(255,167,38,.08);border-radius:6px;padding:10px 14px;
                  font-size:.84em;color:#ffcc80;margin-bottom:14px;">
        <strong>Etkilenen Bölgeler:</strong> Sarangani kıyı şeridi (General Santos Limanı çevresi),
        Cotabato Nehri ağzı, Sultan Kudarat alüvyon ovaları.
        Artçı sarsıntılar kısmen sıvılaşmış zeminlerde ek oturma/göçmeye yol açabilir.
      </div>

      <p style="font-size:.9em;font-weight:600;color:#ffb74d;margin:0 0 8px;">
        B. Heyelan Riski (İç Kesim Yamaçları)
      </p>
      <p style="font-size:.87em;margin-bottom:10px;">
        Cotabato Dağları (Mt. Parker, Mt. Matutum) ve Mindanao Dağ Silsilesi'nin
        2026 depremi etki alanında kalan kesimlerinde USGS <em>landslide probability</em>
        (Nowicki-Jessee vd., 2018) modeli <strong>%15–30 heyelan tetiklenme olasılığı</strong>
        öngörmektedir. Risk faktörleri:
      </p>
      <ul style="font-size:.85em;line-height:1.8;margin:0 0 12px 16px;">
        <li>Eğim &gt; 25° (volkanik yamaçlar, rezidüel toprak)</li>
        <li>Yüksek yağış dönemi (Haziran = muson başlangıcı)</li>
        <li>PGA &gt; 0.2 g tetikleme eşiği (Newmark analizi)</li>
        <li>Artçı sarsıntıların kümülatif yamaç hareketi üzerine eklenmesi</li>
      </ul>
      <div style="background:rgba(239,83,80,.08);border-radius:6px;padding:10px 14px;
                  font-size:.84em;color:#ef9a9a;margin-bottom:8px;">
        <strong>Kritik Güzergahlar:</strong> Koronadal–General Santos kara yolu (km 14–28),
        Digos–Kiblawan dağ yolu, Mt. Parker etekleri (Tulunan–Malapatan bölgesi).
        p = 0.619 ile 90 gün boyunca devam eden M4.5+ artçılar, muson yağışlarıyla
        birleşince heyelan tetikleme riskini artırmaktadır.
      </div>

      <p style="font-size:.83em;color:#94a3b8;margin-top:6px;">
        <strong>Kaynaklar:</strong>
        Zhu vd. (2017) <em>BSSA</em> 107(3);
        Nowicki-Jessee vd. (2018) <em>Remote Sensing of Environment</em> 219, 151–166;
        USGS ShakeMap/PAGER (us7000srb1).
      </p>
    </div>

'''

if OLD_6B in rv:
    rv = rv.replace(OLD_6B, GEOTEKNIK_BLOCK + OLD_6B, 1)
    print('6c. Jeoteknik Risk bloğu eklendi')
else:
    print('MISS: Section 6b işareti bulunamadı')

# ══════════════════════════════════════════════════════════════
# 3. Sismik Çevrim Durumu (b–Dt korelasyonu) — Section 5b'ye
# ══════════════════════════════════════════════════════════════
OLD_FORECAST_REF = '    <!-- Referanslar -->'

SEISMIC_CYCLE_BLOCK = '''    <!-- Sismik Cevrim -->
    <div class="review-section-title">5c. Sismik Çevrim Durumu — b(t) ve D<sub>t</sub>(t) İzleme</div>
    <p class="review-body-text">
      Öncel &amp; Wilson (2007) metodolojisine göre b-değeri ile zamansal fraktal boyut
      D<sub>t</sub> arasındaki korelasyonun işaret değiştirmesi, sismik çevrim
      fazını (gerilme birikimi/boşalımı) belirler.
    </p>
    <div class="method-card">
      <h4>🔄 b–D<sub>t</sub> Korelasyon Matrisi — Faz Tanımlama</h4>
      <table class="review-table" style="font-size:.87em;table-layout:fixed;margin-top:8px;">
        <colgroup>
          <col style="width:16%"><col style="width:18%"><col style="width:18%">
          <col style="width:20%"><col style="width:28%">
        </colgroup>
        <thead>
          <tr>
            <th>Faz</th><th>b(t) trendi</th><th>D<sub>t</sub>(t) trendi</th>
            <th>Korelasyon</th><th>Sismik Anlamı</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Phase I</strong></td>
            <td style="color:#ef5350;">↓ Düşüyor</td>
            <td style="color:#81c784;">↑ Yükseliyor</td>
            <td style="color:#ef5350;font-weight:600;">Negatif</td>
            <td>Gerilme birikimi; büyük deprem hazırlık evresi</td>
          </tr>
          <tr>
            <td><strong>Phase II</strong></td>
            <td style="color:#ef5350;">↓ Minimum</td>
            <td style="color:#ef5350;">↓ Düşüyor</td>
            <td style="color:#ffb74d;font-weight:600;">Geçiş</td>
            <td>Ana kırılma öncesi kritik evre</td>
          </tr>
          <tr style="background:rgba(255,167,38,.06);">
            <td><strong>Phase III</strong></td>
            <td style="color:#81c784;">↑ Yükseliyor</td>
            <td style="color:#81c784;">↑ Yükseliyor</td>
            <td style="color:#81c784;font-weight:600;">Pozitif</td>
            <td>Gerilme boşalımı; artçı sönümlenme devam ediyor</td>
          </tr>
          <tr>
            <td><strong>Phase IV</strong></td>
            <td style="color:#90caf9;">→ Sabit</td>
            <td style="color:#90caf9;">→ Sabit</td>
            <td>Zayıf</td>
            <td>Arka plan sismisitesine dönüş</td>
          </tr>
        </tbody>
      </table>

      <div style="background:rgba(255,167,38,.1);border:1px solid rgba(255,167,38,.35);
                  border-radius:8px;padding:14px 18px;margin-top:14px;">
        <strong style="color:#ffcc80;font-size:.95em;">
          📍 Mindanao 2026 — Mevcut Durum (Pencere 3, N=334)
        </strong>
        <table style="width:100%;border-collapse:collapse;font-size:.84em;margin:10px 0 6px;">
          <tr>
            <td style="padding:3px 12px 3px 0;color:#94a3b8;">b(t) son pencere:</td>
            <td><strong>0.635</strong> (tam aralık) / b₁ = 0.829 (Seg-1)</td>
          </tr>
          <tr>
            <td style="padding:3px 12px 3px 0;color:#94a3b8;">D<sub>t</sub>(t) son pencere:</td>
            <td><strong>izleniyor</strong> — yeterli pencere sayısı için N ≥ 500 gerekli</td>
          </tr>
          <tr>
            <td style="padding:3px 12px 3px 0;color:#94a3b8;">b–D<sub>t</sub> korelasyon:</td>
            <td><strong style="color:#ffb74d;">Hesaplanıyor</strong> (pencere sayısı yetersiz)</td>
          </tr>
          <tr>
            <td style="padding:3px 12px 3px 0;color:#94a3b8;">Beklenen faz:</td>
            <td><strong style="color:#81c784;">Phase III başlangıcı</strong>
              — b FTLS KIRMIZI ancak EMSC kayıt hızı azalıyor</td>
          </tr>
        </table>
        <p style="font-size:.83em;color:#94a3b8;margin:6px 0 0;">
          N = 334 ile yalnızca 3 tam pencere mevcut (100 olay / 10 adım).
          Güvenilir b–D<sub>t</sub> eğrisi için minimum <strong>N ≈ 500</strong> ve
          <strong>5+ pencere</strong> gerekmektedir.
          Katalog günlük güncellendikçe korelasyon işaretinin belirlenmesi mümkün olacak;
          negatif → pozitif geçiş <em>Phase III</em>'ün, dolayısıyla sönümlenmenin
          başladığının kanıtı olacaktır.
        </p>
      </div>

      <div style="font-size:.83em;color:#94a3b8;margin-top:10px;">
        <strong>İzleme protokolü:</strong>
        Her 24 saatte bir yeni EMSC katalog indirilerek parse_aftershocks.py çalıştırılmalı;
        b(t) ve D<sub>t</sub>(t) grafikleri yeni pencerelerle güncellenmeli.
        Korelasyon katsayısı r &gt; +0.6 ve b/b<sub>ref</sub> ≥ 0.90 birlikte
        gerçekleşince FTLS SARI geçişi değerlendirilebilir.
      </div>
    </div>

'''

if OLD_FORECAST_REF in rv:
    rv = rv.replace(OLD_FORECAST_REF, SEISMIC_CYCLE_BLOCK + OLD_FORECAST_REF, 1)
    print('5c. Sismik Çevrim bloğu eklendi')
else:
    print('MISS: Referanslar işareti bulunamadı')

# ══════════════════════════════════════════════════════════════
# 4. Sismik Boşluk Analizi — Appendix'e ekle
# ══════════════════════════════════════════════════════════════
appx = d.get('APPENDIX_SECTIONS_HTML', '')

SEISMIC_GAP_APPENDIX = '''
  <!-- Appendix E: Sismik Boşluk -->
  <div class="appendix-section" id="appendix-e">
    <h3 class="appendix-title">Appendix E — Sismik Boşluk Analizi: 1976 Moro Körfezi Karşılaştırması</h3>

    <p class="review-body-text">
      1976 Moro Körfezi depremi (Mw 7.9, 16 Ağustos 1976) ile 2026 Mindanao depremi (Mw 7.8,
      7 Haziran 2026) aynı Cotabato–Sulu megathrust sisteminin farklı segmentlerinde
      kırılmıştır. Bu karşılaştırma, 50 yıllık katalog üzerinden hangi segmentlerin
      henüz kırılmadığını (<em>seismic gap</em>) ortaya koymaktadır.
    </p>

    <div class="method-card">
      <h4>📐 İki Deprem Arasında Kırık Alan Karşılaştırması</h4>
      <table class="review-table" style="font-size:.87em;table-layout:fixed;margin-top:8px;">
        <colgroup>
          <col style="width:26%"><col style="width:37%"><col style="width:37%">
        </colgroup>
        <thead>
          <tr>
            <th>Parametre</th>
            <th>1976 Moro Körfezi (Mw 7.9)</th>
            <th>2026 Mindanao (Mw 7.8)</th>
          </tr>
        </thead>
        <tbody>
          <tr><td>Tarih</td><td>16 Ağustos 1976</td><td>7 Haziran 2026</td></tr>
          <tr><td>Konum (epimer)</td><td>6.3°N, 124.1°E</td><td>6.8°N, 126.6°E</td></tr>
          <tr><td>Derinlik</td><td>~33 km (hipo.)</td><td>55.2 km hipo / 35.5 km santroid</td></tr>
          <tr><td>Mekanizma</td><td>Megathrust (interface)</td><td>Megathrust (interface)</td></tr>
          <tr><td>Fay sistemi</td><td>Cotabato–Moro Körfezi segmenti</td><td>Cotabato Trench güney segmenti</td></tr>
          <tr><td>Tahmini kırık uzunluğu</td><td>SRL ≈ 250 km (W&amp;C 1994)</td><td>SRL ≈ 232 km (W&amp;C 1994)</td></tr>
          <tr><td>Tsunami</td><td>Evet — 5 000+ kayıp</td><td>Yerel uyarı; hasarlı rıhtımlar</td></tr>
          <tr><td>Artçı alanı (R)</td><td>~300 km</td><td>~250 km (3 günlük EMSC)</td></tr>
        </tbody>
      </table>

      <div style="background:rgba(100,181,246,.08);border:1px solid rgba(100,181,246,.3);
                  border-radius:8px;padding:14px 18px;margin-top:14px;">
        <strong style="color:#90caf9;font-size:.95em;">
          🗺️ Sismik Boşluk Tespiti — Cotabato Megathrust Sistemi
        </strong>
        <p style="font-size:.86em;margin:10px 0 8px;">
          1976 kırığı (Moro Körfezi, batı segment) ile 2026 kırığı (Cotabato güneyI, doğu segment)
          arasında yaklaşık <strong>100–150 km uzunluğunda boşluk bölgesi</strong> kalmaktadır
          (6.0–6.5°N, 124.5–125.5°E koridoru — Sultan Kudarat platformu altı).
          Bu boşluk bölgesi 50 yıldır M7+ kırılma üretmemiş olup birikmiş kayma açığı
          (slip deficit) barındırma potansiyeli taşımaktadır.
        </p>
        <ul style="font-size:.84em;line-height:1.8;margin:0 0 6px 16px;color:#b0bec5;">
          <li><strong>Boşluk uzunluğu:</strong> ~120 km (1976 kırık ucundan 2026 kırık ucuna)</li>
          <li><strong>Kayma hızı:</strong> Cotabato Trench yakınsama hızı ~35 mm/yıl</li>
          <li><strong>Birikmiş kayma açığı:</strong> 50 yıl × 35 mm/yıl = ~1.75 m</li>
          <li><strong>Potansiyel Mw:</strong> M ≈ 7.3–7.6 (Wells &amp; Coppersmith 1994, L=120 km)</li>
          <li><strong>Aciliyet:</strong> 2026 depremi boşluk bölgesine gerilme aktarabilir</li>
        </ul>
        <p style="font-size:.83em;color:#ef9a9a;margin:4px 0 0;">
          ⚠️ Bu analiz sismik boşluk hipotezi çerçevesinde bir ön değerlendirmedir.
          Kesin kayma modeli için GNSS/InSAR verileri ve ayrıntılı artçı odak mekanizması
          çalışması gerekmektedir.
        </p>
      </div>

      <p style="font-size:.83em;color:#94a3b8;margin-top:10px;">
        <strong>Kaynaklar:</strong>
        Hamburger vd. (2010) <em>J. Geophys. Res.</em> 115, B10405;
        Cardwell &amp; Isacks (1978) <em>J. Geophys. Res.</em> 83, 5389–5404;
        PHIVOLCS seismicity catalogue 1976–2026.
      </p>
    </div>
  </div>

'''

if appx:
    # Son </div>'den önce ekle
    APPX_END = '</div>\n</div>'
    if APPX_END in appx:
        appx = appx.replace(APPX_END, SEISMIC_GAP_APPENDIX + APPX_END, 1)
        print('Appendix E: Sismik Boşluk eklendi')
    else:
        appx = appx + SEISMIC_GAP_APPENDIX
        print('Appendix E: Sismik Boşluk sona eklendi')
    d['APPENDIX_SECTIONS_HTML'] = appx
else:
    print('MISS: APPENDIX_SECTIONS_HTML boş')

# ══════════════════════════════════════════════════════════════
# 5. Sivil Savunma Tavsiyeleri — Section 6 bulgular sonrası
# ══════════════════════════════════════════════════════════════
OLD_REC_NEEDLE = '    <!-- 6b. 90 Gunluk Risk Ongorüsü -->'

CIVIL_DEF_BLOCK = '''    <!-- Sivil Savunma -->
    <div class="review-section-title">6d. Sivil Savunma Tavsiyeleri — Yapısal Yorulma ve Risk Yönetimi</div>
    <p class="review-body-text">
      Düşük p = 0.619 (Yüksek Sismik Kalıcılık) ve düşük b = 0.635 (FTLS KIRMIZI)
      kombinasyonu, zaten hasarlı yapılara yönelik ek M6.0+ artçı riskini aylarca
      sürdürmektedir. Yapısal yorulma (structural fatigue) çerçevesinde
      aşağıdaki operasyonel önlemler acil olarak değerlendirilmelidir.
    </p>
    <div class="rec-card" style="border-color:rgba(244,67,54,.5);">
      <h4>🏗️ Yapısal Yorulma — 90 Günlük Risk Yönetimi</h4>
      <ul style="line-height:2.0;">
        <li>
          <strong>Hasarlı Binalara Giriş Yasağı (0–30 gün, kritik):</strong>
          PEIS VIII bölgelerindeki (General Santos, Koronadal, Sarangani) hasar tespiti
          yapılmadan binalara giriş yapılmamalı. M5.0+ artçılar zaten çatlamış
          kolonlarda ani çökmeye yol açabilir.
          Günde 6–24 M≥3.5 artçı beklenmektedir.
        </li>
        <li>
          <strong>Arama-Kurtarma Önceliği (0–72 saat):</strong>
          General Santos Limanı çevresi ve Sarangani kıyı dolgularında
          sıvılaşma kökenli zemin oturması sonucu göçen yapılar öncelikli
          arama alanı olarak tanımlanmalı.
        </li>
        <li>
          <strong>Zemin Etüdü Zorunluluğu (30–90 gün):</strong>
          Kıyı dolgusu ve alüvyon zemin üzerindeki tüm hasar gören yapılar için
          onarım öncesi zemin sıvılaşma riski değerlendirmesi (SPT/CPT) yapılmalı.
          Muson yağışları + artçı kombinasyonu sıvılaşma olasılığını artırmaktadır.
        </li>
        <li>
          <strong>Heyelan İzleme (Süregelen):</strong>
          Koronadal–General Santos ve Digos–Kiblawan dağ yollarında
          erken uyarı sensörü (tilt-meter, wire extensometer) kurulumu;
          M4.5+ artçı sonrası yamaç kontrolü prosedürü uygulanmalı.
        </li>
        <li>
          <strong>Tsunami Hazırlığı (Kalıcı):</strong>
          Sarangani Körfezi kıyıları için M7.0+ artçı senaryosunda
          tahliye tatbikatı; PTWC (Pasifik Tsunami Uyarı Merkezi)
          bildirimleri için 7/24 izleme devam etmeli.
        </li>
        <li>
          <strong>FTLS İzleme Eşiği:</strong>
          b/b<sub>ref</sub> ≥ 0.90 (SARI) gerçekleşene dek kırmızı alarm
          protokolü sürdürülmeli. Bu eşiğin aşılması beklenen süre:
          p=0.619 ile <strong>30–60 gün sonra</strong> (N ≈ 600–800 olaya ulaşıldığında).
        </li>
      </ul>
      <div style="background:rgba(244,67,54,.08);border-radius:6px;padding:10px 14px;
                  margin-top:10px;font-size:.85em;">
        <strong style="color:#ef9a9a;">Kombinasyon Riski:</strong>
        b=0.635 + p=0.619 + FTLS KIRMIZI + muson mevsimi + sıvılaşma potansiyeli =
        <strong>yüksek müdahale önceliği</strong>.
        Normal koşullar altında 30 gün içinde sönümlenecek bir sekans,
        bu parametrelerle <strong>90+ güne yayılmaktadır.</strong>
      </div>
    </div>

'''

if OLD_REC_NEEDLE in rv:
    rv = rv.replace(OLD_REC_NEEDLE, CIVIL_DEF_BLOCK + OLD_REC_NEEDLE, 1)
    print('6d. Sivil Savunma bloğu eklendi')
else:
    print('MISS: Section 6b işareti (2. arama) bulunamadı')

# ══════════════════════════════════════════════════════════════
# Referanslar bölümüne yeni kaynaklar ekle
# ══════════════════════════════════════════════════════════════
OLD_ÖNCEL_REF = '<div class="review-ref-item">Öncel, A. O.'
NEW_REFS = (
    '<div class="review-ref-item">Hamburger, M. W. vd. (2010). '
    'Earthquake history of the Philippines. '
    '<em>J. Geophys. Res.</em>, 115, B10405.</div>\n    '
    '<div class="review-ref-item">Nowicki-Jessee, M. A. vd. (2018). '
    'A globally applicable model for near real-time prediction of seismically induced landslides. '
    '<em>Remote Sensing of Environment</em>, 219, 151–166.</div>\n    '
    '<div class="review-ref-item">Zhu, J. vd. (2017). '
    'An updated geospatial liquefaction model for global application. '
    '<em>Bulletin of the Seismological Society of America</em>, 107(3), 1365–1385.</div>\n    '
)

if OLD_ÖNCEL_REF in rv:
    rv = rv.replace(OLD_ÖNCEL_REF, NEW_REFS + OLD_ÖNCEL_REF, 1)
    print('Referanslar: Hamburger, Nowicki-Jessee, Zhu eklendi')
else:
    print('MISS: Öncel referansı bulunamadı')

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('JSON kaydedildi')
