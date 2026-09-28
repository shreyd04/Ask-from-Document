import { useEffect, useState } from "react";
import {
  BookOpen,
  Wifi,
  WifiOff,
  Send,
  LoaderCircle,
  AlertCircle,
} from "lucide-react";

import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);

  const checkBackend = async () => {
    if (!API_URL) {
      console.error("VITE_API_URL is not configured.");
      setBackendOnline(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/health`);

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      const data = await response.json();

      setBackendOnline(data.status === "healthy");
    } catch (error) {
      console.error("Backend health check failed:", error);
      setBackendOnline(false);
    }
  };

  useEffect(() => {
    checkBackend();
  }, []);

  const askQuestion = async (event) => {
    event?.preventDefault();

    // IMPORTANT:
    // Capture the question BEFORE changing/clearing state.
    const currentQuestion = question.trim();

    if (!currentQuestion) {
      return;
    }

    if (!API_URL) {
      setMessages((previous) => [
        ...previous,
        {
          type: "error",
          message: "Backend URL is not configured.",
        },
      ]);

      return;
    }

    // Add user's question immediately.
    setMessages((previous) => [
      ...previous,
      {
        type: "user",
        question: currentQuestion,
      },
    ]);

    // Clear input only AFTER saving the question.
    setQuestion("");

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: currentQuestion,
        }),
      });

      const contentType = response.headers.get("content-type") || "";

      let data;

      if (contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const text = await response.text();

        throw new Error(
          `Backend returned non-JSON response (${response.status}): ${text}`
        );
      }

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Request failed with status ${response.status}`
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          type: "answer",
          answer: data.answer,
          sources: data.sources || [],
        },
      ]);

      setBackendOnline(true);
    } catch (error) {
      console.error("Ask request failed:", error);

      setMessages((previous) => [
        ...previous,
        {
          type: "error",
          message: error.message || "Request failed.",
        },
      ]);

      // Only mark offline for actual connection/server failures.
      if (
        error.message?.includes("Failed to fetch") ||
        error.message?.includes("NetworkError") ||
        error.message?.includes("503") ||
        error.message?.includes("502")
      ) {
        setBackendOnline(false);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion(event);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <BookOpen size={28} strokeWidth={2} />
          </div>

          <div>
            <div className="brand-name">ASK MY DOC</div>
            <div className="brand-subtitle">
              Baroque Art Research Assistant
            </div>
          </div>
        </div>

        <div
          className={`system-status ${
            backendOnline ? "online" : "offline"
          }`}
        >
          {backendOnline ? (
            <>
              <Wifi size={17} />
              <span>System Check</span>
            </>
          ) : (
            <>
              <WifiOff size={17} />
              <span>Backend Offline</span>
            </>
          )}
        </div>
      </header>

      <main className="main">
        <section className="research-header">
          <div>
            <div className="eyebrow">RESEARCH SESSION</div>

            <h1>Baroque Art Documents</h1>
          </div>

          <div className="question-count">
            {messages.filter((message) => message.type === "user").length}{" "}
            questions
          </div>
        </section>

        <section className="conversation">
          {messages.map((message, index) => {
            if (message.type === "user") {
              return (
                <div className="message-row user-row" key={index}>
                  <div className="message-label">YOU</div>

                  <div className="user-message">
                    {message.question}
                  </div>
                </div>
              );
            }

            if (message.type === "answer") {
              return (
                <div className="answer-card" key={index}>
                  <div className="answer-label">ASK MY DOC</div>

                  <div className="answer-text">
                    {message.answer}
                  </div>

                  {message.sources.length > 0 && (
                    <div className="sources-section">
                      <div className="sources-title">
                        SOURCES
                      </div>

                      <div className="sources-list">
                        {message.sources.map((source, sourceIndex) => (
                          <div
                            className="source-item"
                            key={sourceIndex}
                          >
                            <BookOpen size={15} />

                            <span>
                              {source.document}
                              {" — "}
                              Page {source.page}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            }

            if (message.type === "error") {
              return (
                <div className="error-card" key={index}>
                  <AlertCircle size={19} />

                  <div>
                    <strong>Request failed</strong>

                    <p>{message.message}</p>
                  </div>
                </div>
              );
            }

            return null;
          })}

          {loading && (
            <div className="retrieving">
              <div className="retrieving-icon">
                <LoaderCircle
                  size={21}
                  className="spin"
                />
              </div>

              <div>
                <strong>Retrieving evidence...</strong>

                <span>
                  Searching the document collection
                </span>
              </div>
            </div>
          )}
        </section>

        <form
          className="question-form"
          onSubmit={askQuestion}
        >
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about the Baroque art documents..."
            disabled={loading}
            rows={1}
          />

          <button
            type="submit"
            disabled={!question.trim() || loading}
            aria-label="Ask question"
          >
            {loading ? (
              <LoaderCircle
                size={22}
                className="spin"
              />
            ) : (
              <Send size={22} />
            )}
          </button>
        </form>

        <div className="disclaimer">
          Answers are generated from the indexed document collection
          and accompanied by available citations.
        </div>
      </main>

      <footer>
        Ask My Doc&nbsp;&nbsp;•&nbsp;&nbsp; Baroque Art Knowledge Base
      </footer>
    </div>
  );
}

export default App;