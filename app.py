import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="public", static_url_path="")

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Route to serve main index.html
@app.route("/")
def index():
    return send_from_directory("public", "index.html")

# API Endpoint to fetch Anime/Donghua media list
@app.route("/api/media", methods=["GET"])
def get_media():
    category = request.args.get("category")
    search = request.args.get("search")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM Media WHERE 1=1"
    params = []

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
        
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    media_list = [dict(row) for row in rows]
    return jsonify({"status": "success", "data": media_list})

# API Endpoint to fetch episodes for a specific media item
@app.route("/api/episodes/<int:media_id>", methods=["GET"])
def get_episodes(media_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Episodes WHERE media_id = ? ORDER BY episode_num ASC", (media_id,))
    rows = cursor.fetchall()
    conn.close()

    episodes = [dict(row) for row in rows]
    return jsonify({"status": "success", "data": episodes})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
