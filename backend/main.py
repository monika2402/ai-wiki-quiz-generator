from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pydantic
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq

from database import SessionLocal
from models import Quiz

load_dotenv()

app = FastAPI()

# -----------------------------------
# ✅ CORS (FIXED FOR VERCEL + LOCAL)
# -----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-wiki-quiz-generator-nine.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# DB Session Dependency
# -----------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------
# Helper: Validate Wikipedia URL
# -----------------------------------
def is_valid_wikipedia_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ["http", "https"]
            and "wikipedia.org" in parsed.netloc
            and parsed.path.startswith("/wiki/")
        )
    except:
        return False

# -----------------------------------
# Helper: Scrape Wikipedia Page
# -----------------------------------
def scrape_wikipedia_page(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Wikipedia page")

    soup = BeautifulSoup(response.text, "lxml")

    # Title
    title = soup.find("h1").get_text(strip=True)

    # Summary
    summary = ""
    for p in soup.select("div#mw-content-text p"):
        if p.get_text(strip=True):
            summary = p.get_text(strip=True)
            break

    # Sections
    sections = []
    for h in soup.find_all(["h2", "h3"]):
        span = h.find("span", class_="mw-headline")
        text = span.get_text(strip=True) if span else h.get_text(strip=True)
        if text.lower() not in ["references", "external links", "see also", "contents"]:
            sections.append(text)

    # Full text
    content_div = soup.find("div", id="mw-content-text")
    paragraphs = content_div.find_all("p")
    text_content = " ".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    return {
        "title": title,
        "summary": summary,
        "sections": sections,
        "text": text_content
    }

# -----------------------------------
# Prompt Builder
# -----------------------------------
def build_quiz_prompt(title, summary, sections, text):
    return f"""
You are an expert educator.

Create a quiz ONLY from the Wikipedia article below.

RULES:
- Output VALID JSON ONLY
- No markdown
- No extra text

TITLE:
{title}

SUMMARY:
{summary}

SECTIONS:
{sections}

CONTENT:
{text[:4000]}

TASK:
Generate exactly 5 MCQs.

Each question must include:
- question
- options (4)
- answer
- explanation
- difficulty (easy | medium | hard)

Also include:
- related_topics (3–5)

OUTPUT FORMAT:
{{
  "quiz": [
    {{
      "question": "",
      "options": ["", "", "", ""],
      "answer": "",
      "difficulty": "",
      "explanation": ""
    }}
  ],
  "related_topics": []
}}
"""

# -----------------------------------
# LLM (Groq)
# -----------------------------------
def generate_quiz_with_llm(prompt: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key missing")

    llm = ChatGroq(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0.3
    )

    response = llm.invoke(prompt)
    return response.content

# -----------------------------------
# JSON Cleaner
# -----------------------------------
def extract_json(text: str):
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except:
        raise HTTPException(status_code=500, detail="Invalid JSON from LLM")

# -----------------------------------
# Root
# -----------------------------------
@app.get("/")
def root():
    return {"message": "AI Wiki Quiz Generator API running"}

# -----------------------------------
# Generate Quiz (CACHE + SAVE)
# -----------------------------------
@app.post("/generate-quiz")
def generate_quiz(url: str, db: Session = Depends(get_db)):
    if not is_valid_wikipedia_url(url):
        raise HTTPException(status_code=400, detail="Invalid Wikipedia URL")

    # Cache check
    existing = db.query(Quiz).filter(Quiz.url == url).first()
    if existing:
        return {
            "id": existing.id,
            "url": existing.url,
            "title": existing.title,
            "summary": existing.summary,
            "sections": json.loads(existing.sections),
            "quiz": json.loads(existing.quiz_data),
            "related_topics": json.loads(existing.related_topics)
        }

    scraped = scrape_wikipedia_page(url)
    prompt = build_quiz_prompt(
        scraped["title"],
        scraped["summary"],
        scraped["sections"],
        scraped["text"]
    )

    ai_response = generate_quiz_with_llm(prompt)
    quiz_data = extract_json(ai_response)

    new_quiz = Quiz(
        url=url,
        title=scraped["title"],
        summary=scraped["summary"],
        sections=json.dumps(scraped["sections"]),
        quiz_data=json.dumps(quiz_data["quiz"]),
        related_topics=json.dumps(quiz_data["related_topics"])
    )

    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return {
        "id": new_quiz.id,
        "url": new_quiz.url,
        "title": new_quiz.title,
        "summary": new_quiz.summary,
        "sections": scraped["sections"],
        "quiz": quiz_data["quiz"],
        "related_topics": quiz_data["related_topics"]
    }

# -----------------------------------
# Get All Quizzes
# -----------------------------------
@app.get("/quizzes")
def get_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).order_by(Quiz.created_at.desc()).all()
    return [
        {
            "id": q.id,
            "title": q.title,
            "created_at": q.created_at,
            "last_score": q.last_score,
            "high_score": q.high_score
        }
        for q in quizzes
    ]

# -----------------------------------
# Get Quiz Details
# -----------------------------------
@app.get("/quizzes/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {
        "id": quiz.id,
        "url": quiz.url,
        "title": quiz.title,
        "summary": quiz.summary,
        "sections": json.loads(quiz.sections),
        "quiz": json.loads(quiz.quiz_data),
        "related_topics": json.loads(quiz.related_topics),
        "created_at": quiz.created_at,
        "last_score": quiz.last_score,
        "high_score": quiz.high_score
    }

# -----------------------------------
# Update Score
# -----------------------------------
class ScoreUpdate(pydantic.BaseModel):
    score: int

@app.post("/quizzes/{quiz_id}/score")
def update_score(quiz_id: int, data: ScoreUpdate, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz.last_score = data.score
    quiz.high_score = max(quiz.high_score, data.score)
    db.commit()

    return {
        "message": "Score updated",
        "last_score": quiz.last_score,
        "high_score": quiz.high_score
    }
