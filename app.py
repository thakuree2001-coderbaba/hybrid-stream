from flask import Flask, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__, static_folder='public', static_url_path='')

@app.route('/')
def index():
    if os.path.exists('public/index.html'):
        with open('public/index.html', 'r') as f:
            return f.read()
    return "Index page not found", 4404

@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    url = "https://luciferdonghua.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    catalog = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Select post cards on luciferdonghua.in
        articles = soup.find_all('article')
        for idx, article in enumerate(articles):
            title_tag = article.find('h2') or article.find('h3') or article.find('a')
            link_tag = article.find('a')
            img_tag = article.find('img')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                page_url = link_tag.get('href', '')
                
                # Extract image thumbnail URL
                poster = "https://via.placeholder.com/300x400"
                if img_tag:
                    poster = img_tag.get('data-src') or img_tag.get('src') or poster
                
                catalog.append({
                    "id": idx + 1,
                    "title": title,
                    "category": "Donghua",
                    "source_platform": "Lucifer Donghua",
                    "poster_url": poster,
                    "rating": "9.5",
                    "stream_url": page_url
                })
    except Exception as e:
        print("Scraping error:", e)
        
    return jsonify(catalog)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
