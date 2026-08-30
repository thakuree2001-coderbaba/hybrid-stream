import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__, static_folder='public', static_url_path='')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://luciferdonghua.in/"
}

# Base Layout Template
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title if title else 'Lucifer Donghua' }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: #0d0e12; color: #eceff4; font-family: sans-serif; }
        header { background: #151821; border-bottom: 2px solid #e50914; padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 1000; }
        .logo { font-size: 22px; font-weight: 800; color: #fff; text-decoration: none; }
        .logo span { color: #e50914; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 15px; }
        .player-wrapper { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 6px; overflow: hidden; margin-bottom: 20px; border: 1px solid #222634; }
        iframe { width: 100%; height: 100%; border: 0; }
        .episodes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 10px; margin: 20px 0; }
        .ep-btn { background: #1f2330; color: #fff; text-align: center; padding: 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 14px; border: 1px solid #2a2f42; }
        .ep-btn:hover, .ep-btn.active { background: #e50914; border-color: #e50914; }
        .section-title { font-size: 18px; font-weight: 700; margin: 20px 0 15px; border-left: 4px solid #e50914; padding-left: 10px; text-transform: uppercase; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 16px; }
        .card { background: #151821; border-radius: 6px; overflow: hidden; text-decoration: none; border: 1px solid #1e2230; display: block; }
        .card img { width: 100%; height: 230px; object-fit: cover; display: block; }
        .card-body { padding: 10px; }
        .card-title { font-size: 13px; font-weight: 600; color: #fff; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; height: 36px; }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">LUCIFER <span>DONGHUA</span></a>
    </header>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    url = "https://luciferdonghua.in/"
    cards_html = ""
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
                
                cards_html += f'''
                <a href="/watch?url={target_url}" class="card">
                    <img src="{poster}" alt="{title}" onerror="this.src='https://via.placeholder.com/200x300?text=No+Cover'">
                    <div class="card-body">
                        <div class="card-title">{title}</div>
                    </div>
                </a>
                '''
    except Exception as e:
        cards_html = f"<p>Error loading catalog: {e}</p>"

    page_content = f'''
        <div class="section-title">Latest Released Episodes</div>
        <div class="grid">{cards_html}</div>
    '''
    return render_template_string(HTML_LAYOUT, title="Lucifer Donghua - Home", content=page_content)

@app.route('/watch')
def watch_page():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing URL", 400
        
    embed_src = ""
    title = "Watch Donghua"
    episodes_html = ""
    
    try:
        res = requests.get(target_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title_tag = soup.find('h1')
        if title_tag:
            title = title_tag.get_text(strip=True)
            
        iframe = soup.find('iframe')
        if iframe and iframe.get('src'):
            embed_src = iframe.get('src')
            if embed_src.startswith('//'):
                embed_src = 'https:' + embed_src

        # Find episode links inside post
        ep_links = soup.find_all('a', href=re.compile(r'/episode-|/ep-|\d+'))
        for idx, ep in enumerate(ep_links[:50]):
            ep_url = ep.get('href')
            ep_name = ep.get_text(strip=True) or f"EP {idx+1}"
            if ep_url:
                episodes_html += f'<a href="/watch?url={ep_url}" class="ep-btn">{ep_name}</a>'

    except Exception as e:
        print("Page parse error:", e)

    page_content = f'''
        <h2 style="margin-bottom: 15px; font-size: 20px;">{title}</h2>
        <div class="player-wrapper">
            <iframe src="{embed_src}" allowfullscreen allow="autoplay; encrypted-media"></iframe>
        </div>
        <div class="section-title">Available Episodes</div>
        <div class="episodes-grid">{episodes_html if episodes_html else '<p>Direct video stream loaded above.</p>'}</div>
    '''
    return render_template_string(HTML_LAYOUT, title=title, content=page_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
