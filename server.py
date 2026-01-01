from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# Permette al gioco di comunicare con il server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "scores.db"

class Score(BaseModel):
    name: str
    score: int

def init():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)")
init()

@app.get("/leaderboard")
def leaderboard():
    with sqlite3.connect(DB) as c:
        return c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10").fetchall()

@app.post("/score")
def add_score(s: Score):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (s.name[:12], s.score))
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    # Render usa la variabile d'ambiente PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)