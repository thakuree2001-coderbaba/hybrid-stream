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

        header { background: #0f111a; height: 60px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 12px; position: sticky; top: 0; z-index: 1000; gap: 8px; }
        .logo { font-size: 16px; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 0.5px; flex-shrink: 0; }
        .logo span { color: var(--accent-red); }

        .search-form { display: flex; align-items: center; background: #1a1d29; border: 1px solid var(--border-color); border-radius: 20px; padding: 4px 10px; flex-grow: 1; max-width: 200px; }
        .search-form input { background: transparent; border: none; color: #fff; font-size: 12px; width: 100%; outline: none; }
        .search-form button { background: transparent; border: none; color: #888; cursor: pointer; font-size: 12px; }

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
        <form class="search-form" action="/search" method="get">
            <input type="text" name="q" placeholder="Search donghua..." required>
            <button type="submit"><i class="fa-solid fa-magnifying-glass"></i></button>
        </form>
    </header>

    {{ content | safe }}

    <nav class="bottom-nav">
        <a href="/" class="nav-item {{ 'active' if active_nav == 'home' else '' }}"><i class="fa-solid fa-house"></i>Home</a>
        <a href="/anime" class="nav-item {{ 'active' if active_nav == 'anime' else '' }}"><i class="fa-solid fa-film"></i>Anime List</a>
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

def parse_cards(soup):
    cards_html = ""
    for article in soup.find_all(['article', 'div'], class_=re.compile(r'bsx|item|article|post', re.I)):
        link = article.find('a')
        img = article.find('img')
        title = article.find(['h2', 'h3', 'h4']) or link
        if link and title:
            t_text = title.get_text(strip=True)
            href = link.get('href', '')
            src = img.get('data-src') or img.get('src') or '' if img else ''
            cards_html += f'''
            <a href="/watch?url={href}" class="card">
                <div class="card-img-wrap">
                    <img src="{src}" alt="{t_text}">
                    <div class="card-badge">HD</div>
                </div>
                <div class="card-title">{t_text}</div>
            </a>
            '''
    return cards_html

@app.route('/')
def index():
    try:
        res = requests.get("https://luciferdonghua.in/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards_html = parse_cards(soup)
    except Exception as e:
        cards_html = f"<p style='padding:15px; color:#888;'>Error loading content: {e}</p>"

    content = f'<div class="grid-3" style="margin-top:10px;">{cards_html}</div>'
    return render_template_string(LAYOUT, title="Home", content=content, active_nav="home")

@app.route('/anime')
def anime_list():
    try:
        res = requests.get("https://luciferdonghua.in/series/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards_html = parse_cards(soup)
    except Exception as e:
        cards_html = f"<p style='padding:15px; color:#888;'>Error loading series list: {e}</p>"

    content = f'<div class="grid-3" style="margin-top:10px;">{cards_html}</div>'
    return render_template_string(LAYOUT, title="Anime List", content=content, active_nav="anime")

@app.route('/search')
def search():
    query = request.args.get('q', '')
    cards_html = ""
    if query:
        try:
            search_url = f"https://luciferdonghua.in/?s={query}"
            res = requests.get(search_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            cards_html = parse_cards(soup)
        except Exception as e:
            cards_html = f"<p style='padding:15px; color:#888;'>Search failed: {e}</p>"

    if not cards_html:
        cards_html = "<p style='padding:15px; color:#888;'>No results found.</p>"

    content = f'<div style="padding:10px 10px 0 10px; font-size:12px; font-weight:bold;">Search results for: "{query}"</div><div class="grid-3" style="margin-top:10px;">{cards_html}</div>'
    return render_template_string(LAYOUT, title=f"Search: {query}", content=content, active_nav="")

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

            # 1. Regex search for embed providers
            matches = re.findall(r'(https?://[^\s"\'<>]+)', html_text)
            for raw in matches:
                url = raw.replace('\\/', '/').replace('&amp;', '&')
                if any(k in url for k in ['rumble.com/embed', 'dailymotion.com/embed', 'ok.ru/videoembed', 'vidhide', 'luluvdo', 'streamtape']):
                    if not any(s['url'] == url for s in servers):
                        name = "Server " + str(len(servers) + 1)
                        if 'rumble' in url: name = "Server 1 (Rumble)"
                        elif 'ok.ru' in url: name = "Server 2 (OK.ru)"
                        elif 'vidhide' in url: name = "Server 3 (VidHide)"
                        servers.append({"name": name, "url": url})

            # 2. Fallback: direct site stream frame if no third-party embeds are isolated
            if not servers:
                servers.append({"name": "Direct Web Player", "url": target_url})

            # 3. Extract all episodes
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
                {server_btns}
            </div>
        </div>

        <div class="ep-list-container">
            <div class="server-title">Episodes</div>
            <div class="ep-grid">{episodes_html}</div>
        </div>
    '''
    return render_template_string(LAYOUT, title=title, content=content, active_nav="")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
