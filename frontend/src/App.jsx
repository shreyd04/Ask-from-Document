import { useState } from "react";
import {
  BookOpen,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  FileText,
  Loader2,
  MessageSquare,
  Send,
  ShieldCheck,
  Sparkles,
  Wifi,
  WifiOff,
} from "lucide-react";

import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(null);
  const [expandedSources, setExpandedSources] = useState({});

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);

      if (!response.ok) {
        throw new Error("Backend unavailable");
      }

      setApiOnline(true);
    } catch {
      setApiOnline(false);
    }
  };

  const askQuestion = async (questionText = question) => {
    const cleanQuestion = questionText.trim();

    if (!cleanQuestion || loading) {
      return;
    }

    setLoading(true);

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: cleanQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setQuestion("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: cleanQuestion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "The request could not be completed."
        );
      }

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

      setApiOnline(true);
    } catch (error) {
      setApiOnline(false);

      const errorMessage = {
        id: crypto.randomUUID(),
        role: "error",
        content:
          error.message ||
          "Unable to connect to the Ask My Doc backend.",
      };

      setMessages((previous) => [
        ...previous,
        errorMessage,
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    askQuestion();
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const toggleSource = (messageId, sourceIndex) => {
    const key = `${messageId}-${sourceIndex}`;

    setExpandedSources((previous) => ({
      ...previous,
      [key]: !previous[key],
    }));
  };

  const suggestedQuestions = [
    "What are the main characteristics of Baroque art?",
    "Who were the major artists associated with Baroque art?",
    "How did Baroque art differ from Renaissance art?",
  ];

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            <BookOpen size={21} strokeWidth={1.8} />
          </div>

          <div>
            <div className="brand-name">ASK MY DOC</div>
            <div className="brand-subtitle">
              Baroque Art Research Assistant
            </div>
          </div>
        </div>

        <button
          className={`status-pill ${
            apiOnline === false
              ? "status-offline"
              : "status-online"
          }`}
          onClick={checkHealth}
          type="button"
        >
          {apiOnline === false ? (
            <WifiOff size={14} />
          ) : (
            <Wifi size={14} />
          )}

          {apiOnline === false
            ? "Backend Offline"
            : "System Check"}
        </button>
      </header>

      <main className="main-container">
        {messages.length === 0 ? (
          <section className="welcome-section">
            <div className="hero-icon">
              <Sparkles size={27} strokeWidth={1.7} />
            </div>

            <p className="eyebrow">
              DOMAIN-SPECIFIC DOCUMENT QA
            </p>

            <h1>
              Explore Baroque art
              <br />
              through your documents.
            </h1>

            <p className="hero-description">
              Ask questions about the indexed Baroque art
              collection and receive answers grounded in
              retrieved document evidence.
            </p>

            <div className="trust-row">
              <div className="trust-item">
                <ShieldCheck size={16} />
                <span>Evidence grounded</span>
              </div>

              <div className="trust-item">
                <FileText size={16} />
                <span>Document citations</span>
              </div>

              <div className="trust-item">
                <CheckCircle2 size={16} />
                <span>Retrieval based</span>
              </div>
            </div>

            <div className="suggestions">
              {suggestedQuestions.map((item) => (
                <button
                  key={item}
                  className="suggestion-card"
                  onClick={() => askQuestion(item)}
                  type="button"
                >
                  <MessageSquare size={17} />
                  <span>{item}</span>
                </button>
              ))}
            </div>
          </section>
        ) : (
          <section className="conversation">
            <div className="conversation-heading">
              <div>
                <p className="eyebrow">RESEARCH SESSION</p>
                <h2>Baroque Art Documents</h2>
              </div>

              <span className="message-count">
                {messages.filter(
                  (message) => message.role === "user"
                ).length}{" "}
                questions
              </span>
            </div>

            {messages.map((message) => {
              if (message.role === "user") {
                return (
                  <div
                    className="message-row user-row"
                    key={message.id}
                  >
                    <div className="user-label">YOU</div>

                    <div className="user-message">
                      {message.content}
                    </div>
                  </div>
                );
              }

              if (message.role === "error") {
                return (
                  <div
                    className="error-card"
                    key={message.id}
                  >
                    <WifiOff size={18} />
                    <div>
                      <strong>Request failed</strong>
                      <p>{message.content}</p>
                    </div>
                  </div>
                );
              }

              return (
                <div
                  className="answer-block"
                  key={message.id}
                >
                  <div className="answer-header">
                    <div className="answer-label">
                      <div className="assistant-mark">
                        <BookOpen size={16} />
                      </div>

                      <span>ASK MY DOC</span>
                    </div>

                    <div className="grounded-badge">
                      <CheckCircle2 size={14} />
                      Grounded response
                    </div>
                  </div>

                  <div className="answer-card">
                    <div className="answer-text">
                      {message.content}
                    </div>
                  </div>

                  {message.sources?.length > 0 && (
                    <div className="sources-section">
                      <div className="sources-heading">
                        <div>
                          <p className="eyebrow">
                            RETRIEVED EVIDENCE
                          </p>

                          <h3>
                            Document citations
                          </h3>
                        </div>

                        <span className="source-count">
                          {message.sources.length}{" "}
                          source
                          {message.sources.length !== 1
                            ? "s"
                            : ""}
                        </span>
                      </div>

                      <div className="source-list">
                        {message.sources.map(
                          (source, index) => {
                            const key = `${message.id}-${index}`;
                            const expanded =
                              expandedSources[key];

                            return (
                              <div
                                className="source-card"
                                key={key}
                              >
                                <div className="source-main">
                                  <div className="source-icon">
                                    <FileText
                                      size={17}
                                    />
                                  </div>

                                  <div className="source-info">
                                    <div className="source-document">
                                      {source.document}
                                    </div>

                                    <div className="source-page">
                                      Page {source.page}
                                    </div>
                                  </div>

                                  <button
                                    className="source-toggle"
                                    onClick={() =>
                                      toggleSource(
                                        message.id,
                                        index
                                      )
                                    }
                                    type="button"
                                  >
                                    {expanded ? (
                                      <>
                                        Hide
                                        <ChevronUp
                                          size={16}
                                        />
                                      </>
                                    ) : (
                                      <>
                                        Details
                                        <ChevronDown
                                          size={16}
                                        />
                                      </>
                                    )}
                                  </button>
                                </div>

                                {expanded && (
                                  <div className="source-detail">
                                    <span>
                                      Citation {index + 1}
                                    </span>

                                    <p>
                                      Retrieved from{" "}
                                      <strong>
                                        {source.document}
                                      </strong>{" "}
                                      on page{" "}
                                      <strong>
                                        {source.page}
                                      </strong>
                                      .
                                    </p>
                                  </div>
                                )}
                              </div>
                            );
                          }
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="loading-row">
                <div className="assistant-mark">
                  <Loader2
                    size={17}
                    className="spinner"
                  />
                </div>

                <div>
                  <span>Retrieving evidence...</span>
                  <small>
                    Searching the document collection
                  </small>
                </div>
              </div>
            )}
          </section>
        )}

        <section className="input-section">
          <form
            className="question-form"
            onSubmit={handleSubmit}
          >
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about the Baroque art documents..."
              rows={1}
              disabled={loading}
            />

            <button
              className="send-button"
              type="submit"
              disabled={
                loading || !question.trim()
              }
              aria-label="Ask question"
            >
              {loading ? (
                <Loader2
                  size={19}
                  className="spinner"
                />
              ) : (
                <Send size={19} />
              )}
            </button>
          </form>

          <p className="input-note">
            Answers are generated from the indexed document
            collection and accompanied by available citations.
          </p>
        </section>
      </main>

      <footer className="footer">
        <span>Ask My Doc</span>
        <span>•</span>
        <span>Baroque Art Knowledge Base</span>
      </footer>
    </div>
  );
}

export default App;