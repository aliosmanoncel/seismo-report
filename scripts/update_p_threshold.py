import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('INPUT/Mindanao-2026.json', encoding='utf-8') as f:
    d = json.load(f)
rv = d['REVIEW_SECTION_HTML']

# ── 1. Tablo guncelle: 3 satir → 4 satir (< 0.7 esigi + Mindanao ayri) ──
OLD_TABLE = (
    '            <tr style="color:#81c784;"><td style="padding:4px 10px;">Hızlı sönümlenme</td>'
    '<td style="text-align:center;">≥ 1.0</td>'
    '<td style="padding:4px 10px;">Frekans hızla düşer; sistem kısa sürede kapanır</td></tr>\n'
    '            <tr style="color:#ffb74d;"><td style="padding:4px 10px;">Orta sönümlenme</td>'
    '<td style="text-align:center;">0.7–1.0</td>'
    '<td style="padding:4px 10px;">Haftalarca süren aktivite; dikkatli izleme gerekir</td></tr>\n'
    '            <tr style="color:#ef9a9a;font-weight:700;"><td style="padding:4px 10px;">⚠️ Mindanao 2026</td>'
    '<td style="text-align:center;">0.564</td>'
    '<td style="padding:4px 10px;">Yüksek kalıcılık; tehlike aylarca masada kalır</td></tr>'
)

NEW_TABLE = (
    '            <tr style="color:#81c784;"><td style="padding:4px 10px;">Hızlı sönümlenme</td>'
    '<td style="text-align:center;">≥ 1.0</td>'
    '<td style="padding:4px 10px;">Frekans hızla düşer; sistem kısa sürede kapanır</td></tr>\n'
    '            <tr style="color:#ffb74d;"><td style="padding:4px 10px;">Orta sönümlenme</td>'
    '<td style="text-align:center;">0.7–1.0</td>'
    '<td style="padding:4px 10px;">Haftalarca süren aktivite; dikkatli izleme gerekir</td></tr>\n'
    '            <tr style="color:#ef5350;font-weight:600;">'
    '<td style="padding:4px 10px;">Yavaş sönümlenme<br>'
    '<small style="font-weight:400;color:#ef9a9a;">Yüksek Sismik Kalıcılık</small></td>'
    '<td style="text-align:center;">&lt; 0.7</td>'
    '<td style="padding:4px 10px;">Enerji verimsiz ve zamana yayılarak boşalır; büyük artçı riski '
    'aylarca sürer; yapısal olarak yorulmuş binalar için uzun süreli tehlike penceresi</td></tr>\n'
    '            <tr style="background:rgba(244,67,54,.18);color:#ffcdd2;font-weight:700;">'
    '<td style="padding:5px 10px;">🔴 Mindanao 2026</td>'
    '<td style="text-align:center;">0.564</td>'
    '<td style="padding:5px 10px;">0.7 eşiğinin <strong>belirgin biçimde altında</strong> — '
    'Yüksek Kalıcılık kategorisi</td></tr>'
)

if OLD_TABLE in rv:
    rv = rv.replace(OLD_TABLE, NEW_TABLE, 1)
    print('Tablo guncellendi')
else:
    print('HATA: eski tablo bulunamadi')

# ── 2. Aciklama paragrafini guncelle (0.7 esigini one cikar) ──────
OLD_P = (
    'p</em> &lt; 1.0 durumu sismolojik açıdan olumsuz bir göstergedir: artçı\n'
    '          frekansı beklenen hızda azalmamakta, bölge <strong>aylarca aktif kalabilmektedir</strong>.\n'
    '          Fay üzerindeki gerilme transferi yavaş ve verimsiz gerçekleşmekte;\n'
    '          yapısal olarak zayıflamış yapılar için tehlike penceresi uzamaktadır.'
)

NEW_P = (
    'Sönümlenme hızı için kritik eşik <strong><em>p</em> = 0.7</strong>'
    "'dir. Bu değerin altı "
    '"Yüksek Sismik Kalıcılık" (High Persistence) olarak tanımlanır: '
    'artçı frekansı beklenen hızda azalmamakta, sismik enerji verimsiz ve zamana '
    'yayılarak boşalmaktadır. Mindanao 2026 için hesaplanan <strong>p = 0.564</strong>, '
    'bu eşiğin belirgin biçimde altında kalarak bölgenin '
    '<strong>aylarca aktif kalabileceğine</strong> işaret etmektedir. '
    'Yapısal olarak yorulmuş binalar için bu uzun süreli tehlike penceresi kritik önem taşımaktadır.'
)

if OLD_P in rv:
    rv = rv.replace(OLD_P, NEW_P, 1)
    print('Paragraf guncellendi')
else:
    print('HATA: eski paragraf bulunamadi — manuel kontrol:')
    idx = rv.find('p</em> &lt; 1.0 durumu')
    print(repr(rv[idx:idx+300]))

d['REVIEW_SECTION_HTML'] = rv
with open('INPUT/Mindanao-2026.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('Kaydedildi')
