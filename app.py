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

def scrape_grid(url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for art in soup.find_all('article'):
            a_tag = art.find('a', href=True)
            img_tag = art.find('img')
            if a_tag:
                items.append({
                    "title": a_tag.get('title') or a_tag.text.strip() or "Donghua Episode",
                    "link": a_tag['href'],
                    "img": img_tag.get('src') or img_tag.get('data-src') if img_tag else "https://via.placeholder.com/150x225?text=No+Cover"
                })
    except Exception as e:
        print(f"Scraper Error: {e}")
    return items

def extract_stream(post_url):
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if 'facebook' not in src and 'google' not in src and 'nbl' not in src:
                return src if src.startswith('http') else f"https:{src}"
    except Exception as e:
        print(f"Stream Error: {e}")
    return "about:blank"

@app.route('/')
def home():
    items = scrape_grid(BASE_URL)
    return render_template('index.html', items=items)

@app.route('/catalog')
def catalog():
    items = scrape_grid(BASE_URL)
    return render_template('catalog.html', items=items)

@app.route('/watch')
def watch():
    target_url = request.args.get('url', '')
    stream_url = extract_stream(target_url) if target_url else "about:blank"
    return render_template('watch.html', stream_url=stream_url)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    search_url = f"{BASE_URL}/?s={query}" if query else BASE_URL
    items = scrape_grid(search_url)
    return render_template('catalog.html', items=items, query=query)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
