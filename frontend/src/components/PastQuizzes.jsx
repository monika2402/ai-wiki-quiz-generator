import { useEffect, useState } from "react";
import "./PastQuizzes.css";

const API_BASE_URL = window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://ai-wiki-quiz-generator-so6x.onrender.com";

function PastQuizzes({ onRetake }) {
    const [quizzes, setQuizzes] = useState([]);
    const [selected, setSelected] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        fetch(`${API_BASE_URL}/quizzes`)
            .then((res) => res.json())
            .then((data) => {
                setQuizzes(data);
                setLoading(false);
            })
            .catch(() => {
                setLoading(false);
            });
    }, []);

    const openDetails = async (id) => {
        const res = await fetch(`${API_BASE_URL}/quizzes/${id}`);
        const data = await res.json();
        setSelected(data);
    };

    const handleRetake = async (id) => {
        // Fetch the full quiz details to retake
        const res = await fetch(`${API_BASE_URL}/quizzes/${id}`);
        const data = await res.json();
        // Pass the data to the parent handler
        if (onRetake) {
            onRetake(data);
        }
    };

    return (
        <div className="past-quizzes-container">
            <h3>Past Quizzes</h3>

            {loading ? (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p className="loading-text">Loading quizzes...</p>
                </div>
            ) : quizzes.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">📚</div>
                    <h4>No Quizzes Yet</h4>
                    <p>Generate your first quiz to get started!</p>
                </div>
            ) : (
                <div className="past-quizzes-grid">
                    {quizzes.map((q) => (
                        <div className="quiz-card" key={q.id}>
                            <h4>{q.title}</h4>
                            <div className="quiz-topic">
                                {q.url ? (
                                    <a href={q.url} target="_blank" rel="noopener noreferrer">
                                        {q.url.length > 40 ? q.url.substring(0, 37) + "..." : q.url}
                                    </a>
                                ) : (
                                    <span>No URL available</span>
                                )}
                            </div>

                            <div className="quiz-info">
                                <p>
                                    <span>Previous Score:</span>
                                    <strong>{q.last_score || "N/A"}</strong>
                                </p>
                                <p>
                                    <span>High Score:</span>
                                    <strong>{q.high_score || "N/A"}</strong>
                                </p>
                            </div>

                            <div className="card-actions">
                                <button className="btn-details" onClick={() => openDetails(q.id)}>
                                    Details
                                </button>
                                <button className="btn-retake" onClick={() => handleRetake(q.id)}>
                                    Retake Quiz
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {selected && (
                <div className="quiz-details-overlay">
                    <div className="quiz-details-modal">
                        <h4>{selected.title}</h4>

                        {selected.quiz.map((q, idx) => (
                            <div key={idx} style={{ marginBottom: "15px", borderBottom: "1px solid #eee", paddingBottom: "10px" }}>
                                <b>Q{idx + 1}:</b> {q.question}
                                <p style={{ margin: "5px 0 0 0", color: "green" }}><b>Answer:</b> {q.answer}</p>
                            </div>
                        ))}

                        <button className="close-btn" onClick={() => setSelected(null)}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default PastQuizzes;
