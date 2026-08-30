import os
import re
from urllib.parse import urljoin, urlparse, quote_plus

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template_string, abort


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__, static_folder="public", static_url_path="")

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB request limit


BASE_URL = "https://luciferdonghua.in"
HOME_URL = f"{BASE_URL}/"
SERIES_URL = f"{BASE_URL}/series/"

ALLOWED_HOSTS = {
    "luciferdonghua.in",
    "www.luciferdonghua.in",
}


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": BASE_URL + "/",
    "Accept-Language": "en-US,en;q=0.9",
}


REQUEST_TIMEOUT = (5, 12)


# ============================================================
# SESSION
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# ALLOWED EMBED PROVIDERS
# ============================================================

EMBED_PATTERNS = [
    r"rumble\.com/embed",
    r"dailymotion\.com/embed",
    r"ok\.ru/videoembed",
    r"vidhide",
    r"luluvdo",
    r"streamtape",
]


# ============================================================
# HTML TEMPLATE
# ============================================================

LAYOUT = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width,
        initial-scale=1.0,
        maximum-scale=1.0"
    >

    <meta name="theme-color" content="#0b0c10">

    <meta
        name="description"
        content="{{ title }} - Lucifer Donghua"
    >

    <title>{{ title }} - LUCIFER DONGHUA</title>

    <link
        rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    >

    <style>

        :root {
            --bg: #08090d;
            --header: #0e1017;
            --card: #12151e;
            --card-hover: #181c27;
            --accent: #e50914;
            --accent-dark: #a80710;
            --text: #eeeeee;
            --muted: #858995;
            --border: #202431;
            --success: #20c997;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            background: var(--bg);
            color: var(--text);
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Roboto,
                Arial,
                sans-serif;

            padding-bottom: 75px;
            min-height: 100vh;
        }

        a {
            color: inherit;
        }


        /* ====================================================
           HEADER
        ==================================================== */

        header {
            height: 62px;
            width: 100%;

            background: rgba(14, 16, 23, 0.97);

            border-bottom:
                1px solid var(--border);

            display: flex;
            align-items: center;
            justify-content: space-between;

            padding: 0 14px;

            position: sticky;
            top: 0;

            z-index: 999;

            backdrop-filter: blur(10px);

            gap: 10px;
        }

        .logo {
            text-decoration: none;

            color: #fff;

            font-size: 15px;
            font-weight: 900;

            letter-spacing: 0.5px;

            white-space: nowrap;
        }

        .logo span {
            color: var(--accent);
        }


        /* ====================================================
           SEARCH
        ==================================================== */

        .search-form {
            display: flex;
            align-items: center;

            background: #191c25;

            border:
                1px solid var(--border);

            border-radius: 22px;

            height: 38px;

            width: 220px;

            padding: 0 11px;

            transition: 0.2s ease;
        }

        .search-form:focus-within {
            border-color: var(--accent);

            box-shadow:
                0 0 0 2px
                rgba(229, 9, 20, 0.12);
        }

        .search-form input {
            width: 100%;

            background: transparent;

            border: none;

            outline: none;

            color: #fff;

            font-size: 12px;

            min-width: 0;
        }

        .search-form input::placeholder {
            color: #70747f;
        }

        .search-form button {
            border: none;

            background: transparent;

            color: #999;

            cursor: pointer;

            padding: 5px;
        }

        .search-form button:hover {
            color: var(--accent);
        }


        /* ====================================================
           MAIN
        ==================================================== */

        .main-container {
            width: 100%;
            max-width: 1400px;

            margin: auto;

            padding-bottom: 20px;
        }


        /* ====================================================
           PAGE TITLE
        ==================================================== */

        .page-heading {
            padding: 18px 12px 10px;

            font-size: 15px;

            font-weight: 800;
        }

        .page-heading span {
            color: var(--accent);
        }


        /* ====================================================
           ANIME GRID
        ==================================================== */

        .anime-grid {
            display: grid;

            grid-template-columns:
                repeat(6, minmax(0, 1fr));

            gap: 12px;

            padding: 0 12px;
        }

        .anime-card {
            background: var(--card);

            border:
                1px solid var(--border);

            border-radius: 8px;

            overflow: hidden;

            text-decoration: none;

            display: block;

            transition:
                transform 0.2s ease,
                border-color 0.2s ease,
                background 0.2s ease;
        }

        .anime-card:hover {
            transform: translateY(-3px);

            border-color: #353b4b;

            background: var(--card-hover);
        }

        .poster {
            position: relative;

            width: 100%;

            aspect-ratio: 0.71;

            background: #050505;

            overflow: hidden;
        }

        .poster img {
            width: 100%;
            height: 100%;

            object-fit: cover;

            display: block;

            transition: transform 0.3s ease;
        }

        .anime-card:hover .poster img {
            transform: scale(1.04);
        }

        .quality {
            position: absolute;

            top: 6px;
            right: 6px;

            background: var(--accent);

            color: #fff;

            font-size: 9px;

            font-weight: 800;

            padding: 3px 5px;

            border-radius: 4px;
        }

        .anime-title {
            padding: 8px 6px;

            font-size: 11px;

            line-height: 1.3;

            color: #eee;

            font-weight: 600;

            min-height: 38px;

            display: -webkit-box;

            -webkit-line-clamp: 2;

            -webkit-box-orient: vertical;

            overflow: hidden;
        }


        /* ====================================================
           PLAYER
        ==================================================== */

        .player-container {
            width: 100%;

            aspect-ratio: 16 / 9;

            background: #000;

            position: relative;
        }

        .player-container iframe {
            width: 100%;
            height: 100%;

            border: none;

            display: block;

            background: #000;
        }


        /* ====================================================
           PREMIUM BANNER
        ==================================================== */

        .banner-premium {
            margin: 12px;

            padding: 13px;

            border-radius: 9px;

            background:
                linear-gradient(
                    135deg,
                    #210608,
                    #0d0f16
                );

            border:
                1px solid #3c1014;
        }

        .banner-title {
            color: #fff;

            font-size: 13px;

            font-weight: 800;

            display: flex;

            align-items: center;

            gap: 7px;
        }

        .banner-title i {
            color: #ffb703;
        }

        .banner-sub {
            color: var(--muted);

            font-size: 10px;

            margin-top: 5px;

            line-height: 1.5;
        }

        .badge-group {
            display: flex;

            flex-wrap: wrap;

            gap: 6px;

            margin-top: 9px;
        }

        .badge {
            background:
                rgba(229, 9, 20, 0.12);

            border:
                1px solid var(--accent);

            color: #eee;

            font-size: 9px;

            padding: 4px 7px;

            border-radius: 4px;

            font-weight: 700;
        }


        /* ====================================================
           SERVER BOX
        ==================================================== */

        .server-box {
            margin: 12px;

            padding: 13px;

            border:
                1px solid var(--border);

            background: var(--header);

            border-radius: 9px;
        }

        .section-title {
            color: var(--muted);

            font-size: 10px;

            font-weight: 800;

            text-transform: uppercase;

            letter-spacing: 0.6px;

            margin-bottom: 10px;
        }

        .server-grid {
            display: grid;

            grid-template-columns:
                repeat(auto-fit, minmax(120px, 1fr));

            gap: 8px;
        }

        .server-btn {
            appearance: none;

            border:
                1px solid var(--border);

            background: var(--card);

            color: #bbb;

            padding: 10px 7px;

            border-radius: 6px;

            font-size: 11px;

            font-weight: 700;

            cursor: pointer;

            transition: 0.2s ease;

            overflow: hidden;

            text-overflow: ellipsis;

            white-space: nowrap;
        }

        .server-btn:hover {
            border-color: #454b5c;

            color: #fff;
        }

        .server-btn.active {
            color: var(--accent);

            border-color: var(--accent);

            background:
                rgba(229, 9, 20, 0.10);
        }


        /* ====================================================
           EPISODES
        ==================================================== */

        .episode-container {
            padding: 0 12px;
        }

        .episode-grid {
            display: grid;

            grid-template-columns:
                repeat(6, minmax(0, 1fr));

            gap: 7px;

            max-height: 390px;

            overflow-y: auto;

            padding-right: 3px;
        }

        .episode-btn {
            text-decoration: none;

            background: var(--card);

            border:
                1px solid var(--border);

            color: #ddd;

            border-radius: 6px;

            padding: 10px 5px;

            text-align: center;

            font-size: 10px;

            font-weight: 700;

            transition: 0.2s ease;

            overflow: hidden;

            text-overflow: ellipsis;

            white-space: nowrap;
        }

        .episode-btn:hover {
            border-color: var(--accent);

            color: #fff;
        }

        .episode-btn.active {
            color: #fff;

            background:
                rgba(229, 9, 20, 0.18);

            border-color: var(--accent);
        }


        /* ====================================================
           EMPTY / ERROR
        ==================================================== */

        .message {
            margin: 20px 12px;

            padding: 25px 15px;

            text-align: center;

            color: var(--muted);

            background: var(--card);

            border:
                1px solid var(--border);

            border-radius: 9px;

            font-size: 12px;
        }

        .message i {
            display: block;

            font-size: 25px;

            margin-bottom: 10px;

            color: var(--accent);
        }


        /* ====================================================
           BOTTOM NAV
        ==================================================== */

        .bottom-nav {
            position: fixed;

            left: 0;
            right: 0;
            bottom: 0;

            height: 60px;

            background:
                rgba(14, 16, 23, 0.98);

            border-top:
                1px solid var(--border);

            display: flex;

            justify-content: center;

            gap: 80px;

            align-items: center;

            z-index: 1000;

            backdrop-filter: blur(10px);
        }

        .nav-item {
            text-decoration: none;

            color: #70747f;

            display: flex;

            flex-direction: column;

            align-items: center;

            gap: 4px;

            font-size: 10px;

            min-width: 60px;
        }

        .nav-item i {
            font-size: 17px;
        }

        .nav-item.active {
            color: var(--accent);
        }


        /* ====================================================
           TABLET
        ==================================================== */

        @media (max-width: 1000px) {

            .anime-grid {
                grid-template-columns:
                    repeat(5, minmax(0, 1fr));
            }

            .episode-grid {
                grid-template-columns:
                    repeat(5, minmax(0, 1fr));
            }
        }


        /* ====================================================
           MOBILE
        ==================================================== */

        @media (max-width: 700px) {

            header {
                height: 58px;

                padding: 0 10px;

                gap: 7px;
            }

            .logo {
                font-size: 12px;
            }

            .search-form {
                height: 34px;

                width: auto;

                flex: 1;

                max-width: none;
            }

            .search-form input {
                font-size: 11px;
            }

            .anime-grid {
                grid-template-columns:
                    repeat(3, minmax(0, 1fr));

                gap: 7px;

                padding: 0 8px;
            }

            .page-heading {
                padding: 15px 9px 9px;
            }

            .anime-title {
                font-size: 9px;

                padding: 6px 4px;

                min-height: 32px;
            }

            .quality {
                top: 4px;
                right: 4px;

                font-size: 8px;
            }

            .banner-premium,
            .server-box {
                margin: 8px;
            }

            .episode-container {
                padding: 0 8px;
            }

            .episode-grid {
                grid-template-columns:
                    repeat(4, minmax(0, 1fr));

                gap: 6px;

                max-height: 340px;
            }

            .episode-btn {
                font-size: 9px;

                padding: 9px 3px;
            }

            .server-grid {
                grid-template-columns:
                    repeat(2, minmax(0, 1fr));
            }

            .bottom-nav {
                height: 57px;

                gap: 45px;
            }
        }


        /* ====================================================
           VERY SMALL PHONES
        ==================================================== */

        @media (max-width: 380px) {

            .logo {
                font-size: 10px;
            }

            .anime-grid {
                gap: 5px;

                padding: 0 6px;
            }

            .episode-grid {
                grid-template-columns:
                    repeat(3, minmax(0, 1fr));
            }

            .bottom-nav {
                gap: 25px;
            }
        }

    </style>
</head>

<body>

<header>

    <a href="/" class="logo">
        LUCIFER <span>DONGHUA</span>
    </a>

    <form
        class="search-form"
        action="/search"
        method="get"
        autocomplete="off"
    >

        <input
            type="search"
            name="q"
            placeholder="Search donghua..."
            maxlength="100"
            value="{{ search_query }}"
            required
        >

        <button type="submit" aria-label="Search">
            <i class="fa-solid fa-magnifying-glass"></i>
        </button>

    </form>

</header>


<main class="main-container">

    {{ content | safe }}

</main>


<nav class="bottom-nav">

    <a
        href="/"
        class="nav-item {{ 'active' if active_nav == 'home' else '' }}"
    >
        <i class="fa-solid fa-house"></i>
        <span>Home</span>
    </a>

    <a
        href="/anime"
        class="nav-item {{ 'active' if active_nav == 'anime' else '' }}"
    >
        <i class="fa-solid fa-film"></i>
        <span>Anime List</span>
    </a>

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


# ============================================================
# HELPER FUNCTIONS & ROUTE LOGIC
# ============================================================

def is_safe_url(target):
    """Ensure requested URL target belongs strictly to luciferdonghua.in domain."""
    try:
        ref_url = urlparse(BASE_URL)
        test_url = urlparse(target)
        return test_url.scheme in ('http', 'https') and test_url.netloc in ALLOWED_HOSTS
    except Exception:
        return False


def parse_anime_cards(soup):
    """Parses standard site cards into clean anime-grid HTML."""
    cards_html = ""
    articles = soup.find_all(['article', 'div'], class_=re.compile(r'bsx|item|article|post', re.I))
    
    for article in articles:
        link = article.find('a')
        img = article.find('img')
        title_el = article.find(['h2', 'h3', 'h4']) or link

        if link and title_el:
            t_text = title_el.get_text(strip=True)
            raw_href = link.get('href', '')
            
            # Map source URL to localized route
            full_target = urljoin(BASE_URL, raw_href)
            if not is_safe_url(full_target):
                continue
                
            local_href = f"/watch?url={quote_plus(full_target)}"
            img_src = img.get('data-src') or img.get('src') or '' if img else ''
            
            cards_html += f'''
            <a href="{local_href}" class="anime-card">
                <div class="poster">
                    <img src="{img_src}" alt="{t_text}" loading="lazy">
                    <div class="quality">HD</div>
                </div>
                <div class="anime-title">{t_text}</div>
            </a>
            '''
    return cards_html


@app.route('/')
def index():
    try:
        res = session.get(HOME_URL, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = parse_anime_cards(soup)
        
        if not cards:
            cards = '''
            <div class="message">
                <i class="fa-solid fa-triangle-exclamation"></i>
                No donghua updates found right now.
            </div>
            '''
    except Exception as e:
        cards = f'''
        <div class="message">
            <i class="fa-solid fa-circle-exclamation"></i>
            Failed to connect to source server. ({e})
        </div>
        '''

    content = f'''
    <div class="page-heading">Latest <span>Releases</span></div>
    <div class="anime-grid">{cards}</div>
    '''
    return render_template_string(LAYOUT, title="Home", content=content, active_nav="home", search_query="")


@app.route('/anime')
def anime_list():
    try:
        res = session.get(SERIES_URL, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(res.text, 'html.parser')
        cards = parse_anime_cards(soup)
        
        if not cards:
            cards = '''
            <div class="message">
                <i class="fa-solid fa-film"></i>
                Series catalog is currently empty.
            </div>
            '''
    except Exception as e:
        cards = f'''
        <div class="message">
            <i class="fa-solid fa-circle-exclamation"></i>
            Unable to load series catalog. ({e})
        </div>
        '''

    content = f'''
    <div class="page-heading">All <span>Donghua & Series</span></div>
    <div class="anime-grid">{cards}</div>
    '''
    return render_template_string(LAYOUT, title="Anime List", content=content, active_nav="anime", search_query="")


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    cards = ""
    
    if query:
        try:
            search_endpoint = f"{BASE_URL}/?s={quote_plus(query)}"
            res = session.get(search_endpoint, timeout=REQUEST_TIMEOUT)
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = parse_anime_cards(soup)
        except Exception as e:
            cards = f'''
            <div class="message">
                <i class="fa-solid fa-circle-exclamation"></i>
                Search error encountered: {e}
            </div>
            '''

    if not cards and query:
        cards = f'''
        <div class="message">
            <i class="fa-solid fa-magnifying-glass"></i>
            No results found matching "<b>{query}</b>".
        </div>
        '''

    content = f'''
    <div class="page-heading">Search <span>Results</span> for: "{query}"</div>
    <div class="anime-grid">{cards}</div>
    '''
    return render_template_string(LAYOUT, title=f"Search: {query}", content=content, active_nav="", search_query=query)


@app.route('/watch')
def watch():
    target_url = request.args.get('url', '').strip()
    
    if not target_url or not is_safe_url(target_url):
        abort(400, "Invalid or unauthorized target URL.")

    title = "Watch Donghua"
    servers = []
    episodes = []

    try:
        res = session.get(target_url, timeout=REQUEST_TIMEOUT)
        html_text = res.text
        soup = BeautifulSoup(html_text, 'html.parser')

        # Heading Title
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)

        # 1. Resolve Dynamic Player Options via WordPress AJAX
        options = soup.find_all(['option', 'li', 'div', 'a'], attrs={'data-post': True})
        for opt in options:
            post_id = opt.get('data-post')
            nume = opt.get('data-nume')
            type_val = opt.get('data-type')
            
            if post_id:
                try:
                    ajax_res = session.post(
                        f"{BASE_URL}/wp-admin/admin-ajax.php",
                        data={'action': 'player_ajax', 'post': post_id, 'nume': nume, 'type': type_val},
                        timeout=(3, 6)
                    )
                    iframe_match = re.search(r'src=["\']([^"\']+)["\']', ajax_res.text)
                    if iframe_match:
                        embed_link = iframe_match.group(1).replace('\\/', '/')
                        if embed_link.startswith('//'):
                            embed_link = 'https:' + embed_link
                            
                        # Validate embed host matching known video platforms
                        if any(re.search(pat, embed_link, re.I) for pat in EMBED_PATTERNS):
                            if not any(s['url'] == embed_link for s in servers):
                                servers.append({
                                    "name": f"Server {len(servers) + 1}",
                                    "url": embed_link
                                })
                except Exception:
                    pass

        # 2. Regex fallback scan directly inside script blocks if AJAX fails
        if not servers:
            for pat in EMBED_PATTERNS:
                matches = re.findall(rf'(https?://[^\s"\'<>]*{pat}[^\s"\'<>]*)', html_text, re.I)
                for raw in matches:
                    clean_url = raw.replace('\\/', '/').replace('&amp;', '&')
                    if not any(s['url'] == clean_url for s in servers):
                        servers.append({
                            "name": f"Server {len(servers) + 1}",
                            "url": clean_url
                        })

        # 3. Episode List Parser
        series_anchor = soup.find('a', href=re.compile(r'/anime/|/series/'))
        ep_target = series_anchor.get('href') if series_anchor else target_url
        
        ep_res = session.get(ep_target, timeout=REQUEST_TIMEOUT)
        ep_soup = BeautifulSoup(ep_res.text, 'html.parser')

        ep_container = ep_soup.find('div', class_=re.compile(r'eplister|episodes|eplist|bx', re.I)) or ep_soup
        for ep in ep_container.find_all('a', href=re.compile(r'luciferdonghua\.in/')):
            ep_href = ep.get('href', '')
            full_ep_href = urljoin(BASE_URL, ep_href)
            
            if is_safe_url(full_ep_href) and re.search(r'episode-\d+|ep-\d+', full_ep_href, re.I):
                ep_match = re.search(r'Episode\s*(\d+)|Ep\s*(\d+)', ep.get_text(), re.I)
                if not ep_match:
                    ep_match = re.search(r'-episode-(\d+)', full_ep_href, re.I)
                
                num = ep_match.group(1) or ep_match.group(2) if ep_match else ""
                display_name = f"Episode {num}" if num else "Episode"
                local_ep_href = f"/watch?url={quote_plus(full_ep_href)}"

                if not any(e['href'] == local_ep_href for e in episodes):
                    episodes.append({
                        "name": display_name,
                        "href": local_ep_href,
                        "is_current": full_ep_href == target_url
                    })

    except Exception as e:
        print("Watch page parse error:", e)

    # Server Buttons Generation
    server_btns = ""
    for idx, srv in enumerate(servers):
        active_cls = "active" if idx == 0 else ""
        server_btns += f'''
        <button class="server-btn {active_cls}" onclick="setServer('{srv['url']}', this)">
            {srv['name']}
        </button>
        '''

    # Episode Buttons Generation
    episodes_html = ""
    for ep in episodes:
        active_cls = "active" if ep['is_current'] else ""
        episodes_html += f'''
        <a href="{ep['href']}" class="episode-btn {active_cls}">{ep['name']}</a>
        '''

    initial_stream = servers[0]['url'] if servers else ""

    content = f'''
    <div class="player-container">
        {'<iframe id="main-player" src="' + initial_stream + '" allowfullscreen allow="autoplay; encrypted-media"></iframe>' if initial_stream else '<div class="message"><i class="fa-solid fa-video-slash"></i>No stream embed link found for this episode.</div>'}
    </div>

    <div class="banner-premium">
        <div class="banner-title"><i class="fa-solid fa-crown"></i> Premium Access</div>
        <div class="banner-sub">Ad-free streaming experience, high bandwidth CDN, and up to 4K resolution streams.</div>
        <div class="badge-group">
            <span class="badge"><i class="fa-solid fa-check"></i> Zero Ads</span>
            <span class="badge"><i class="fa-solid fa-check"></i> Ultra HD 4K</span>
            <span class="badge"><i class="fa-solid fa-check"></i> Fast Servers</span>
        </div>
    </div>

    <div class="server-box">
        <div class="section-title">Select Video Server</div>
        <div class="server-grid">
            {server_btns if server_btns else '<p style="font-size:11px; color:var(--muted);">No server nodes extracted.</p>'}
        </div>
    </div>

    <div class="episode-container">
        <div class="section-title">Episodes</div>
        <div class="episode-grid">
            {episodes_html if episodes_html else '<p style="font-size:11px; color:var(--muted);">No episode list found.</p>'}
        </div>
    </div>
    '''
    
    return render_template_string(LAYOUT, title=title, content=content, active_nav="", search_query="")


# ============================================================
# ENTRYPOINT
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
