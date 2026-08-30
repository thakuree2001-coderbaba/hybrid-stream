import os
import re
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__, static_folder='public', static_url_path='')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://luciferdonghua.in/"
}

LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{ title }} - Lucifer Donghua</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0c0d12;
            --card-bg: #151821;
            --accent-red: #e50914;
            --text-color: #e0e0e0;
            --border-color: #222634;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); padding-bottom: 70px; }

        header { background: #12141d; height: 55px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 15px; position: sticky; top: 0; z-index: 1000; }
        .logo { font-size: 18px; font-weight: 900; color: #fff; text-decoration: none; }
        .logo span { color: var(--accent-red); }

        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; position: relative; }
        iframe { width: 100%; height: 100%; border: 0; }

        .server-box { background: #12141d; border: 1px solid var(--border-color); margin: 12px; padding: 10px; border-radius: 6px; }
        .server-title { font-size: 11px; color: #888; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; }
        .server-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
        .server-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: #fff; padding: 10px 8px; font-size: 11px; border-radius: 4px; text-align: center; cursor: pointer; text-decoration: none; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .server-btn.active { border-color: var(--accent-red); color: var(--accent-red); font-weight: bold; }

        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 0 12px; }
        .card { background: var(--card-bg); border-radius: 6px; overflow: hidden; text-decoration: none; position: relative; display: block; border: 1px solid var(--border-color); }
        .card-img-wrap { position: relative; width: 100%; padding-top: 140%; }
        .card-img-wrap img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
        .card-title { font-size: 11px; font-weight: 600; color: #fff; padding: 6px 4px; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 32px; }

        .ep-list-container { padding: 0 12px; margin-bottom: 15px; }
        .ep-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; max-height: 250px; overflow-y: auto; }
        .ep-btn { background: var(--card-bg); border: 1px solid var(--border-color); padding: 8px 4px; border-radius: 4px; text-align: center; text-decoration: none; display: block; color: var(--accent-red); font-size: 11px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; height: 55px; background: #12141d; border-top: 1px solid var(--border-color); display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #777; text-decoration: none; font-size: 10px; gap: 3px; }
        .nav-item.active { color: var(--accent-red); }
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">LUCIFER <span>DONGHUA</span></a>
    </header>

    {{ content | safe }}

    <nav class="bottom-nav">
        <a href="/" class="nav-item active"><i class="fa-solid fa-house"></i>Home</a>
        <a href="/watch" class="nav-item"><i class="fa-solid fa-film"></i>Anime</a>
    </nav>

    <script>
        function setServer(url, btnElement) {
            const iframe = document.getElementById('main-player');
            if (iframe && url) {
                iframe.src = url;
            }
            document.querySelectorAll('.server-btn').forEach(b => b.classList.remove('active'));
            if (btnElement) btnElement.classList.add('active');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    cards_html = ""
    try:
        res = requests.get("https://luciferdonghua.in/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for article in soup.find_all('article'):
            link = article.find('a')
            img = article.find('img')
            title = article.find('h2') or article.find('h3') or link
            if link and title:
                t_text = title.get_text(strip=True)
                href = link.get('href', '')
                src = img.get('data-src') or img.get('src') or '' if img else ''
                cards_html += f'''
                <a href="/watch?url={href}" class="card">
                    <div class="card-img-wrap">
                        <img src="{src}">
                    </div>
                    <div class="card-title">{t_text}</div>
                </a>
                '''
    except Exception as e:
        cards_html = f"<p style='padding:15px;'>Error: {e}</p>"

    content = f'<div class="grid-3" style="margin-top:15px;">{cards_html}</div>'
    return render_template_string(LAYOUT, title="Home", content=content)

@app.route('/watch')
def watch():
    target_url = request.args.get('url', '')
    title = "Watch"
    servers = []
    episodes_html = ""

    if target_url:
        try:
            res = requests.get(target_url, headers=HEADERS, timeout=10)
            html_text = res.text
            soup = BeautifulSoup(html_text, 'html.parser')
            
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)

            # Extract iframe sources directly via Regex from embedded scripts/iframes
            raw_embeds = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html_text, re.IGNORECASE)
            
            # Clean duplicate and internal layout links
            for idx, embed in enumerate(raw_embeds):
                if embed.startswith('//'):
                    embed = 'https:' + embed
                if 'facebook' not in embed and 'twitter' not in embed and embed not in [s['url'] for s in servers]:
                    servers.append({
                        "name": f"Server {len(servers)+1}",
                        "url": embed
                    })

            # Extract episode list and scrub text
            for ep in soup.find_all('a', href=re.compile(r'luciferdonghua\.in/')):
                ep_href = ep.get('href')
                ep_text = ep.get_text(strip=True)
                
                # Match episode links specifically
                if re.search(r'episode-\d+|ep-\d+|\d+$', ep_href, re.IGNORECASE):
                    # Clean title formatting
                    clean_title = re.sub(r'4K|Watching|Aug\s*\d+,\s*\d+|Jul\s*\d+,\s*\d+', '', ep_text).strip()
                    if not clean_title:
                        clean_title = "Episode Stream"
                    episodes_html += f'''
                    <a href="/watch?url={ep_href}" class="ep-btn">{clean_title}</a>
                    '''

        except Exception as e:
            print("Error parsing target page:", e)

    server_btns = ""
    for idx, srv in enumerate(servers):
        active_class = "active" if idx == 0 else ""
        server_btns += f'''
        <button class="server-btn {active_class}" onclick="setServer('{srv['url']}', this)">
            {srv['name']}
        </button>
        '''

    initial_stream = servers[0]['url'] if servers else ""

    content = f'''
        <div class="player-container">
            <iframe id="main-player" src="{initial_stream}" allowfullscreen allow="autoplay; encrypted-media"></iframe>
        </div>

        <div class="server-box">
            <div class="server-title">Select Video Server</div>
            <div class="server-grid">
                {server_btns if server_btns else "<p style='font-size:11px; color:#888;'>No streams extracted for this episode. Try selecting another episode below.</p>"}
            </div>
        </div>

        <div class="ep-list-container">
            <div class="server-title">Episodes</div>
            <div class="ep-grid">{episodes_html}</div>
        </div>
    '''
    return render_template_string(LAYOUT, title=title, content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
