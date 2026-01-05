import os
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# --- CONFIGURAZIONE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permette a itch.io di connettersi
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURAZIONE DATABASE POSTGRESQL ---
DB_URL = os.environ.get("DATABASE_URL")

# Modello dati per ricezione punteggio
class Score(BaseModel):
    name: str
    score: int

# --- INIZIALIZZAZIONE DB ---
def init_db():
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require')
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                score INTEGER
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database PostgreSQL inizializzato correttamente.")
    except Exception as e:
        print(f"Errore inizializzazione DB: {e}")

# Inizializza subito il DB all'avvio
if DB_URL:
    init_db()
else:
    print("ERRORE: DATABASE_URL non trovato nelle variabili d'ambiente!")

# --- ENDPOINTS ---

@app.get("/leaderboard")
def leaderboard():
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require')
        cur = conn.cursor()
        # Prende i primi 10 punteggi migliori
        cur.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print(f"Errore lettura DB: {e}")
        return []

@app.post("/score")
def add_score(s: Score):
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require')
        cur = conn.cursor()
        
        # 1. Inserisce il nuovo punteggio
        safe_name = s.name.strip()[:12] # Pulisce spazi e taglia a 12 caratteri
        cur.execute("INSERT INTO scores (name, score) VALUES (%s, %s)", (safe_name, s.score))
        
        # 2. PULIZIA: Mantiene solo la Top 10, cancella gli altri
        # Questa query cancella tutti gli ID che NON sono nei primi 10
        cur.execute("""
            DELETE FROM scores
            WHERE id NOT IN (
                SELECT id FROM scores
                ORDER BY score DESC
                LIMIT 10
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True}
    except Exception as e:
        print(f"Errore scrittura DB: {e}")
        return {"ok": False, "error": str(e)}
        
@app.get("/")
def root():
    return {"status": "alive"}


# Avvio server (necessario per Render)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)