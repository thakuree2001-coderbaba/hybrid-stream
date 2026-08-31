import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string

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
        body { background: #08090d; color: #fff; font-family: sans-serif; margin: 0; padding-bottom: 60px; }
        header { background: #0e1017; padding: 15px; border-bottom: 1px solid #202431; }
        .logo { font-weight: 900; color: #fff; text-decoration: none; }
        .logo span { color: #e50914; }
        .player-container { width: 100%; aspect-ratio: 16/9; background: #000; }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <header><a href="/" class="logo">LUCIFER <span>DONGHUA</span></a></header>
    <main>
        <div class="player-container">
            <iframe id="main-player" src="{{ stream_url }}" allowfullscreen referrerpolicy="no-referrer"></iframe>
        </div>
    </main>
</body>
</html>
"""

def get_latest_stream():
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        iframe = soup.find('iframe')
        if iframe and iframe.get('src'):
            src = iframe['src']
            return src if src.startswith('http') else f"https:{src}"
    except Exception as e:
        print(f"Scraping error: {e}")
    return "about:blank"

@app.route('/')
def home():
    stream_url = get_latest_stream()
    return render_template_string(LAYOUT, stream_url=stream_url)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
