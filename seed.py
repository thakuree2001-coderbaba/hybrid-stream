import sqlite3
import httpx
from bs4 import BeautifulSoup

def seed_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Sample catalog data merging AniWave anime and Lucifer Donghua content
    sample_catalog = [
        (
            "Battle Through the Heavens (BTTH)",
            "Donghua",
            "https://picsum.photos/300/450?random=101",
            "https://picsum.photos/1200/400?random=102",
            9.8,
            "Xiao Yan regains his powers and embarks on a journey to conquer the Dou Qi continent.",
            "Action, Cultivation, Fantasy",
            "Lucifer Donghua"
        ),
        (
            "Solo Leveling Season 2",
            "Anime",
            "https://picsum.photos/300/450?random=103",
            "https://picsum.photos/1200/400?random=104",
            9.7,
            "Sung Jinwoo continues his descent into the shadow monarch powers.",
            "Action, Fantasy, Superpower",
            "AniWave"
        ),
        (
            "Perfect World (Wanmei Shijie)",
            "Donghua",
            "https://picsum.photos/300/450?random=105",
            "https://picsum.photos/1200/400?random=106",
            9.6,
            "Shi Hao was born with a supreme bone, destined to rule the heavens.",
            "Action, Cultivation, Adventure",
            "Lucifer Donghua"
        ),
        (
            "Demon Slayer: Hashira Training Arc",
            "Anime",
            "https://picsum.photos/300/450?random=107",
            "https://picsum.photos/1200/400?random=108",
            9.5,
            "Tanjiro undergoes intense training with the Hashira.",
            "Action, Supernatural, Shounen",
            "AniWave"
        )
    ]

    print("[*] Seeding Media database...")
    for item in sample_catalog:
        cursor.execute("""
            INSERT INTO Media (title, category, poster_url, banner_url, rating, synopsis, genres, source_platform)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, item)
        media_id = cursor.lastrowid

        # Insert 12 sample episodes for each media item
        for ep in range(1, 13):
            cursor.execute("""
                INSERT INTO Episodes (media_id, episode_num, server_alpha, server_beta, sub_type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                media_id,
                ep,
                f"https://www.youtube.com/embed/dQw4w9WgXcQ",
                f"https://www.youtube.com/embed/dQw4w9WgXcQ",
                "SUB"
            ))

    conn.commit()
    conn.close()
    print("[+] Database successfully seeded with catalog items and episode streams!")

if __name__ == "__main__":
    seed_database()
