import { useState, useEffect } from "react";
import "./GenerateQuiz.css";

function GenerateQuiz({ initialData, onReset }) {
    const [url, setUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedOption, setSelectedOption] = useState("");
    const [showFeedback, setShowFeedback] = useState(false);
    const [score, setScore] = useState(0);
    const [finished, setFinished] = useState(false);
    const [quizStarted, setQuizStarted] = useState(false);
    const [shuffledOptions, setShuffledOptions] = useState([]);

    // Shuffle function (Fisher-Yates algorithm)
    const shuffleArray = (array) => {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    };

    // Shuffle options when question changes
    useEffect(() => {
        if (result && result.quiz && result.quiz[currentIndex]) {
            const shuffled = shuffleArray(result.quiz[currentIndex].options);
            setShuffledOptions(shuffled);
        }
    }, [currentIndex, result]);

    // Initialize with existing data if provided
    if (initialData && !quizStarted && !result) {
        setResult(initialData);
        setQuizStarted(true);
        // If the API returns the original URL, we can set it too
        if (initialData.url) setUrl(initialData.url);
    }

    const generateQuiz = async () => {
        if (!url) return;

        setLoading(true);
        setError("");
        setResult(null);
        setCurrentIndex(0);
        setSelectedOption("");
        setShowFeedback(false);
        setScore(0);
        setFinished(false);
        if (onReset) onReset(); // Clear parent retake data if any

        try {
            const res = await fetch(
                `http://127.0.0.1:8000/generate-quiz?url=${encodeURIComponent(url)}`,
                { method: "POST" }
            );
            const data = await res.json();
            setResult(data);
            setQuizStarted(true);
        } catch {
            setError("Something went wrong. Check backend.");
        } finally {
            setLoading(false);
        }
    };

    const submitAnswer = () => {
        const correct = result.quiz[currentIndex].answer;

        if (selectedOption === correct) {
            setScore((prev) => prev + 1);
        }

        setShowFeedback(true);
    };

    const saveScore = async (finalScore) => {
        if (!result || !result.id) return;
        try {
            await fetch(`http://127.0.0.1:8000/quizzes/${result.id}/score`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ score: finalScore })
            });
            console.log("Score saved!");
        } catch (err) {
            console.error("Failed to save score:", err);
        }
    };

    const nextQuestion = () => {
        setShowFeedback(false);
        setSelectedOption("");

        if (currentIndex + 1 < result.quiz.length) {
            setCurrentIndex((prev) => prev + 1);
        } else {
            setFinished(true);
            saveScore(score);
        }
    };

    /* ================= FINAL SCORE SCREEN ================= */
    if (finished && result) {
        const percentage = Math.round((score / result.quiz.length) * 100);

        // Get personalized message based on score
        const getMessage = (percent) => {
            if (percent === 100) {
                return {
                    title: "Perfect Score! 🎉",
                    message: "Outstanding! You've mastered this topic completely!",
                    emoji: "🌟"
                };
            } else if (percent >= 90) {
                return {
                    title: "Excellent Work! 👏",
                    message: "You're doing amazingly well! Keep up the great work!",
                    emoji: "🚀"
                };
            } else if (percent >= 75) {
                return {
                    title: "Great Job! 💪",
                    message: "You have a solid understanding of this topic!",
                    emoji: "✨"
                };
            } else if (percent >= 60) {
                return {
                    title: "Good Effort! 👍",
                    message: "You're on the right track! A bit more practice will help!",
                    emoji: "📚"
                };
            } else if (percent >= 40) {
                return {
                    title: "Keep Learning! 💡",
                    message: "Don't give up! Review the material and try again!",
                    emoji: "🎯"
                };
            } else {
                return {
                    title: "Keep Trying! 💪",
                    message: "Every expert was once a beginner. You've got this!",
                    emoji: "🌱"
                };
            }
        };

        const resultMessage = getMessage(percentage);

        return (
            <div className="final-score-screen">
                <div className="result-emoji">{resultMessage.emoji}</div>
                <div className="score-circle">{percentage}%</div>
                <h2>{resultMessage.title}</h2>
                <p className="score-fraction">
                    {score} / {result.quiz.length}
                </p>
                <p className="result-message">{resultMessage.message}</p>
            </div>
        );
    }

    return (
        <div className="quiz-container">

            {/* ========== PRE-QUIZ SCREEN ========== */}
            {!quizStarted && (
                <>
                    <h2>Generate Quiz</h2>

                    <div className="url-box">
                        <input
                            type="text"
                            placeholder="Enter Wikipedia URL"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                        />
                        <button onClick={generateQuiz}>Take Quiz</button>
                    </div>

                    {loading && <p>Generating quiz...</p>}
                    {error && <p className="error">{error}</p>}
                </>
            )}

            {/* ========== QUIZ MODE ========== */}
            {quizStarted && result && !finished && (
                <>
                    {/* TOP RIGHT SCORE */}
                    <div className="score-bar">
                        <span>Score: {score}</span>
                        <span>
                            {currentIndex + 1} / {result.quiz.length}
                        </span>
                    </div>

                    {/* QUESTION CARD */}
                    <div className="generate-quiz-card">
                        <h3>
                            Q{currentIndex + 1}. {result.quiz[currentIndex].question}
                        </h3>

                        {shuffledOptions.map((opt, i) => (
                            <label
                                key={i}
                                className={`option ${showFeedback && opt === result.quiz[currentIndex].answer
                                    ? "correct"
                                    : ""
                                    } ${showFeedback &&
                                        selectedOption === opt &&
                                        opt !== result.quiz[currentIndex].answer
                                        ? "wrong"
                                        : ""
                                    }`}
                            >
                                <input
                                    type="radio"
                                    name="option"
                                    checked={selectedOption === opt}
                                    disabled={showFeedback}
                                    onChange={() => setSelectedOption(opt)}
                                />
                                {opt}
                            </label>
                        ))}

                        {/* BUTTON LOGIC */}
                        {!showFeedback ? (
                            <button
                                className="submit-btn"
                                disabled={!selectedOption}
                                onClick={submitAnswer}
                            >
                                Submit
                            </button>
                        ) : (
                            <button className="submit-btn" onClick={nextQuestion}>
                                {currentIndex + 1 === result.quiz.length
                                    ? "Finish"
                                    : "Next"}
                            </button>
                        )}

                        {showFeedback && (
                            <p className="feedback">
                                {selectedOption === result.quiz[currentIndex].answer
                                    ? "Correct ✅"
                                    : "Wrong ❌"}
                            </p>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}

export default GenerateQuiz;
