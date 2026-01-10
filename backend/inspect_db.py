from database import engine
from sqlalchemy import inspect

def check_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('quizzes')
    print("Existing columns in 'quizzes' table:")
    for col in columns:
        print(f"- {col['name']} ({col['type']})")

if __name__ == "__main__":
    try:
        check_schema()
    except Exception as e:
        print(f"Error inspecting DB: {e}")
