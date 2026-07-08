/** Fan Assistant — chat UI with multilingual support.
 *
 * Semantic HTML: <section> with aria-labelledby, <form> for input,
 * aria-live region for new messages, aria-busy on send button.
 */

import { type FormEvent, useRef, useState, useEffect } from "react";
import type { ChatMessage } from "../lib/types";
import { LanguageSelector } from "./LanguageSelector";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  error: string;
  onSendMessage: (text: string, language: string) => Promise<void>;
  onSuggestionClick: (text: string, language: string) => Promise<void>;
}

export function FanAssistant({ messages, loading, error, onSendMessage, onSuggestionClick }: Props) {
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("en");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput("");
    void onSendMessage(msg, language);
  };

  return (
    <section className="card chat-container" aria-labelledby="chat-heading">
      <div className="card-header">
        <h2 id="chat-heading">⚽ Fan Assistant</h2>
        <LanguageSelector value={language} onChange={setLanguage} />
      </div>

      {/* Error alert — assertive live region */}
      {error && (
        <div role="alert" aria-live="assertive" className="error-alert">
          {error}
        </div>
      )}

      {/* Messages area */}
      <div
        className="chat-messages"
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
      >
        {messages.length === 0 && (
          <div className="chat-message assistant">
            <p>
              Welcome to MetLife Stadium for the FIFA World Cup 2026! 🏟️
            </p>
            <p style={{ marginTop: "0.5rem", fontSize: "0.88rem", opacity: 0.8 }}>
              Ask me about food, restrooms, your seats, accessibility services,
              transportation, or anything else. I speak 12+ languages!
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-message ${msg.role}`}
            aria-label={`${msg.role === "user" ? "You" : "Assistant"}: ${msg.content}`}
          >
            <p>{msg.content}</p>
            {msg.source && (
              <span className={`source-badge ${msg.source}`}>
                {msg.source === "gemini" ? "✨ AI" : msg.source === "cache" ? "⚡ cached" : "📋 guide"}
              </span>
            )}
            {msg.suggested_actions && msg.suggested_actions.length > 0 && (
              <div className="suggested-actions">
                {msg.suggested_actions.map((action) => (
                  <button
                    key={action}
                    className="suggestion-btn"
                    onClick={() => void onSuggestionClick(action, language)}
                    type="button"
                  >
                    {action}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input form */}
      <form
        className="chat-input-area"
        onSubmit={handleSubmit}
        aria-labelledby="chat-heading"
      >
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about food, directions, accessibility..."
          aria-label="Type your message"
          disabled={loading}
          autoComplete="off"
        />
        <button
          type="submit"
          className="chat-send-btn"
          disabled={loading || !input.trim()}
          aria-busy={loading}
        >
          {loading ? (
            <>
              <span className="loading-spinner" aria-hidden="true" /> Sending…
            </>
          ) : (
            "Send"
          )}
        </button>
      </form>
    </section>
  );
}
