import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT CHECK(category IN ('Donghua', 'Anime')),
        poster_url TEXT,
        banner_url TEXT,
        rating REAL,
        synopsis TEXT,
        genres TEXT,
        source_platform TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Episodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        media_id INTEGER,
        episode_num INTEGER,
        server_alpha TEXT,
        server_beta TEXT,
        sub_type TEXT CHECK(sub_type IN ('SUB', 'DUB', 'RAW')),
        FOREIGN KEY(media_id) REFERENCES Media(id)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
