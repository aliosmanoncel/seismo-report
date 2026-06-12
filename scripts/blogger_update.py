# -*- coding: utf-8 -*-
"""
Blogger PAGE ve POST içeriğini GitHub Actions üzerinden günceller.
Gerekli env vars: BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, BLOGGER_REFRESH_TOKEN
"""
import os, json, urllib.parse, urllib.request, sys

BLOG_ID = "4033408817556081896"
PAGE_ID = "2105708432870999540"
POST_ID = "2692320355804154267"

CLIENT_ID     = os.environ["BLOGGER_CLIENT_ID"]
CLIENT_SECRET = os.environ["BLOGGER_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["BLOGGER_REFRESH_TOKEN"]

def get_access_token():
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

def api_request(method, url, token, body=None):
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HATA {method} {url}: {e.code} {e.reason}")
        print(e.read().decode())
        sys.exit(1)

def load_html(path):
    if not os.path.exists(path):
        print(f"UYARI: {path} bulunamadi, atlanıyor")
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()

def main():
    token = get_access_token()

    # PAGE güncelle
    page_html = load_html("OUTPUT/SEISMO/Mindanao-Mw78-SeismoNote.html")
    if page_html:
        api_request("PUT",
            f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/pages/{PAGE_ID}",
            token,
            {"id": PAGE_ID, "content": page_html}
        )
        print("[+] PAGE guncellendi")

    # POST güncelle
    post_html = load_html("OUTPUT/POSTS/Mindanao-Mw78-Post.html")
    if post_html:
        api_request("PUT",
            f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{POST_ID}",
            token,
            {"id": POST_ID, "content": post_html}
        )
        print("[+] POST guncellendi")

    print("[+] Blogger guncelleme tamamlandi")

if __name__ == "__main__":
    main()
