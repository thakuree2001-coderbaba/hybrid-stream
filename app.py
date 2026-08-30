import os
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

@app.route('/api/embed')
def get_embed():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"embed": ""})
        
    try:
        res = requests.get(target_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Look specifically for stream player containers or any embed iframe
        iframe = soup.find('iframe', id='option-1') or soup.find('iframe', class_='metaframe') or soup.find('iframe')
        
        if iframe and iframe.get('src'):
            src = iframe.get('src')
            if src.startswith('//'):
                src = 'https:' + src
            return jsonify({"embed": src})
            
        return jsonify({"embed": target_url})
    except Exception as e:
        return jsonify({"embed": target_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
