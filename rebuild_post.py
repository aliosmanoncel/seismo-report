# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', encoding='utf-8') as f:
    html = f.read()

# ── MAIN TEXT + CARDS + BOXES + Q&A + AHEAD → Mindanao ──────────────────────
idx_text_sec = html.find('<div class="ep-section">\U0001f52c Seismologist Perspective')
idx_export = html.find('<!-- DIŞA AKTARMA -->')

NEW_BULK = '''<div class="ep-section">\U0001f52c Sismolog Perspektifi: Tehlike Ne Boyutta?</div>

<p class="ep-p">Filipinler Takımadası, <strong class="ep-kw">Pasifik Levhası</strong>, Avustralya Levhası ve Güneydoğu Asya Levhasıʼnın karmaşık etkileşimleri sonucu küresel en aktif sismik bölgelerden biridir. Mindanao adası; Batı Mindanao Fay Zonu, Cotabato Çukuru ve Mindanao Hendek Zonu gibi yapısal unsurlarıyla son derece karmaşık bir sismotektonik ortam oluşturmaktadır.</p>

<div class="ep-quote">
  &ldquo;Earthquakes cause damage to many parts of the natural and built environment, with potentially widespread and devastating impacts. Since 1900, earthquakes have killed approximately 8.5 million people and caused $2 trillion of damage.&rdquo;
  <cite>&mdash; Baker, Bradley &amp; Stafford (2021, s. 1)</cite>
</div>

<p class="ep-p">Dört bağımsız ajansın (EMSC, USGS/NEIC, GFZ, GlobalCMT) moment tensör çözümleri, depremin <strong class="ep-kw">saf ters faylanma (megathrust)</strong> mekanizmasıyla gerçekleştiğini tutar lı biçimde doğrulamaktadır. Hipocenter derinliği 55.2 km, W-faz santroid derinliği 35.5 km; enerji geniş alana yayılmış, 2000 kmʼyi aşan mesafelerde hissedilmiştir.</p>

<div class="ep-think">
  <strong>FTLS Kırmızı Uyarı &mdash; Ne Anlama Gelir?</strong>
  b-değeri 0.635, Öncel &amp; Wilson (2007) FTLS metodolojisinde kırmızı eşiğin altında. Sismik çevrimde birikmekte olan gerilme, M6.0+ tetikleyici artçı olasılığını artırıyor. Düşük p=0.619 ile birlikte: zaten hasar lı yapılara yönelik 90 gün boyunca yüksek tetikte kalınması zorunlu.
</div>

<div class="ep-divider"></div>

<!-- KARTLAR -->
<div class="ep-section">\U0001f5fa️ Bilimsel Altyapı &mdash; 4 Temel Analiz</div>
<div class="ep-cards">
  <div class="ep-card">
    <div class="ep-icon">\U0001f30a</div>
    <h4>Tsunami Değerlendirmesi</h4>
    <p>Ters faylanma mekanizması tsunami potansiyeli taşısa da okyanus geneli yıkıcı risk düşük değerlendirildi. Cotabato ve Sarangani körfezi kıyıları için yerel risk uyarısı verildi.</p>
  </div>
  <div class="ep-card">
    <div class="ep-icon">\U0001f4ca</div>
    <h4>G-R b = 0.635</h4>
    <p>Gutenberg-Richter analizi (Mc=3.5, Aki 1965): tam aralık b=0.635 &mdash; FTLS kırmızı eşiğinin altında. İki-segment analiz M5.0ʼde eğim kırılması gösterdi (b₁=0.829, b₂=1.12).</p>
  </div>
  <div class="ep-card">
    <div class="ep-icon">\U0001f3d7️</div>
    <h4>Yapısal Risk %90+</h4>
    <p>PSHA medyan PGA=0.759g, Filipinler tasarım standardı 0.40gʼnin %90 üzerinde. 84. fraktil 1.140g &mdash; hasar lı yapılara yönelik M6.0+ artçı riski kritik.</p>
  </div>
  <div class="ep-card">
    <div class="ep-icon">\U0001f9e0</div>
    <h4>Omori-Utsu p = 0.619</h4>
    <p>Düşük p-değeri yüksek sismik kalıcılığı gösteriyor. 90 günlük beklenti: 2× M6.5+, 1× M7.0+. Hasar lı yapılar için ek artçı yükü önemli risk oluşturuyor.</p>
  </div>
</div>

<div class="ep-divider"></div>

<!-- BİLGİ KUTULARI -->
<div class="ep-box ep-box-red">
  <strong>\U0001f534 FTLS Kırmızı Uyarı &mdash; b=0.635:</strong> Gutenberg-Richter b-değeri FTLS eşiğinin altında. Öncel &amp; Wilson (2007) metodolojisine göre M6.0+ tetikleyici artçı olasılığı yüksek. Zaten hasar lı yapılar için ek yük kritik risk oluşturuyor.
  <div class="ep-tags" style="margin-top:12px;">
    <span class="ep-tag">\U0001f4c9 b=0.635</span>
    <span class="ep-tag">\U0001f534 Kırmızı Eşlik</span>
    <span class="ep-tag">⚡ M6.0+ Risk</span>
  </div>
</div>

<div class="ep-box ep-box-gold" style="margin-top:16px;">
  <strong>\U0001f511 PSHA Temel Bulgu:</strong> Logic Tree 27 dal hesaplaması (Baker 2021, Youngs 1988 GMPE) &mdash; General Santos City için medyan PGA=0.759g, 84. fraktil=1.140g. Filipinler ulusal tasarım standardı 0.40gʼnin %90 üzerinde.
</div>

<div class="ep-box ep-box-red" style="margin-top:16px;">
  <strong>⚠️ Sivil Savunma Tavsiyesi:</strong> Düşük p=0.619 + düşük b=0.635 kombinasyonu &mdash; hasar lı yapıların tahliyesi ve M6.0+ artçılar için 90 gün boyunca yüksek tetikte kalınması önerilmektedir.
</div>

<div class="ep-divider"></div>

'''

html = html[:idx_text_sec] + NEW_BULK + html[idx_export:]
print('bulk replaced')

# ── ABSTRACT variable ─────────────────────────────────────────────────────────
idx_ab = html.find("var ABSTRACT='")
end_ab = html.find("';", idx_ab) + 2
OLD_AB = html[idx_ab:end_ab]
NEW_AB = "var ABSTRACT='7 Haziran 2026 tarihinde 23:37 UTC de Mindanao açıklarında gerçekleşen Mw 7.8 depremi, ters faylanma mekanizması ve PSHA Logic Tree 27 dal hesaplamasıyla General Santos City için medyan PGA=0.759g değeri ortaya koymuştur — Filipinler tasarım standardının yüzde 90 üzerinde.';"
html = html[:idx_ab] + NEW_AB + html[end_ab:]
print('abstract replaced')

# ── CTA subtitle ─────────────────────────────────────────────────────────────
html = html.replace(
    'Haritalar · 17 Soru-Cevap · Beach Ball · Bilimsel Makaleler · Google Earth Sanal Tur · INGV/AHEAD Veri Linkleri · PDF/Word Export',
    'Artçı Dizi · FTLS b-Değeri · PSHA Logic Tree · ShakeMap · Moment Tensör · PDF/Word Export'
)
print('CTA subtitle done')

# ── YAZAR bio ─────────────────────────────────────────────────────────────────
html = html.replace(
    'Akdeniz tektoniği üzerine araştırmalar.',
    'subdüksiyon tektoniği üzerine araştırmalar.'
)

# ── FOOTER ───────────────────────────────────────────────────────────────────
html = html.replace(
    'Southern Italy Mw 6.2 Deep Earthquake · Haziran 2026',
    'Mindanao Mw 7.8 Büyük Deprem · Haziran 2026'
)

# ── KAYNAKÇA — update references ─────────────────────────────────────────────
idx_ref = html.find('<ol style="padding-left:1.4em;font-size:0.82rem')
idx_ref_end = html.find('</ol>', idx_ref) + 5
html = html[:idx_ref] + '''<ol style="padding-left:1.4em;font-size:0.82rem;line-height:1.75;color:var(--ep-muted);margin:0;">
    <li style="margin-bottom:6px;">Baker, J. W., Bradley, B. A., &amp; Stafford, P. J. (2021). <em>Seismic Hazard and Risk Analysis</em>. Cambridge University Press.</li>
    <li style="margin-bottom:6px;">Cardwell, R. K., Isacks, B. L., &amp; Karig, D. E. (1980). The spatial distribution of earthquakes in the Philippine islands. <em>Geophys. Monogr.</em>, 23, 1&ndash;35.</li>
    <li style="margin-bottom:6px;">Youngs, R. R., Chiou, S. J., Silva, W. J., &amp; Humphrey, J. R. (1988). Strong ground motion for subduction zone earthquakes. <em>Seism. Res. Lett.</em>, 68, 58&ndash;73.</li>
    <li style="margin-bottom:6px;">Öncel, A. O., &amp; Wilson, T. H. (2007). Anomalous seismicity preceding the 1999 Izmit earthquake, NW Turkey. <em>Geophys. J. Int.</em>, 169, 259&ndash;270.</li>
    <li style="margin-bottom:6px;">Aurelio, M. A. (2000). Shear partitioning in the Philippines. <em>Island Arc</em>, 9, 584&ndash;597.</li>
    <li style="margin-bottom:0;">Yumul, G. P. Jr. vd. (2008). Geological features of the Philippines. <em>Island Arc</em>, 17, 3&ndash;17.</li>
  </ol>''' + html[idx_ref_end:]
print('references replaced')

with open('OUTPUT/POSTS/Mindanao-Mw78-Post.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('DONE, length:', len(html))
