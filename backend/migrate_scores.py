from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN last_score INTEGER DEFAULT 0"))
            print("Added last_score column")
        except Exception as e:
            print(f"Error adding last_score: {e}")
            
        try:
            conn.execute(text("ALTER TABLE quizzes ADD COLUMN high_score INTEGER DEFAULT 0"))
            print("Added high_score column")
        except Exception as e:
            print(f"Error adding high_score: {e}")
        
        conn.commit()

if __name__ == "__main__":
    migrate()
