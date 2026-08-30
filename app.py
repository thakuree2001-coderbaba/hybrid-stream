import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request

app = Flask(__name__, static_folder='public', static_url_path='')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://luciferdonghua.in/"
}

@app.route('/')
def index():
    if os.path.exists('public/index.html'):
        with open('public/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    return "index.html missing", 404

@app.route('/api/latest')
def get_latest():
    url = "https://luciferdonghua.in/"
    items = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for article in soup.find_all('article'):
            link_tag = article.find('a')
            img_tag = article.find('img')
            title_tag = article.find('h2') or article.find('h3') or link_tag
            
            if link_tag and title_tag:
                title = title_tag.get_text(strip=True)
                target_url = link_tag.get('href', '')
                
                poster = ""
                if img_tag:
                    poster = img_tag.get('data-src') or img_tag.get('src') or img_tag.get('data-lazy-src') or ""
                
                items.append({
                    "title": title,
                    "url": target_url,
                    "poster": poster
                })
    except Exception as e:
        print("Backend Fetch Error:", e)
        
    return jsonify(items)

@app.route('/api/resolve')
def resolve_stream():
    page_url = request.args.get('url')
    if not page_url:
        return jsonify({"stream": ""})
    
    try:
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Search for video player iframes or embedded player sources
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if src and ('player' in src or 'embed' in src or 'dood' in src or 'stream' in src or 'vk' in src):
                if src.startswith('//'):
                    src = 'https:' + src
                return jsonify({"stream": src})
        
        # Regex search for video sources in scripts if iframe is dynamically rendered
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                match = re.search(r'https?://[^\s"\'<>]+(?:\.m3u8|\.mp4)', script.string)
                if match:
                    return jsonify({"stream": match.group(0)})

        if iframes and iframes[0].get('src'):
            src = iframes[0].get('src')
            if src.startswith('//'):
                src = 'https:' + src
            return jsonify({"stream": src})

    except Exception as e:
        print("Resolver error:", e)
        
    return jsonify({"stream": page_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
