import requests
from bs4 import BeautifulSoup
import sqlite3

DB_NAME = "database.db"

def scrape_lucifer_latest():
    url = "https://luciferdonghua.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch site: Status {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        scraped_count = 0
        for article in articles:
            title_tag = article.find('h2') or article.find('h3')
            link_tag = article.find('a')
            img_tag = article.find('img')

            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                page_url = link_tag.get('href', '')
                poster_url = img_tag.get('src', '') if img_tag else 'https://via.placeholder.com/300x400'

                cursor.execute("""
                    INSERT OR IGNORE INTO Media (title, category, source_platform, poster_url, rating)
                    VALUES (?, 'Donghua', 'LuciferDonghua', ?, 8.5)
                """, (title, poster_url))

                cursor.execute("SELECT id FROM Media WHERE title = ?", (title,))
                media_row = cursor.fetchone()

                if media_row:
                    media_id = media_row[0]
                    cursor.execute("""
                        INSERT OR IGNORE INTO Episodes (media_id, episode_num, server_alpha)
                        VALUES (?, 1, ?)
                    """, (media_id, page_url))
                    scraped_count += 1

        conn.commit()
        conn.close()
        print(f"Scraping complete. Processed {scraped_count} entries.")

    except Exception as e:
        print(f"Scraping error: {e}")

if __name__ == "__main__":
    scrape_lucifer_latest()
