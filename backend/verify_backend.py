from database import SessionLocal
from models import Quiz

def verify():
    db = SessionLocal()
    try:
        quizzes = db.query(Quiz).all()
        print(f"Found {len(quizzes)} quizzes.")
        for q in quizzes:
            print(f"ID: {q.id}, Last Score: {q.last_score}, High Score: {q.high_score}")
    except Exception as e:
        print(f"Error querying quizzes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
