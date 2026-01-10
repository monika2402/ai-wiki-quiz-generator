import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def log(msg):
    with open("migration_log_v2.txt", "a") as f:
        f.write(msg + "\n")

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    
    # Add last_score
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN last_score INTEGER DEFAULT 0"))
            conn.commit()
            log("Added last_score column and committed.")
    except Exception as e:
        log(f"last_score: {e}")

    # Add high_score
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN high_score INTEGER DEFAULT 0"))
            conn.commit()
            log("Added high_score column and committed.")
    except Exception as e:
        log(f"high_score: {e}")

except Exception as e:
    log(f"Fatal: {e}")
