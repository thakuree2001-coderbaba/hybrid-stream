import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template_string

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
    <title>{{ title }} - LUCIFER DONGHUA</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0c10;
            --card-bg: #12141c;
            --accent-red: #e50914;
            --text-color: #e0e0e0;
            --border-color: #1e2230;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); padding-bottom: 70px; }

        header { background: #0f111a; height: 55px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 15px; position: sticky; top: 0; z-index: 1000; }
        .logo { font-size: 18px; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 0.5px; }
        .logo span { color: var(--accent-red); }

        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; position: relative; }
        iframe { width: 100%; height: 100%; border: 0; }

        .banner-premium { background: linear-gradient(135deg, #1c0507 0%, #0d0e15 100%); border: 1px solid #3d0c10; margin: 10px; padding: 12px; border-radius: 8px; position: relative; }
        .banner-title { color: #fff; font-size: 13px; font-weight: bold; display: flex; align-items: center; gap: 6px; }
        .banner-title i { color: #ffb703; }
        .banner-sub { color: #888; font-size: 10px; margin: 4px 0 8px 0; }
        .badge-group { display: flex; gap: 6px; }
        .badge { background: rgba(229, 9, 20, 0.2); border: 1px solid var(--accent-red); color: #fff; font-size: 9px; padding: 3px 6px; border-radius: 4px; font-weight: bold; }

        .server-box { background: #0f111a; border: 1px solid var(--border-color); margin: 10px; padding: 12px; border-radius: 8px; }
        .server-title { font-size: 11px; color: #888; text-transform: uppercase; margin-bottom: 10px; font-weight: bold; letter-spacing: 0.5px; }
        .server-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .server-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: #bbb; padding: 10px; font-size: 11px; border-radius: 6px; text-align: center; cursor: pointer; text-decoration: none; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 600; }
        .server-btn.active { border-color: var(--accent-red); color: var(--accent-red); background: rgba(229, 9, 20, 0.1); }

        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 0 10px; }
        .card { background: var(--card-bg); border-radius: 6px; overflow: hidden; text-decoration: none; position: relative; display: block; border: 1px solid var(--border-color); }
        .card-img-wrap { position: relative; width: 100%; padding-top: 140%; }
        .card-img-wrap img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
        .card-badge { position: absolute; top: 4px; right: 4px; background: var(--accent-red); color: #fff; font-size: 9px; font-weight: bold; padding: 2px 4px; border-radius: 3px; }
        .card-title { font-size: 10px; font-weight: 600; color: #eee; padding: 6px 4px; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 30px; }

        .ep-list-container { padding: 0 10px; margin-top: 10px; }
        .ep-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; max-height: 380px; overflow-y: auto; padding-right: 2px; }
        .ep-btn { background: var(--card-bg); border: 1px solid var(--border-color); padding: 10px 4px; border-radius: 6px; text-align: center; text-decoration: none; display: block; color: var(--accent-red); font-size: 11px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .ep-btn.active-ep { border-color: var(--accent-red); background: rgba(229, 9, 20, 0.2); }

        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; height: 55px; background: #0f111a; border-top: 1px solid var(--border-color); display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #666; text-decoration: none; font-size: 10px; gap: 3px; }
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
        <a href="/" class="nav-item"><i class="fa-solid fa-film"></i>Anime</a>
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
                        <div class="card-badge">LD</div>
                    </div>
                    <div class="card-title">{t_text}</div>
                </a>
                '''
    except Exception as e:
        cards_html = f"<p style='padding:15px;'>Error: {e}</p>"

    content = f'<div class="grid-3" style="margin-top:10px;">{cards_html}</div>'
    return render_template_string(LAYOUT, title="Home", content=content)

@app.route('/watch')
def watch():
    target_url = request.args.get('url', '')
    title = "Watch Donghua"
    servers = []
    episodes = []

    if target_url:
        try:
            res = requests.get(target_url, headers=HEADERS, timeout=10)
            html_text = res.text
            soup = BeautifulSoup(html_text, 'html.parser')

            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)

            # 1. Filter out direct webpage links to prevent inside-player site loops
            raw_sources = re.findall(r'src=["\'](https?://[^"\']+|//[^"\']+)["\']', html_text)
            
            for src in raw_sources:
                if src.startswith('//'):
                    src = 'https:' + src
                
                is_valid_embed = any(domain in src for domain in ['rumble.com', 'dailymotion.com', 'ok.ru', 'vidhide', 'luluvdo'])
                is_lucifer_page = 'luciferdonghua.in' in src

                if is_valid_embed and not is_lucifer_page:
                    if not any(s['url'] == src for s in servers):
                        if 'rumble' in src: name = "Server 2 (Rumble 4K)"
                        elif 'dailymotion' in src: name = "Server 1 (Dailymotion)"
                        elif 'ok.ru' in src: name = "Server 3 (OK.ru)"
                        elif 'vidhide' in src: name = "Server 4 (VidHide)"
                        else: name = f"Server {len(servers)+1}"
                        
                        servers.append({"name": name, "url": src})

            # 2. Extract series container for full episode lists
            series_anchor = soup.find('a', href=re.compile(r'/anime/|/series/'))
            ep_target = series_anchor.get('href') if series_anchor else target_url
            
            ep_res = requests.get(ep_target, headers=HEADERS, timeout=10)
            ep_soup = BeautifulSoup(ep_res.text, 'html.parser')

            ep_container = ep_soup.find('div', class_=re.compile(r'eplister|episodes|eplist|bx', re.I)) or ep_soup
            for ep in ep_container.find_all('a', href=re.compile(r'luciferdonghua\.in/')):
                ep_href = ep.get('href', '')
                if re.search(r'episode-\d+|ep-\d+', ep_href, re.I):
                    ep_match = re.search(r'Episode\s*(\d+)|Ep\s*(\d+)', ep.get_text(), re.I)
                    if not ep_match:
                        ep_match = re.search(r'-episode-(\d+)', ep_href, re.I)
                    
                    num = ep_match.group(1) or ep_match.group(2) if ep_match else ""
                    display_name = f"Episode {num}" if num else "Episode"

                    if not any(e['href'] == ep_href for e in episodes):
                        episodes.append({"name": display_name, "href": ep_href})

        except Exception as e:
            print("Parsing error:", e)

    server_btns = ""
    for idx, srv in enumerate(servers):
        active_class = "active" if idx == 0 else ""
        server_btns += f'''
        <button class="server-btn {active_class}" onclick="setServer('{srv['url']}', this)">
            {srv['name']}
        </button>
        '''

    episodes_html = ""
    for ep in episodes:
        is_current = "active-ep" if ep['href'] == target_url else ""
        episodes_html += f'''
        <a href="/watch?url={ep['href']}" class="ep-btn {is_current}">{ep['name']}</a>
        '''

    # Auto-select first direct stream embed
    initial_stream = servers[0]['url'] if servers else ""

    content = f'''
        <div class="player-container">
            <iframe id="main-player" src="{initial_stream}" allowfullscreen allow="autoplay; encrypted-media"></iframe>
        </div>

        <div class="banner-premium">
            <div class="banner-title"><i class="fa-solid fa-crown"></i> Go Premium and Remove All Ads</div>
            <div class="banner-sub">No ads, faster player, full 4K access. Start from $1.19 per month.</div>
            <div class="badge-group">
                <span class="badge">✓ No ads</span>
                <span class="badge">✓ 4K Quality</span>
                <span class="badge">✓ High Speed Streaming</span>
            </div>
        </div>

        <div class="server-box">
            <div class="server-title">Select Video Server</div>
            <div class="server-grid">
                {server_btns if server_btns else "<p style='font-size:11px; color:#888;'>No clean embed links extracted.</p>"}
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
