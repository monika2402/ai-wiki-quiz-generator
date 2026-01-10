import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Setup logging to file
def log(msg):
    with open("migration_log.txt", "a") as f:
        f.write(msg + "\n")

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    log("DATABASE_URL not found!")
    sys.exit(1)

log(f"Connecting to DB...") # Don't log full URL for security

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        log("Connected.")
        
        # Try adding last_score
        try:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN last_score INTEGER DEFAULT 0"))
            log("Added last_score column.")
        except Exception as e:
            log(f"Error adding last_score: {e}")

        # Try adding high_score
        try:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN high_score INTEGER DEFAULT 0"))
            log("Added high_score column.")
        except Exception as e:
            log(f"Error adding high_score: {e}")

        conn.commit()
        log("Migration committed.")

except Exception as e:
    log(f"Migration fatal error: {e}")
