import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('SeismoReport-Analiz-PDF-WORD.txt', encoding='utf-8') as f:
    txt = f.read()

OLD = ('║  ADIM 9: Post olustur (istege bagli) ────────────────────────  ║\n'
       '║  page-to-post-template.txt kullan.                                   ║\n'
       "║  OUTPUT/aftershock_map_snippet.html icerigini post'a ekle.            ║\n"
       '║  (Tam Rapor linkinden once)                                           ║\n'
       '║                                                                      ║\n'
       '║  Dosya konumları:')

NEW = ('║  ADIM 9: Post olustur (istege bagli) ────────────────────────  ║\n'
       '║  page-to-post-template.txt kullan.                                   ║\n'
       "║  OUTPUT/aftershock_map_snippet.html icerigini post'a ekle.            ║\n"
       '║  (Tam Rapor linkinden once)                                           ║\n'
       '║                                                                      ║\n'
       '║  ── ADIM 10: Otomatik artci takibi (aftershock_update.py) ───────  ║\n'
       '║  Yeni deprem icin aftershock_update.py dosyasini kopyala ve        ║\n'
       '║  CFG sozlugundeki su alanlari guncelle:                             ║\n'
       '║    start    → ana deprem UTC zamani (YYYY-MM-DDTHH:MM:SS)          ║\n'
       '║    lat/lon  → ana deprem koordinati                                 ║\n'
       '║    json     → INPUT/[DepremAdi].json                                ║\n'
       '║    page_html → OUTPUT/SEISMO/[FILENAME].html                        ║\n'
       '║    post_html → OUTPUT/POSTS/[FILENAME]-Post.html                    ║\n'
       '║                                                                      ║\n'
       '║  Komutlar (CMD veya bat dosyasindan):                               ║\n'
       '║    python aftershock_update.py aftershock-update                    ║\n'
       '║      → EMSC FDSN API sorgusu → ham veriyi guncelle (deduplikasyon) ║\n'
       '║      → parse_aftershocks.py calistir                                ║\n'
       '║      → JSON icinde AFTERSHOCK_MAP_JS + OMORI_CHART_JS guncelle     ║\n'
       '║      → generate.py ile HTML uret                                    ║\n'
       '║    python aftershock_update.py page-update                          ║\n'
       '║      → Sadece generate.py (veri degismeden HTML yenile)             ║\n'
       '║    python aftershock_update.py post-update                          ║\n'
       '║      → Snippet ile POST dosyasini guncelle                          ║\n'
       '║    python aftershock_update.py status                               ║\n'
       '║      → Kac artci, en buyuk, son guncelleme zamani                   ║\n'
       '║                                                                      ║\n'
       '║  Gunluk otomatik calisma (Windows Gorev Zamanlayici):               ║\n'
       '║    aftershock-update.bat dosyasini zamanlayiciya ekle               ║\n'
       '║    PowerShell komutu:                                                ║\n'
       "║    $a = New-ScheduledTaskAction -Execute 'cmd.exe'                  ║\n"
       "║         -Argument '/c aftershock-update.bat >> logs\\update.log'    ║\n"
       "║    $t = New-ScheduledTaskTrigger -Daily -At '09:00AM'               ║\n"
       '║    Register-ScheduledTask -TaskName "AfterShock-Update"             ║\n'
       '║      -Action $a -Trigger $t -Settings                               ║\n'
       '║      (New-ScheduledTaskSettingsSet -StartWhenAvailable)             ║\n'
       '║                                                                      ║\n'
       '║  Log dosyasi: logs/aftershock-update.log (her calistirmada eklenir) ║\n'
       '║  Bag dosyalar: aftershock_update.py, aftershock-update.bat,         ║\n'
       '║                page-update.bat, post-update.bat                     ║\n'
       '║                                                                      ║\n'
       '║  Dosya konumları:║  Dosya konumları:')

if OLD in txt:
    txt = txt.replace(OLD, NEW, 1)
    with open('SeismoReport-Analiz-PDF-WORD.txt', 'w', encoding='utf-8') as f:
        f.write(txt)
    print('Sablon guncellendi: ADIM 10 eklendi')
else:
    print('HATA: OLD metin bulunamadi')
    idx = txt.find('ADIM 9')
    print(repr(txt[idx:idx+300]))
