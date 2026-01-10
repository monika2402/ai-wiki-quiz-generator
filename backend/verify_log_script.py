from database import SessionLocal
from models import Quiz

def log(msg):
    with open("verify_log.txt", "a") as f:
        f.write(msg + "\n")

def verify():
    db = SessionLocal()
    try:
        quizzes = db.query(Quiz).all()
        log(f"Found {len(quizzes)} quizzes.")
        for q in quizzes:
            log(f"ID: {q.id}, Last Score: {q.last_score}, High Score: {q.high_score}")
    except Exception as e:
        log(f"Error querying quizzes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
