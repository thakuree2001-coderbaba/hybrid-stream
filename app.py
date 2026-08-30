import os
import re
from urllib.parse import urljoin, quote_plus
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template_string, abort, Response

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

BASE_URL = "https://luciferdonghua.in"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Referer": f"{BASE_URL}/"
}

session = requests.Session()
session.headers.update(HEADERS)

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

@app.route('/')
def home():
    return render_template_string(LAYOUT, stream_url="https://rumble.com/embed/v238xxx/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
