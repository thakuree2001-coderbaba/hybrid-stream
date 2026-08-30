import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__, static_folder='public', static_url_path='')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://luciferdonghua.in/"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - AniLucifer VIP</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
        body { background-color: #0b0c10; color: #c5c6c7; min-height: 100vh; }
        
        header { background: #1f2833; border-bottom: 2px solid #66fcf1; padding: 15px 5%; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .logo { font-size: 24px; font-weight: 800; color: #fff; text-decoration: none; letter-spacing: 1px; }
        .logo span { color: #66fcf1; }
        
        .search-box { display: flex; background: #0b0c10; border-radius: 20px; border: 1px solid #45a29e; overflow: hidden; padding: 2px 10px; }
        .search-box input { background: transparent; border: none; outline: none; color: #fff; padding: 6px 10px; font-size: 13px; width: 140px; }
        .search-box button { background: none; border: none; color: #66fcf1; cursor: pointer; font-weight: bold; }

        .container { max-width: 1200px; margin: 25px auto; padding: 0 20px; }
        
        .player-card { background: #1f2833; border-radius: 12px; overflow: hidden; border: 1px solid #45a29e; box-shadow: 0 8px 30px rgba(102, 252, 241, 0.1); margin-bottom: 25px; }
        .player-wrapper { width: 100%; aspect-ratio: 16/9; background: #000; position: relative; }
        iframe { width: 100%; height: 100%; border: 0; }
        
        .server-bar { display: flex; gap: 10px; padding: 12px; background: #111; overflow-x: auto; border-top: 1px solid #333; }
        .server-btn { background: #1f2833; color: #66fcf1; border: 1px solid #45a29e; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: 0.3s; }
        .server-btn.active, .server-btn:hover { background: #66fcf1; color: #0b0c10; }

        .section-title { font-size: 18px; font-weight: 700; color: #fff; margin: 25px 0 15px; border-left: 4px solid #66fcf1; padding-left: 10px; text-transform: uppercase; }
        
        .episodes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 10px; margin-bottom: 30px; }
        .ep-btn { background: #1f2833; color: #fff; text-align: center; padding: 10px 5px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px; border: 1px solid #2c3540; transition: 0.2s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .ep-btn:hover, .ep-btn.active { background: #66fcf1; color: #0b0c10; border-color: #66fcf1; font-weight: 700; }

        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 18px; }
        .card { background: #1f2833; border-radius: 10px; overflow: hidden; text-decoration: none; border: 1px solid #2c3540; transition: transform 0.3s, box-shadow 0.3s; display: block; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(102, 252, 241, 0.2); border-color: #66fcf1; }
        .card img { width: 100%; height: 230px; object-fit: cover; display: block; }
        .card-body { padding: 12px; }
        .card-title { font-size: 13px; font-weight: 600; color: #fff; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; height: 38px; }

        @media (max-width: 600px) {
            .grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
            .card img { height: 190px; }
            .search-box input { width: 90px; }
        }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">ANI<span>LUCIFER</span></a>
        <form action="/search" method="GET" class="search-box">
            <input type="text" name="q" placeholder="Search..." required>
            <button type="submit">🔍</button>
        </form>
    </header>
    <div class="container">
        {{ content | safe }}
    </div>
    <script>
        function switchServer(url, btn) {
            document.getElementById('video-frame').src = url;
            document.querySelectorAll('.server-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
    </script>
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
        cards_html = f"<p>Error loading content: {e}</p>"

    content = f'''
        <div class="section-title">Latest Released Episodes</div>
        <div class="grid">{cards_html}</div>
    '''
    return render_template_string(HTML_TEMPLATE, title="Home", content=content)

@app.route('/watch')
def watch_page():
    target_url = request.args.get('url')
    if not target_url:
        return "Missing URL parameter", 400
        
    title = "Watch Donghua"
    servers = []
    episodes = []
    
    try:
        res = requests.get(target_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title_tag = soup.find('h1')
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract all iframes and video player options
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                servers.append(src)

        # Regex search for alternate embeds in scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                matches = re.findall(r'https?://[^\s"\'<>]+(?:embed|player|dood|filelions|streamwish)[^\s"\'<>]*', script.string)
                for m in matches:
                    if m not in servers:
                        servers.append(m)

        # Extract Episode navigation links accurately
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if ('luciferdonghua.in' in href or href.startswith('/')) and ('episode' in href or 'ep-' in href or re.search(r'-\d+/$', href)):
                if text and len(text) < 20 and href not in [e['url'] for e in episodes]:
                    episodes.append({"title": text, "url": href})

    except Exception as e:
        print("Watch parse error:", e)

    # Server buttons builder
    server_buttons = ""
    default_stream = servers[0] if servers else target_url
    for idx, s in enumerate(servers):
        active = "active" if idx == 0 else ""
        server_buttons += f'<button class="server-btn {active}" onclick="switchServer(\'{s}\', this)">Server {idx+1}</button>'

    # Episode buttons builder
    episodes_html = ""
    for ep in episodes:
        episodes_html += f'<a href="/watch?url={ep["url"]}" class="ep-btn">{ep["title"]}</a>'

    content = f'''
        <h2 style="margin-bottom: 15px; font-size: 20px; color:#fff;">{title}</h2>
        <div class="player-card">
            <div class="player-wrapper">
                <iframe id="video-frame" src="{default_stream}" allowfullscreen allow="autoplay; encrypted-media"></iframe>
            </div>
            <div class="server-bar">
                <span style="font-size:12px; font-weight:bold; color:#fff; align-self:center; margin-right:5px;">SERVERS:</span>
                {server_buttons if server_buttons else '<button class="server-btn active">Default Proxy</button>'}
            </div>
        </div>
        
        <div class="section-title">Episode Select</div>
        <div class="episodes-grid">
            {episodes_html if episodes_html else '<p style="color:#aaa;">Streaming source playing above. Select other series below.</p>'}
        </div>
    '''
    return render_template_string(HTML_TEMPLATE, title=title, content=content)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    url = f"https://luciferdonghua.in/?s={query}"
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
        cards_html = f"<p>Search error: {e}</p>"

    content = f'''
        <div class="section-title">Search Results for: "{query}"</div>
        <div class="grid">{cards_html if cards_html else '<p>No series found.</p>'}</div>
    '''
    return render_template_string(HTML_TEMPLATE, title=f"Search: {query}", content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
