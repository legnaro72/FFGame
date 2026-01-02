from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Permette al gioco (Web e Locale) di comunicare con il server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Recupera l'URL del database dalle variabili d'ambiente di Render
DATABASE_URL = os.environ.get("DATABASE_URL")

class Score(BaseModel):
    name: str
    score: int

def get_db_connection():
    """Crea una connessione al database PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    """Inizializza la tabella se non esiste"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Nota: In Postgres usiamo SERIAL per l'auto-incremento invece di INTEGER PRIMARY KEY
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                score INTEGER
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database inizializzato correttamente.")
    except Exception as e:
        print(f"Errore inizializzazione DB: {e}")

# Inizializziamo il DB all'avvio
if DATABASE_URL:
    init_db()
else:
    print("ATTENZIONE: DATABASE_URL non trovato nelle variabili d'ambiente!")

@app.get("/leaderboard")
def leaderboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Errore lettura leaderboard: {e}")
        return []

@app.post("/score")
def add_score(s: Score):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # IMPORTANTE: Postgres usa %s invece di ? per i parametri
        cur.execute("INSERT INTO scores (name, score) VALUES (%s, %s)", (s.name[:12], s.score))
        conn.commit()
        cur.close()
        conn.close()
        return {"ok": True}
    except Exception as e:
        print(f"Errore salvataggio score: {e}")
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
