import sys

def log(msg):
    with open("verify_log_v2.txt", "a") as f:
        f.write(str(msg) + "\n")

log("Starting verification v2...")

try:
    from database import SessionLocal
    from models import Quiz
    log("Imports successful.")
except Exception as e:
    log(f"Import failed: {e}")
    sys.exit(1)

def verify():
    db = SessionLocal()
    try:
        log("Session created.")
        quizzes = db.query(Quiz).all()
        log(f"Found {len(quizzes)} quizzes.")
        for q in quizzes:
            log(f"ID: {q.id}, Last Score: {q.last_score}, High Score: {q.high_score}")
        log("Verification successful.")
    except Exception as e:
        log(f"Error querying quizzes: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
