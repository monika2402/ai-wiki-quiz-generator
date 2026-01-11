# AI Wiki Quiz Generator

An AI-powered web application that generates interactive quizzes from Wikipedia articles.
Users can generate quizzes, take them one question at a time, get instant feedback, track live score, and view past quizzes — all backed by a real database.

---

## Features

- Generate quizzes from any Wikipedia URL
- One-question-at-a-time Take Quiz mode
- Instant correctness feedback after each answer
- Live score + progress indicator
- Past quizzes stored and retrievable
- AI-generated questions using Groq LLM
- PostgreSQL database (Neon)
- Full-stack app (FastAPI + React)

---

## Tech Stack

### Frontend
- React (Vite)
- JavaScript
- CSS

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL (Neon)
- BeautifulSoup (web scraping)
- Groq LLM (LLaMA 3.1)

### Deployment
- Backend: Render
- Database: Neon
- Frontend: Vercel 

---

## Project Structure

```
ai-wiki-quiz-generator/
│
├── backend/
│ ├── main.py
│ ├── database.py
│ ├── models.py
│ ├── create_tables.py
│ ├── requirements.txt
│ └── .env (ignored)
│
├── frontend/
│ ├── src/
│ ├── public/
│ └── package.json
│
└── README.md
```

---

## Backend Setup (Local)

### 1. Create virtual environment
```bash
python -m venv venv
```

### 2. Activate venv
**Windows**
```bash
venv\Scripts\activate
```
**Mac/Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env


### 5. Create database tables
```bash
python create_tables.py
```

### 6. Run backend
```bash
uvicorn main:app --reload
```
Visit: http://127.0.0.1:8000/docs

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: http://localhost:5173

---

## Backend Deployment (Render)

- **Root Directory:** backend
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
- **Add Environment Variables on Render:**
    - `DATABASE_URL`
    - `GROQ_API_KEY`

---

## API Endpoint

### Generate Quiz
```
POST /generate-quiz?url=<wikipedia_url>
```

**Example:**
`/generate-quiz?url=https://en.wikipedia.org/wiki/Alan_Turing`

---

## Bonus Implemented

- Take Quiz mode (one question per screen)
- Live score & progress
- Final score screen with visual feedback
- Database persistence

---

## Future Improvements

- User authentication
- Timed quizzes
- Difficulty filtering
- Shareable quiz links
- Analytics dashboard

---

## Deployed Links

- **Frontend:** [https://ai-wiki-quiz-generator-nine.vercel.app/](https://ai-wiki-quiz-generator-nine.vercel.app/)
- **Backend:** [https://ai-wiki-quiz-generator-so6x.onrender.com/](https://ai-wiki-quiz-generator-so6x.onrender.com/)

---

## Author

**Monika Reddy**

Built with ❤️ as a full-stack AI project.
