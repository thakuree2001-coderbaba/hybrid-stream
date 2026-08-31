import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

BASE_URL = "https://luciferdonghua.in"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/"
}

def fetch_homepage_items():
    items = []
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        articles = soup.find_all('article')
        for art in articles:
            a_tag = art.find('a', href=True)
            img_tag = art.find('img')
            
            if a_tag:
                link = a_tag['href']
                title = a_tag.get('title') or a_tag.text.strip() or "Donghua Episode"
                img = img_tag.get('src') or img_tag.get('data-src') if img_tag else "https://via.placeholder.com/150x225?text=No+Cover"
                
                items.append({
                    "title": title,
                    "link": link,
                    "img": img
                })
    except Exception as e:
        print(f"Error scraping catalog: {e}")
    return items

def extract_stream_from_post(post_url):
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if 'facebook' not in src and 'google' not in src and 'nbl' not in src:
                return src if src.startswith('http') else f"https:{src}"
    except Exception as e:
        print(f"Error extracting video stream: {e}")
    return "about:blank"

@app.route('/')
def home():
    items = fetch_homepage_items()
    active_stream = extract_stream_from_post(items[0]['link']) if items else None
    return render_template('index.html', items=items, active_stream=active_stream)

@app.route('/watch')
def watch():
    target_url = request.args.get('url')
    items = fetch_homepage_items()
    active_stream = extract_stream_from_post(target_url) if target_url else None
    return render_template('index.html', items=items, active_stream=active_stream)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
