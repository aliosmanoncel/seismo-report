# -*- coding: utf-8 -*-
"""
Blogger PAGE ve POST içeriğini günceller.
Kullanım:
  python scripts/blogger_update.py                        # JSON'daki aktif event
  python scripts/blogger_update.py events/Mindanao-2026/Mindanao-2026.json
Env vars: BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN
"""
import os, json, urllib.parse, urllib.request, sys, glob

BLOG_ID = "4033408817556081896"

CLIENT_ID     = os.environ.get("BLOGGER_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("BLOGGER_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("BLOGGER_REFRESH_TOKEN", "")

def get_access_token():
    if not CLIENT_ID:
        print("HATA: BLOGGER_CLIENT_ID env var eksik")
        sys.exit(1)
    data = urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type":    "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    resp = json.loads(urllib.request.urlopen(req).read())
    token = resp.get("access_token")
    if not token:
        print("HATA: access_token alinamadi:", resp)
        sys.exit(1)
    print("[+] Access token alindi")
    return token

def api_put(url, token, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        print(f"HATA PUT {url}: {e.code} {e.reason}")
        print(e.read().decode())
        sys.exit(1)

def find_json_files():
    """events/ altındaki tüm JSON dosyalarını döndürür."""
    return sorted(glob.glob("events/**/*.json", recursive=True))

def update_event(json_path, token):
    with open(json_path, encoding="utf-8") as f:
        cfg = json.load(f)

    event_name = cfg.get("FILENAME", "").replace(".html", "")
    updated = False

    # PAGE güncelle
    page_id   = cfg.get("BLOGGER_PAGE_ID")
    page_file = cfg.get("FILENAME")
    if page_id and page_file:
        path = f"OUTPUT/SEISMO/{page_file}"
        if os.path.exists(path):
            html = open(path, encoding="utf-8").read()
            api_put(
                f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/pages/{page_id}",
                token, {"id": page_id, "content": html}
            )
            print(f"[+] PAGE guncellendi: {event_name}")
            updated = True
        else:
            print(f"[!] PAGE dosyasi yok: {path}")

    # POST güncelle
    post_id   = cfg.get("BLOGGER_POST_ID")
    post_file = cfg.get("POST_FILENAME")
    if post_id and post_file:
        path = f"OUTPUT/POSTS/{post_file}.html"
        if os.path.exists(path):
            html = open(path, encoding="utf-8").read()
            api_put(
                f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}",
                token, {"id": post_id, "content": html}
            )
            print(f"[+] POST guncellendi: {event_name}")
            updated = True
        else:
            print(f"[!] POST dosyasi yok: {path}")

    if not updated:
        print(f"[!] {json_path}: BLOGGER_PAGE_ID veya BLOGGER_POST_ID eksik — atlandi")

def main():
    token = get_access_token()

    if len(sys.argv) > 1:
        # Belirli bir JSON dosyası
        update_event(sys.argv[1], token)
    else:
        # Tüm eventleri güncelle
        files = find_json_files()
        if not files:
            print("Hic JSON bulunamadi")
            sys.exit(0)
        for f in files:
            update_event(f, token)

    print("[+] Blogger guncelleme tamamlandi")

if __name__ == "__main__":
    main()
