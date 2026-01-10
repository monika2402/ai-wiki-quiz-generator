import sys

def log(msg):
    with open("diagnose_pydantic.txt", "a") as f:
        f.write(str(msg) + "\n")

log("Checking pydantic...")
try:
    import pydantic
    log(f"Imported pydantic: {pydantic.VERSION}")
except Exception as e:
    log(f"Failed to import pydantic: {e}")
