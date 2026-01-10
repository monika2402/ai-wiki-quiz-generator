import { useState } from "react";
import "./Quiz.css";

function Quiz({ quiz }) {
    const [index, setIndex] = useState(0);
    const [selected, setSelected] = useState("");
    const [showFeedback, setShowFeedback] = useState(false);
    const [score, setScore] = useState(0);
    const [finished, setFinished] = useState(false);

    const current = quiz[index];

    const submitAnswer = () => {
        const correct = result.quiz[currentIndex].answer;

        if (selectedOption === correct) {
            setScore((prev) => prev + 1);
        }

        setShowFeedback(true);
    };

    const nextQuestion = () => {
        setShowFeedback(false);
        setSelectedOption("");

        if (currentIndex + 1 < result.quiz.length) {
            setCurrentIndex((prev) => prev + 1);
        } else {
            setFinished(true);
        }
    };

    if (finished) {
        const percentage = Math.round((score / quiz.length) * 100);

        return (
            <div className="final-screen">
                <div className="score-circle">
                    <span>{percentage}%</span>
                </div>
                <h2>Your Score</h2>
                <p>
                    {score} / {quiz.length}
                </p>
            </div>
        );
    }

    return (
        <div className="quiz-wrapper">
            {/* TOP BAR */}
            <div className="top-bar">
                <span>Score: {score}</span>
                <span>
                    {index + 1} / {quiz.length}
                </span>
            </div>

            {/* QUESTION */}
            <div className="question-card">
                <h3>{current.question}</h3>

                {current.options.map((opt, i) => (
                    <label
                        key={i}
                        className={`option ${showFeedback && opt === current.answer ? "correct" : ""
                            } ${showFeedback && selected === opt && opt !== current.answer
                                ? "wrong"
                                : ""
                            }`}
                    >
                        <input
                            type="radio"
                            name="option"
                            checked={selected === opt}
                            disabled={showFeedback}
                            onChange={() => setSelected(opt)}
                        />
                        {opt}
                    </label>
                ))}

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
                        Next
                    </button>
                )}

                {showFeedback && (
                    <p className="feedback">
                        {selected === current.answer ? "Correct ✅" : "Wrong ❌"}
                    </p>
                )}
            </div>
        </div>
    );
}

export default Quiz;
