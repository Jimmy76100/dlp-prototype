# app.py
from flask import Flask, request, jsonify
import sqlite3, datetime, os

DB = "dlp.db"
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS incidents
                 (id INTEGER PRIMARY KEY, ts TEXT, source TEXT, channel TEXT, pattern TEXT, excerpt TEXT, action TEXT)''')
    conn.commit()
    conn.close()

@app.route("/api/log", methods=["POST"])
def log_incident():
    data = request.json
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO incidents (ts, source, channel, pattern, excerpt, action) VALUES (?,?,?,?,?,?)",
              (datetime.datetime.utcnow().isoformat(), data.get("source"), data.get("channel"), data.get("pattern"),
               (data.get("excerpt") or "")[:1000], data.get("action")))
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"}), 201

@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute("SELECT id, ts, source, channel, pattern, excerpt, action FROM incidents ORDER BY id DESC LIMIT 200").fetchall()
    conn.close()
    keys = ["id","ts","source","channel","pattern","excerpt","action"]
    return jsonify([dict(zip(keys,row)) for row in rows])

if __name__ == "__main__":
    if not os.path.exists(DB): init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
