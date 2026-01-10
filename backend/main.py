from fastapi import FastAPI, HTTPException, Depends
import pydantic
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Quiz

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# DB Session Dependency
# -------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------
# Helper: Validate Wikipedia URL
# -------------------------------
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


# -------------------------------
# Helper: Scrape Wikipedia Page
# -------------------------------
def scrape_wikipedia_page(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Wikipedia page")

    soup = BeautifulSoup(response.text, "lxml")

    # Title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "No title found"

    # Summary
    summary = ""
    for p in soup.select("div#mw-content-text p"):
        if p.get_text(strip=True):
            summary = p.get_text(strip=True)
            break

    # Sections
    sections = []
    for header in soup.find_all(["h2", "h3"]):
        headline = header.find("span", class_="mw-headline")
        text = headline.get_text(strip=True) if headline else header.get_text(strip=True)

        if text and text.lower() not in [
            "contents", "references", "external links", "see also"
        ]:
            sections.append(text)

    # Full text
    content_div = soup.find("div", {"id": "mw-content-text"})
    paragraphs = content_div.find_all("p")

    text_content = " ".join(
        [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    )

    return {
        "title": title,
        "summary": summary,
        "sections": sections,
        "text": text_content
    }


# -------------------------------
# Prompt Builder
# -------------------------------
def build_quiz_prompt(title: str, summary: str, sections: list, text: str) -> str:
    return f"""
You are an expert educator.

Create a quiz ONLY from the Wikipedia article below.

RULES:
- No hallucinations
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

Each question:
- question
- options (4)
- answer (exact option)
- explanation (1 sentence)
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


# -------------------------------
# LLM (Groq)
# -------------------------------
def generate_quiz_with_llm(prompt: str):
    api_key = os.getenv("GROQ_API_KEY")
    print("GROQ KEY LOADED:", bool(api_key))

    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key not configured")

    llm = ChatGroq(
        api_key=api_key,
        model="llama-3.1-8b-instant",
        temperature=0.3
    )

    response = llm.invoke(prompt)

    if hasattr(response, "content") and response.content:
        return response.content

    raise HTTPException(status_code=500, detail="Empty response from LLM")


# -------------------------------
# JSON Cleaner
# -------------------------------
def extract_json_from_llm_response(text: str):
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid JSON from LLM")


# -------------------------------
# Root
# -------------------------------
@app.get("/")
def root():
    return {"message": "AI Wiki Quiz Generator API running"}


# -------------------------------
# Generate Quiz (SAVE + CACHE)
# -------------------------------
@app.post("/generate-quiz")
def generate_quiz(url: str, db: Session = Depends(get_db)):
    if not is_valid_wikipedia_url(url):
        raise HTTPException(status_code=400, detail="Invalid Wikipedia URL")

    # 🔁 Check if quiz already exists
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

    # 🧠 Scrape + Generate
    scraped = scrape_wikipedia_page(url)

    prompt = build_quiz_prompt(
        scraped["title"],
        scraped["summary"],
        scraped["sections"],
        scraped["text"]
    )

    ai_response = generate_quiz_with_llm(prompt)
    quiz_data = extract_json_from_llm_response(ai_response)

    # 💾 Save to DB
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

@app.get("/quizzes")
def get_all_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).order_by(Quiz.created_at.desc()).all()

    return [
        {
            "id": q.id,
            "url": q.url,
            "title": q.title,
            "created_at": q.created_at,
            "last_score": q.last_score,
            "high_score": q.high_score
        }
        for q in quizzes
    ]

@app.get("/quizzes/{quiz_id}")
def get_quiz_details(quiz_id: int, db: Session = Depends(get_db)):
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

class ScoreUpdate(pydantic.BaseModel):
    score: int

@app.post("/quizzes/{quiz_id}/score")
def update_quiz_score(quiz_id: int, update: ScoreUpdate, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
        
    quiz.last_score = update.score
    if update.score > quiz.high_score:
        quiz.high_score = update.score
        
    db.commit()
    return {"message": "Score updated", "last_score": quiz.last_score, "high_score": quiz.high_score}
