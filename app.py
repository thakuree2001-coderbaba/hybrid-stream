import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request

app = Flask(__name__)

BASE_URL = "https://luciferdonghua.in"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/"
}

LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUCIFER DONGHUA</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #08090d; color: #fff; font-family: system-ui, sans-serif; padding-bottom: 50px; }
        header { background: #0e1017; padding: 15px; border-bottom: 1px solid #202431; text-align: center; }
        .logo { font-weight: 900; color: #fff; text-decoration: none; font-size: 1.3rem; }
        .logo span { color: #e50914; }
        
        .container { padding: 15px; }
        .player-wrapper { width: 100%; aspect-ratio: 16/9; background: #000; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }
        iframe { width: 100%; height: 100%; border: none; }
        
        .section-title { font-size: 1.1rem; margin-bottom: 12px; color: #e50914; text-transform: uppercase; letter-spacing: 1px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 12px; }
        .card { background: #12151e; border: 1px solid #202431; border-radius: 6px; overflow: hidden; text-decoration: none; color: #fff; display: flex; flex-direction: column; }
        .card img { width: 100%; aspect-ratio: 2/3; object-fit: cover; }
        .card-title { padding: 8px; font-size: 0.8rem; line-height: 1.2; text-align: center; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">LUCIFER <span>DONGHUA</span></a>
    </header>

    <div class="container">
        {% if active_stream %}
        <div class="player-wrapper">
            <iframe src="{{ active_stream }}" allowfullscreen referrerpolicy="no-referrer"></iframe>
        </div>
        {% endif %}

        <div class="section-title">Latest Donghua Episodes</div>
        <div class="grid">
            {% for item in items %}
            <a href="/watch?url={{ item.link }}" class="card">
                <img src="{{ item.img }}" alt="{{ item.title }}" loading="lazy">
                <div class="card-title">{{ item.title }}</div>
            </a>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

def fetch_homepage_items():
    items = []
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Scrape post articles from WordPress target theme
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
        
        # Look for video iframe inside the episode page
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
    active_stream = None
    if items:
        # Default player to first episode in catalog
        active_stream = extract_stream_from_post(items[0]['link'])
    return render_template_string(LAYOUT, items=items, active_stream=active_stream)

@app.route('/watch')
def watch():
    target_url = request.args.get('url')
    items = fetch_homepage_items()
    active_stream = extract_stream_from_post(target_url) if target_url else None
    return render_template_string(LAYOUT, items=items, active_stream=active_stream)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
