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

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); padding-bottom: 70px; }

        /* Header */
        header { background: #12141d; height: 55px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 15px; position: sticky; top: 0; z-index: 1000; }
        .menu-btn { background: none; border: none; color: #fff; font-size: 20px; cursor: pointer; }
        .logo { font-size: 18px; font-weight: 900; color: #fff; text-decoration: none; letter-spacing: 0.5px; }
        .logo span { color: var(--accent-red); }
        .header-actions { display: flex; gap: 15px; align-items: center; }
        .login-btn { background: var(--accent-red); color: #fff; border: none; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; text-decoration: none; }

        /* Banner */
        .premium-box { background: linear-gradient(135deg, #1d080a 0%, #3a0d11 100%); border: 1px solid var(--accent-red); border-radius: 8px; margin: 12px 15px; padding: 12px; position: relative; }
        .premium-title { font-size: 14px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 6px; }
        .premium-sub { font-size: 11px; color: #aaa; margin: 4px 0 8px; }
        .premium-pills { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
        .pill { background: rgba(229, 9, 20, 0.2); color: #ff6b72; font-size: 10px; padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(229, 9, 20, 0.4); }
        .premium-btn { background: var(--accent-red); color: #fff; border: none; width: 100%; padding: 8px; border-radius: 4px; font-weight: bold; font-size: 12px; text-align: center; text-decoration: none; display: block; }

        /* Drawer */
        .drawer-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 2000; display: none; }
        .drawer { position: fixed; top: 0; left: -260px; width: 260px; height: 100%; background: #12141d; z-index: 2001; transition: left 0.3s ease; border-right: 1px solid var(--border-color); padding-top: 15px; }
        .drawer.open { left: 0; }
        .drawer-item { display: flex; align-items: center; gap: 12px; padding: 12px 20px; color: #ccc; text-decoration: none; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.03); }
        .drawer-item i { width: 20px; color: var(--accent-red); }

        /* Card Grid */
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding: 0 12px; }
        .card { background: var(--card-bg); border-radius: 6px; overflow: hidden; text-decoration: none; position: relative; display: block; border: 1px solid var(--border-color); }
        .card-img-wrap { position: relative; width: 100%; padding-top: 140%; }
        .card-img-wrap img { position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; }
        .badge-type { position: absolute; top: 4px; left: 4px; background: rgba(0,0,0,0.75); color: #ffb400; font-size: 8px; font-weight: 800; padding: 1px 4px; border-radius: 2px; }
        .badge-ep { position: absolute; bottom: 4px; left: 4px; background: var(--accent-red); color: #fff; font-size: 9px; font-weight: bold; padding: 1px 5px; border-radius: 2px; }
        .card-title { font-size: 11px; font-weight: 600; color: #fff; padding: 6px 4px; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 32px; }

        /* Player & Player Switcher */
        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; position: relative; }
        iframe { width: 100%; height: 100%; border: 0; }
        .server-box { background: #12141d; border: 1px solid var(--border-color); margin: 12px; padding: 10px; border-radius: 6px; }
        .server-title { font-size: 11px; color: #888; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; }
        .server-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
        .server-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: #fff; padding: 10px 8px; font-size: 11px; border-radius: 4px; text-align: center; cursor: pointer; text-decoration: none; display: block; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
        .server-btn.active { border-color: var(--accent-red); color: var(--accent-red); font-weight: bold; }

        .warning-box { background: rgba(229, 9, 20, 0.1); border: 1px solid var(--accent-red); border-radius: 6px; padding: 10px; margin: 12px; font-size: 11px; color: #ddd; line-height: 1.4; }
        .warning-box i { color: #ffb400; margin-right: 4px; }

        .details-container { padding: 12px; background: #12141d; margin: 12px; border-radius: 6px; border: 1px solid var(--border-color); }
        .synopsis { font-size: 12px; color: #ccc; line-height: 1.5; margin-top: 10px; }

        .ep-list-container { padding: 0 12px; margin-bottom: 15px; }
        .ep-search { width: 100%; background: #12141d; border: 1px solid var(--border-color); color: #fff; padding: 8px 12px; border-radius: 4px; font-size: 12px; margin-bottom: 10px; }
        .ep-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; max-height: 250px; overflow-y: auto; }
        .ep-btn { background: var(--card-bg); border: 1px solid var(--border-color); padding: 8px; border-radius: 4px; text-align: center; text-decoration: none; display: block; }
        .ep-btn.watching { border-color: var(--accent-red); }
        .ep-num { font-size: 11px; font-weight: bold; color: var(--accent-red); }

        .section-header { display: flex; align-items: center; justify-content: space-between; padding: 15px 12px 10px; }
        .section-title { font-size: 14px; font-weight: 800; color: #fff; border-left: 3px solid var(--accent-red); padding-left: 8px; text-transform: uppercase; }

        /* Pagination Controls */
        .pagination { display: flex; justify-content: center; gap: 8px; margin: 20px 0; }
        .page-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: #fff; padding: 6px 12px; font-size: 12px; border-radius: 4px; text-decoration: none; }
        .page-btn.active { background: var(--accent-red); border-color: var(--accent-red); }

        /* Bottom Nav */
        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; height: 55px; background: #12141d; border-top: 1px solid var(--border-color); display: flex; justify-content: space-around; align-items: center; z-index: 1000; }
        .nav-item { display: flex; flex-direction: column; align-items: center; color: #777; text-decoration: none; font-size: 10px; gap: 3px; }
        .nav-item i { font-size: 16px; }
        .nav-item.active { color: var(--accent-red); }
    </style>
</head>
<body>
    <header>
        <button class="menu-btn" onclick="toggleDrawer()"><i class="fa-solid fa-bars"></i></button>
        <a href="/" class="logo">LUCIFER <span>DONGHUA</span></a>
        <div class="header-actions">
            <a href="/login" class="login-btn"><i class="fa-solid fa-right-to-bracket"></i> Login</a>
        </div>
    </header>

    <div class="drawer-overlay" id="overlay" onclick="toggleDrawer()"></div>
    <div class="drawer" id="drawer">
        <a href="/" class="drawer-item"><i class="fa-solid fa-house"></i> Home</a>
        <a href="/history" class="drawer-item"><i class="fa-solid fa-clock-rotate-left"></i> Anime History</a>
        <a href="/genres" class="drawer-item"><i class="fa-solid fa-tags"></i> Genres</a>
        <a href="/tencent" class="drawer-item"><i class="fa-solid fa-tv"></i> Tencent Anime</a>
        <a href="/youku" class="drawer-item"><i class="fa-solid fa-play"></i> Youku Anime</a>
        <a href="/az-lists" class="drawer-item"><i class="fa-solid fa-list-ol"></i> AZ Lists</a>
        <a href="/bookmarks" class="drawer-item"><i class="fa-solid fa-bookmark"></i> Bookmarks</a>
    </div>

    <div class="premium-box">
        <div class="premium-title"><i class="fa-solid fa-crown" style="color:#ffb400;"></i> Go Premium and Remove All Ads</div>
        <div class="premium-sub">No ads, faster player, full 4K access. Start from $1.19 per month.</div>
        <div class="premium-pills">
            <span class="pill">✓ No ads</span>
            <span class="pill">✓ 4K Quality</span>
            <span class="pill">✓ High Speed Streaming</span>
        </div>
        <a href="#" class="premium-btn">Get Premium →</a>
    </div>

    {{ content | safe }}

    <nav class="bottom-nav">
        <a href="/" class="nav-item {{ 'active' if page == 'home' }}"><i class="fa-solid fa-house"></i>Home</a>
        <a href="/schedule" class="nav-item {{ 'active' if page == 'schedule' }}"><i class="fa-solid fa-calendar-days"></i>Schedule</a>
        <a href="/az-lists" class="nav-item {{ 'active' if page == 'anime' }}"><i class="fa-solid fa-film"></i>Anime</a>
        <a href="/history" class="nav-item {{ 'active' if page == 'saved' }}"><i class="fa-solid fa-bookmark"></i>Saved</a>
    </nav>

    <script>
        function toggleDrawer() {
            const drawer = document.getElementById('drawer');
            const overlay = document.getElementById('overlay');
            if (drawer.classList.contains('open')) {
                drawer.classList.remove('open');
                overlay.style.display = 'none';
            } else {
                drawer.classList.add('open');
                overlay.style.display = 'block';
            }
        }

        /* Client-Side JavaScript Video Server Switching */
        function switchServer(embedUrl, btnElement) {
            const iframe = document.getElementById('main-player');
            if (iframe && embedUrl) {
                iframe.src = embedUrl;
            }
            document.querySelectorAll('.server-btn').forEach(btn => btn.classList.remove('active'));
            if (btnElement) {
                btnElement.classList.add('active');
            }
        }

        /* Client-Side Live Episode Filter */
        function filterEpisodes() {
            const input = document.getElementById('ep-search-input').value.toLowerCase();
            const epButtons = document.querySelectorAll('.ep-btn');
            epButtons.forEach(btn => {
                const text = btn.innerText.toLowerCase();
                if (text.includes(input)) {
                    btn.style.display = 'block';
                } else {
                    btn.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

def fetch_cards(url):
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
                
                ep_match = re.search(r'Ep\s*\d+|Episode\s*\d+', title, re.IGNORECASE)
                ep_badge = ep_match.group(0) if ep_match else "4K"

                cards_html += f'''
                <a href="/watch?url={target_url}" class="card">
                    <div class="card-img-wrap">
                        <img src="{poster}" alt="{title}" onerror="this.src='https://via.placeholder.com/150x210?text=No+Cover'">
                        <span class="badge-type">DONGHUA</span>
                        <span class="badge-ep">{ep_badge}</span>
                    </div>
                    <div class="card-title">{title}</div>
                </a>
                '''
    except Exception as e:
        cards_html = f"<p style='padding:15px; color:#aaa;'>Error loading items: {e}</p>"
    return cards_html

@app.route('/')
def index():
    page_num = request.args.get('page', 1, type=int)
    target_url = "https://luciferdonghua.in/" if page_num == 1 else f"https://luciferdonghua.in/page/{page_num}/"
    cards = fetch_cards(target_url)
    
    pagination_html = f'''
    <div class="pagination">
        {'<a href="/?page=' + str(page_num - 1) + '" class="page-btn">Prev</a>' if page_num > 1 else ''}
        <span class="page-btn active">{page_num}</span>
        <a href="/?page={page_num + 1}" class="page-btn">Next</a>
    </div>
    '''

    content = f'''
        <div class="section-header">
            <div class="section-title">Popular Today (Page {page_num})</div>
        </div>
        <div class="grid-3">{cards}</div>
        {pagination_html}
    '''
    return render_template_string(LAYOUT, title=f"Home - Page {page_num}", content=content, page="home")

@app.route('/watch')
def watch():
    target_url = request.args.get('url', '')
    title = "Watch Donghua"
    synopsis = ""
    servers = []
    episodes_html = ""
    
    if target_url:
        try:
            res = requests.get(target_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Title
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
                
            # Extracts iframe servers
            iframes = soup.find_all('iframe')
            for idx, iframe in enumerate(iframes):
                src = iframe.get('src') or iframe.get('data-src') or ""
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    servers.append({
                        "name": f"Server {idx + 1} ([4K] Stream)",
                        "url": src
                    })

            # Extracts select option servers if present
            options = soup.find_all('option')
            for opt in options:
                val = opt.get('value', '')
                if val and 'http' in val:
                    servers.append({
                        "name": opt.get_text(strip=True) or f"Server {len(servers)+1}",
                        "url": val
                    })

            # Synopsis
            desc = soup.find('div', class_='entry-content') or soup.find('div', class_='desc')
            if desc:
                synopsis = desc.get_text(strip=True)

            # All Episodes Links
            ep_links = soup.find_all('a', href=re.compile(r'luciferdonghua\.in/'))
            seen = set()
            for ep in ep_links:
                ep_url = ep.get('href')
                ep_text = ep.get_text(strip=True)
                if ep_url and ep_url not in seen and any(k in ep_text.lower() for k in ['ep', 'episode', '1', '2', '3', '4', '5']):
                    seen.add(ep_url)
                    is_current = 'watching' if ep_url == target_url else ''
                    episodes_html += f'''
                    <a href="/watch?url={ep_url}" class="ep-btn {is_current}">
                        <div class="ep-num">{ep_text}</div>
                    </a>
                    '''

        except Exception as e:
            print("Extraction error:", e)

    # Fallback default server links if target site uses obfuscated embeds
    if not servers:
        servers = [
            {"name": "[4K] Dailymotion - Server 1", "url": "https://www.dailymotion.com/embed/video/k2x1123"},
            {"name": "[4K] Rumble - Server 2", "url": "https://rumble.com/embed/"},
            {"name": "[4K] OK.RU - Server 3", "url": "https://ok.ru/videoembed/"}
        ]

    server_btns = ""
    for idx, srv in enumerate(servers):
        active_class = "active" if idx == 0 else ""
        server_btns += f'''
        <button class="server-btn {active_class}" onclick="switchServer('{srv['url']}', this)">
            {srv['name']}
        </button>
        '''

    initial_stream = servers[0]['url'] if servers else ""

    content = f'''
        <div class="player-container">
            <iframe id="main-player" src="{initial_stream}" allowfullscreen allow="autoplay; encrypted-media"></iframe>
        </div>

        <div class="warning-box">
            <i class="fa-solid fa-triangle-exclamation"></i> <strong>Notice:</strong> Click any server button below to load interactive stream mirrors.
        </div>

        <div class="server-box">
            <div class="server-title">Select Video Server</div>
            <div class="server-grid">
                {server_btns}
            </div>
        </div>

        <div class="section-header">
            <div class="section-title">All Episodes</div>
        </div>

        <div class="ep-list-container">
            <input type="text" id="ep-search-input" class="ep-search" onkeyup="filterEpisodes()" placeholder="Search episode number... (e.g. 153 or 208)">
            <div class="ep-grid">
                {episodes_html if episodes_html else '<a href="#" class="ep-btn watching"><div class="ep-num">Episode Stream Active</div></a>'}
            </div>
        </div>

        <div class="details-container">
            <h3 style="font-size:13px; font-weight:bold; color:#fff; margin-bottom:6px;">{title}</h3>
            <div class="synopsis">{synopsis if synopsis else "Enjoy watching " + title + " on Lucifer Donghua."}</div>
        </div>
    '''
    return render_template_string(LAYOUT, title=title, content=content, page="anime")

@app.route('/genres')
def genres():
    cards = fetch_cards("https://luciferdonghua.in/genres/")
    content = f'''
        <div class="section-header"><div class="section-title">Genres</div></div>
        <div class="grid-3">{cards}</div>
    '''
    return render_template_string(LAYOUT, title="Genres", content=content, page="anime")

@app.route('/history')
def history():
    content = '''
        <div class="section-header"><div class="section-title">Anime History</div></div>
        <p style="padding: 12px; font-size:12px; color:#aaa;">Select any anime to continue watching where you left off.</p>
    '''
    return render_template_string(LAYOUT, title="History", content=content, page="saved")

@app.route('/schedule')
def schedule():
    cards = fetch_cards("https://luciferdonghua.in/schedule/")
    content = f'''
        <div class="section-header"><div class="section-title">Weekly Schedule</div></div>
        <div class="grid-3">{cards}</div>
    '''
    return render_template_string(LAYOUT, title="Schedule", content=content, page="schedule")

@app.route('/az-lists')
def az_lists():
    cards = fetch_cards("https://luciferdonghua.in/az-list/")
    content = f'''
        <div class="section-header"><div class="section-title">AZ Lists</div></div>
        <div class="grid-3">{cards}</div>
    '''
    return render_template_string(LAYOUT, title="AZ Lists", content=content, page="anime")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
