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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURAZIONE DATABASE POSTGRESQL ---
# Utilizzo l'External URL fornito (può essere sovrascritto da variabili d'ambiente)
DB_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://ffgame_db_user:mD3mSzbf4zTtd6JGv1pZfOmThdwKJg2O@dpg-d5bphgmmcj7s739f3pmg-a.oregon-postgres.render.com/ffgame_db"
)

# Modello dati per ricezione punteggio
class Score(BaseModel):
    name: str
    score: int

# --- INIZIALIZZAZIONE DB ---
def init_db():
    try:
        # Aggiungiamo sslmode='require' per connessioni sicure su Render
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

init_db()

# --- ENDPOINTS ---

@app.get("/leaderboard")
def leaderboard():
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require')
        cur = conn.cursor()
        # Prende i primi 10 punteggi in ordine decrescente
        cur.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
        data = cur.fetchall()
        cur.close()
        conn.close()
        # Restituisce una lista di liste/tuple es: [["Mario", 100], ["Luigi", 90]]
        return data
    except Exception as e:
        print(f"Errore lettura DB: {e}")
        return []

@app.post("/score")
def add_score(s: Score):
    try:
        conn = psycopg2.connect(DB_URL, sslmode='require')
        cur = conn.cursor()
        # Inserisce il nome (troncato a 12 char per sicurezza grafica) e il punteggio
        safe_name = s.name[:12]
        cur.execute("INSERT INTO scores (name, score) VALUES (%s, %s)", (safe_name, s.score))
        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True}
    except Exception as e:
        print(f"Errore scrittura DB: {e}")
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000)) # Render usa spesso la 10000 di default interno o la env PORT
    uvicorn.run(app, host="0.0.0.0", port=port)a
