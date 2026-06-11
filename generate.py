"""
SeismoReport Generator v3.0
Kullanim: python generate.py events/Mindanao-2026/Mindanao-2026.json
          python generate.py events/Cuba-2026/Cuba-2026.json
Cikti:    OUTPUT/SEISMO/<FILENAME>.html

JSON icinde BASE_TEMPLATE alani ile sablon secilir:
  "BASE_TEMPLATE": "SeismoReport-Base.html"   (varsayilan)
"""

import json
import re
import sys
import os

ROOT = os.path.dirname(__file__)

BASE_DIRS = {
    "SeismoReport-Base.html": os.path.join(ROOT, "OUTPUT", "SEISMO"),
    "JeoTurizm-Base.html":    os.path.join(ROOT, "OUTPUT", "JEOTOUR"),
}

def generate(json_path):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    base_name = data.get("BASE_TEMPLATE", "SeismoReport-Base.html")
    base_file = os.path.join(ROOT, base_name)

    if not os.path.exists(base_file):
        print(f"HATA: Sablon bulunamadi: {base_file}")
        sys.exit(1)

    with open(base_file, encoding="utf-8") as f:
        html = f.read()

    for key, value in data.items():
        # Türkçe kesme işareti (U+2019) JS string'ini kırmaz; ASCII apostrofu (U+0027) kırar
        safe_value = str(value).replace("'", "’")
        html = html.replace("{{" + key + "}}", safe_value)

    leftovers = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if leftovers:
        print(f"UYARI: Doldurulamayan placeholder'lar: {set(leftovers)}")

    filename = data.get("FILENAME", "output")
    out_dir  = BASE_DIRS.get(base_name, os.path.join(ROOT, "OUTPUT"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename + ".html")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Olusturuldu: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanim: python generate.py INPUT/deprem.json")
        sys.exit(1)
    for path in sys.argv[1:]:
        generate(path)
