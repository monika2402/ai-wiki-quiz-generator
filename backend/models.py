from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False)
    title = Column(String(300), nullable=False)

    summary = Column(Text, nullable=True)
    sections = Column(Text, nullable=True)      # stored as JSON string
    quiz_data = Column(Text, nullable=False)     # quiz JSON
    related_topics = Column(Text, nullable=True) # JSON string
    
    last_score = Column(Integer, default=0)
    high_score = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
