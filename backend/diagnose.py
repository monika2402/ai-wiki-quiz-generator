import sys

def log(msg):
    try:
        with open("diagnose_log.txt", "a") as f:
            f.write(str(msg) + "\n")
    except:
        pass

log("Starting diagnosis...")
log(f"Python executable: {sys.executable}")

try:
    import sqlalchemy
    log("Imported sqlalchemy")
except ImportError as e:
    log(f"Failed to import sqlalchemy: {e}")

try:
    import dotenv
    log("Imported dotenv")
except ImportError as e:
    log(f"Failed to import dotenv: {e}")

try:
    import database
    log("Imported database module")
except Exception as e:
    log(f"Failed to import database: {e}")

try:
    import models
    log("Imported models")
except Exception as e:
    log(f"Failed to import models: {e}")

log("Diagnosis complete.")
