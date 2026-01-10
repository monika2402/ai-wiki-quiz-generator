import { useState } from "react";
import GenerateQuiz from "./components/GenerateQuiz";
import PastQuizzes from "./components/PastQuizzes";
import quizLogo from "./assets/logo.jpg";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("generate");
  const [retakeData, setRetakeData] = useState(null);

  const handleRetake = (data) => {
    setRetakeData(data);
    setActiveTab("generate");
  };

  return (
    <div className="app-container">
      {/* Header Section */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            <img
              src={quizLogo}
              alt="Quiz Logo"
              className="title-icon title-logo"
            />
            AI Wiki Quiz Generator
          </h1>
          <p className="app-subtitle">Test your knowledge with AI-powered quizzes from Wikipedia</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className="content-wrapper">
          {/* Tabs Navigation */}
          <nav className="tabs-container">
            <button
              onClick={() => { setActiveTab("generate"); setRetakeData(null); }}
              className={`tab-button ${activeTab === "generate" ? "active" : ""}`}
            >
              <span className="tab-icon">✨</span>
              Generate Quiz
            </button>

            <button
              onClick={() => setActiveTab("history")}
              className={`tab-button ${activeTab === "history" ? "active" : ""}`}
            >
              <span className="tab-icon">📖</span>
              Past Quizzes
            </button>
          </nav>

          {/* Content Area */}
          <div className="content-area">
            {activeTab === "generate" ? (
              <GenerateQuiz initialData={retakeData} onReset={() => setRetakeData(null)} />
            ) : (
              <PastQuizzes onRetake={handleRetake} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
