"""
SeismoReport Generator v4.0
Kullanim: python generate.py events/Mindanao-2026/Mindanao-2026.json
          python generate.py events/Cuba-2026/Cuba-2026.json
Cikti:    OUTPUT/SEISMO/<FILENAME>.html   (BASE_TEMPLATE: SeismoReport-Base.html)
          OUTPUT/POSTS/<POST_FILENAME>.html (BASE_TEMPLATE: SeismoReport-Post-Base.html)

JSON alanlari:
  BASE_TEMPLATE    : sablon dosyasi adi (varsayilan: SeismoReport-Base.html)
  POST_BASE_TEMPLATE: post sablon dosyasi (varsayilan: SeismoReport-Post-Base.html)
  FILENAME         : PAGE cikti dosyasi adi (uzantisiz)
  POST_FILENAME    : POST cikti dosyasi adi (uzantisiz); yoksa POST uretilmez
"""

import json
import re
import sys
import os

ROOT = os.path.dirname(__file__)

BASE_DIRS = {
    "SeismoReport-Base.html":      os.path.join(ROOT, "OUTPUT", "SEISMO"),
    "SeismoReport-Post-Base.html": os.path.join(ROOT, "OUTPUT", "POSTS"),
    "JeoTurizm-Base.html":         os.path.join(ROOT, "OUTPUT", "JEOTOUR"),
}

# JS kodu içeren alanlar — apostrop değiştirilmez (JS string sınırlayıcısı bozulur)
JS_CODE_KEYS = {"MAP_INIT_JS", "AFTERSHOCK_MAP_JS", "OMORI_CHART_JS",
                "REVIEW_SECTION_HTML", "APPENDIX_SECTIONS_HTML",
                "STAT_CARDS_HTML", "HERO_LINKS_HTML", "FOOTER_HTML",
                "POST_STAT_TABLE", "POST_STEPS_SECTION", "POST_BODY_SECTION", "POST_REFS",
                "GR_PLOT_BASE64", "HYPODD_PLOT_BASE64"}

def fill_template(base_file, data):
    with open(base_file, encoding="utf-8") as f:
        html = f.read()
    for key, value in data.items():
        raw = str(value)
        # Sadece kısa metin alanlarında Türkçe kesme işareti güvenli yapılır;
        # JS kodu veya büyük HTML bloklarında dokunulmaz
        if key not in JS_CODE_KEYS and len(raw) < 500:
            raw = raw.replace("’", "’")
        html = html.replace("{{" + key + "}}", raw)
    leftovers = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if leftovers:
        print(f"  UYARI: Doldurulamayan placeholder’lar: {set(leftovers)}")
    return html

FTLS_COLORS = {
    'KIRMIZI': {'bg': 'rgba(180,20,20,.85)', 'fg': '#fff', 'border': '#e53935'},
    'SARI':    {'bg': 'rgba(180,130,0,.85)', 'fg': '#fff', 'border': '#f9a825'},
    'YEŞİL':   {'bg': 'rgba(20,130,60,.85)', 'fg': '#fff', 'border': '#43a047'},
}

def enrich_ftls(data):
    """FTLS+ için hesaplanmış renk ve görüntüleme alanlarını ekle."""
    alarm = data.get('FTLS_ALARM', '')
    c = FTLS_COLORS.get(alarm, {'bg': 'rgba(40,60,80,.85)', 'fg': '#aaa', 'border': '#4a7a9b'})
    data.setdefault('FTLS_ALARM_BG',     c['bg'])
    data.setdefault('FTLS_ALARM_FG',     c['fg'])
    data.setdefault('FTLS_ALARM_BORDER', c['border'])
    # Kısa görüntüleme alanları — None → '—'
    for key in ('FTLS_R_B', 'FTLS_R_DS', 'FTLS_R_DT',
                'FTLS_B_REF', 'FTLS_B_AFTER',
                'FTLS_DS_PRE', 'FTLS_DS_POST',
                'FTLS_DT_PRE', 'FTLS_DT_POST',
                'FTLS_PRE_EVENTS', 'FTLS_POST_EVENTS',
                'FTLS_PHASE', 'FTLS_PRE_WINDOW', 'FTLS_ANALYSIS_DATE'):
        if data.get(key) is None:
            data[key] = '—'
    return data

def generate(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    data = enrich_ftls(data)

    # ── PAGE ────────────────────────────────────────────────────────────────
    base_name = data.get("BASE_TEMPLATE", "SeismoReport-Base.html")
    base_file = os.path.join(ROOT, base_name)
    if not os.path.exists(base_file):
        print(f"HATA: Sablon bulunamadi: {base_file}")
        sys.exit(1)

    html = fill_template(base_file, data)
    filename = data.get("FILENAME", "output").removesuffix(".html")
    out_dir = BASE_DIRS.get(base_name, os.path.join(ROOT, "OUTPUT"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename + ".html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"PAGE olusturuldu : {out_path}")

    # ── POST ────────────────────────────────────────────────────────────────
    post_filename = data.get("POST_FILENAME")
    if post_filename:
        post_base_name = data.get("POST_BASE_TEMPLATE", "SeismoReport-Post-Base.html")
        post_base_file = os.path.join(ROOT, post_base_name)
        if not os.path.exists(post_base_file):
            print(f"UYARI: POST sablon bulunamadi: {post_base_file}")
        else:
            post_html = fill_template(post_base_file, data)
            post_dir = BASE_DIRS.get(post_base_name, os.path.join(ROOT, "OUTPUT", "POSTS"))
            os.makedirs(post_dir, exist_ok=True)
            post_path = os.path.join(post_dir, post_filename + ".html")
            with open(post_path, "w", encoding="utf-8") as f:
                f.write(post_html)
            print(f"POST olusturuldu: {post_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanim: python generate.py INPUT/deprem.json")
        sys.exit(1)
    for path in sys.argv[1:]:
        generate(path)
