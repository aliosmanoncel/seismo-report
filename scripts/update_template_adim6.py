import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('SeismoReport-Analiz-PDF-WORD.txt', encoding='utf-8') as f:
    txt = f.read()

# ADIM 6 eski metni bul
OLD_MARKER = '║  ── ADIM 6: Post oluştur (isteğe bağlı) ──────────────────────────  ║'
END_MARKER  = '║  Dosya konumları:'

idx_start = txt.find(OLD_MARKER)
idx_end   = txt.find(END_MARKER)

if idx_start == -1 or idx_end == -1:
    print(f'Marker bulunamadi: start={idx_start}, end={idx_end}')
    # debug
    i = txt.find('ADIM 6')
    print(repr(txt[max(0,i-5):i+120]))
    sys.exit(1)

OLD_BLOCK = txt[idx_start:idx_end]

NEW_BLOCK = (
    '║  ── ADIM 6: USGS ShakeMap verilerini cek ─────────────────────  ║\n'
    '║  Neden? ShakeMap = alet tabanli zemin hareketi modeli.               ║\n'
    '║    DYFI vatandas bildirimiyle karsilastirmak icin gereklidir.        ║\n'
    '║                                                                      ║\n'
    '║  6a: USGS GeoJSON API ile ShakeMap zaman damgasini bul               ║\n'
    '║    URL: https://earthquake.usgs.gov/fdsnws/event/1/query              ║\n'
    '║          ?eventid=USGS_EVENT_ID&format=geojson                        ║\n'
    '║    products.shakemap[0].contents girdisinde cont_mmi.json url bilgisi ║\n'
    '║    bulunur. URL icerisinden timestamp kismini cikar.                  ║\n'
    '║    Temel URL: earthquake.usgs.gov/product/shakemap/                   ║\n'
    '║               EVENTID/NETID/TIMESTAMP/download/                       ║\n'
    '║                                                                      ║\n'
    '║  6b: Su dosyalari indir, INPUT/ klasorune kaydet:                    ║\n'
    '║    cont_mmi.json  → INPUT/shakemap_cont_mmi.json                    ║\n'
    '║      MMI izokonturlari (3.5-7.0). Leaflet polyline olarak haritada   ║\n'
    '║      gosterilir; DYFI CDI poligonlariyla kiyaslanir.                 ║\n'
    '║    cont_pga.json  → INPUT/shakemap_cont_pga.json                    ║\n'
    '║      Zemin ivmesi (%g); yapi hasari degerlendirilmesinde kullanilir.  ║\n'
    '║    rupture.json   → INPUT/shakemap_rupture.json                     ║\n'
    '║      Fay kirigi geometrisi. Artcilarin yonunu aciklar.               ║\n'
    '║      Haritada mor kalin cizgi; varsayilan acik katman.                ║\n'
    '║    stationlist.json → INPUT/shakemap_stationlist.json               ║\n'
    '║      Sismometre/DYFI noktalari + olcum degerleri.                    ║\n'
    '║      ShakeMap alet tabanini kanitlar. [STA] buton ile gosterilir.    ║\n'
    '║                                                                      ║\n'
    '║  6c: python parse_aftershocks.py — ShakeMap otomatik yuklenir:       ║\n'
    '║    INPUT/shakemap_*.json dosyalari okunur                             ║\n'
    '║    AFTERSHOCK_MAP_JS icine MMI/PGA/Rupture/STA katmanlari eklenir     ║\n'
    '║    Haritada yeni toggle: [MMI] [PGA] [STA]                            ║\n'
    '║    Fay kirigi varsayilan acik, digerleri toggle ile on/off            ║\n'
    '║                                                                      ║\n'
    '║  ── ADIM 7: USGS DYFI verisi ───────────────────────────────────  ║\n'
    '║  Neden? DYFI = vatandas aggregate bildirimleri (CDI degerleri).      ║\n'
    '║    ShakeMap alet modeliyle farki raporu zenginlestirir.              ║\n'
    '║                                                                      ║\n'
    '║  DYFI GeoJSON URL kalibi:                                            ║\n'
    '║    https://earthquake.usgs.gov/product/dyfi/EVENTID/NETID/           ║\n'
    '║      TIMESTAMP/dyfi_geo_10km.geojson                                 ║\n'
    '║    Timestamp: USGS event sayfasindan veya GeoJSON API ile bulunur.   ║\n'
    '║    INPUT/dyfi_geo_10km.geojson olarak kaydet.                        ║\n'
    '║    parse_aftershocks.py icindeki _DYFI_URL ile guncelle.             ║\n'
    '║    Haritada [DYFI] toggle; CDI renk skalali poligonlar.              ║\n'
    '║                                                                      ║\n'
    '║  ShakeMap / DYFI / EMSC felt — 3 farkli kaynak:                      ║\n'
    '║    ShakeMap  → teorik/alet bazli (sismometre + fizik modeli)         ║\n'
    '║    DYFI      → vatandas gozlemi, grid bazli aggregate (10km hucre)   ║\n'
    '║    EMSC felt → vatandas bireysel taniklık (konum + aciklama metni)   ║\n'
    '║    Ucü birlikte → dogrulama + insan boyutu saglar                    ║\n'
    '║                                                                      ║\n'
    '║  ── ADIM 8: EMSC tanikliklari (Appendix E) ───────────────────  ║\n'
    '║  Neden? EMSC = bireysel depremzede sesi; DYFI olmayan kisisel anlatı. ║\n'
    '║    "Massive lots damage", "couldn\'t stand up" vb. dogrudan alintilar. ║\n'
    '║                                                                      ║\n'
    '║  Taniklık URL kalibi:                                                ║\n'
    '║    https://www.emsc-csem.org/Earthquake_information/                  ║\n'
    '║      earthquake_testimonies.php?id=EMSC_EVENT_ID                     ║\n'
    '║    Sayfa metnini kopyala → build_testimonies.py RAW degiskenine yaz  ║\n'
    '║    python build_testimonies.py → INPUT/Mindanao-2026.json guncellenir ║\n'
    '║    Appendix E olarak eklenir; mesafeye gore renk kodlanmis tablo.    ║\n'
    '║                                                                      ║\n'
    '║  EMSC artci katalogu URL kalibi:                                     ║\n'
    '║    https://www.seismicportal.eu/fdsnws/event/1/query                  ║\n'
    '║      ?starttime=...&endtime=...&minlat=...&maxlat=...                ║\n'
    '║      &minlon=...&maxlon=...&minmag=3.0&format=text&limit=500          ║\n'
    '║    INPUT/[DepremAdi]_raw.txt olarak kaydet.                           ║\n'
    '║                                                                      ║\n'
    '║  ── ADIM 9: Post olustur (istege bagli) ────────────────────────  ║\n'
    '║  page-to-post-template.txt kullan.                                   ║\n'
    '║  OUTPUT/aftershock_map_snippet.html icerigini post\'a ekle.            ║\n'
    '║  (Tam Rapor linkinden once)                                           ║\n'
    '║                                                                      ║\n'
    '║  Dosya konumları:'
)

txt = txt.replace(OLD_BLOCK, NEW_BLOCK, 1)
with open('SeismoReport-Analiz-PDF-WORD.txt', 'w', encoding='utf-8') as f:
    f.write(txt)
print('Sablon guncellendi OK')
print(f'Eklenen satir sayisi: {NEW_BLOCK.count(chr(10))}')
