// frontend/src/components/ChatBox.jsx
import React, { useState, useRef, useEffect } from "react";

const ChatBox = () => {
  const [inputText, setInputText] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Smooth auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async () => {
    if (!inputText.trim()) return;

    const userMessage = { role: "user", content: inputText };
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setLoading(true);

    const BASE_URL =
      process.env.NODE_ENV === "development"
        ? "/chat"
        : "http://127.0.0.1:8000/chat";

    try {
      const response = await fetch(BASE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: inputText }),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Server error ${response.status}: ${errText}`);
      }

      const data = await response.json();
      const aiMessage = { role: "ai", content: data.answer };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("[DEBUG] Fetch error:", err);
      const errorMsg = {
        role: "ai",
        content: `⚠️ Error: Could not fetch. ${
          err.message.includes("Failed to fetch")
            ? "Check server/CORS."
            : err.message
        }`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="chat-container">
      {/* Header Branding - Fixed Alignment & Visibility */}
      <div className="header-bar">
        <div className="header-left">
          <div className="header-title">🤖 AI Research Mentor</div>
        </div>
        <div className="header-right">
          <div className="header-sub">
        
            <br />
         
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`message-row ${msg.role === "user" ? "user" : "ai"}`}
            style={{
              animationDelay: `${idx * 0.08}s`,
            }}
          >
            <div className={`message-bubble ${msg.role}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="loading-row">
            <div className="dots">
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </div>
            <span>AI is crafting your response...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-area">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about AI, code, RAG, or anything on your mind... 🚀"
        />
        <button onClick={send} disabled={loading || !inputText.trim()}>
          {loading ? (
            <span className="loading-btn">
              <div className="spinner" />
              Sending...
            </span>
          ) : (
            "Send 🚀"
          )}
        </button>
      </div>

      {/* Health Check */}
      <div className="health-check">
        <button
          onClick={async () => {
            try {
              const res = await fetch(
                process.env.NODE_ENV === "development"
                  ? "/health"
                  : "http://127.0.0.1:8000/health"
              );
              console.log("[DEBUG] Health check:", await res.text());
              alert("✅ Backend is healthy!");
            } catch (e) {
              console.error("[DEBUG] Health check failed:", e);
              alert("⚠️ Backend check failed — check console.");
            }
          }}
        >
          🔍 Test Backend Health
        </button>
      </div>

      <style>{`
        .chat-container {
          position: relative;
          max-width: 800px;
          width: 90%;
          margin: 60px auto;
          display: flex;
          flex-direction: column;
          gap: 20px;
          padding: 28px;
          border-radius: 24px;
          background: linear-gradient(145deg, #0d0d0d, #1b1b1b 60%, #2d2d2d);
          color: #d3d3d3;
          box-shadow: 0 25px 50px rgba(0, 0, 0, 0.55),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
          transition: all 0.3s ease;
          min-height: 720px;
        }

        /* Header - Fixed: Split left/right for better alignment, no hiding */
        .header-bar {
          position: absolute;
          top: -25px;
          left: 20px;
          right: 20px;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          background: linear-gradient(90deg, #1e3c72, #2a5298);
          padding: 14px 22px;
          border-radius: 14px 14px 0 0;
          box-shadow: 0 6px 14px rgba(30, 60, 114, 0.4);
          gap: 20px;
        }
        .header-left {
          flex: 1;
          min-width: 0; /* Prevents overflow */
        }
        .header-title {
          font-size: 22px;
          font-weight: bold;
          color: #fff;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .header-right {
          flex: 1;
          display: flex;
          justify-content: flex-end;
          min-width: 0; /* Allows wrapping if needed */
        }
        .header-sub {
          font-size: 13px;
          color: #cce5ff;
          text-align: right;
          line-height: 1.4;
          max-width: 100%;
          word-wrap: break-word;
        }
        .header-name {
          display: block; /* Ensures full visibility, no inline hiding */
          font-size: 17px;
          color: #ffffff;
          letter-spacing: 0.5px;
          font-weight: bold;
          margin-bottom: 4px;
          white-space: normal; /* Allows wrapping if screen small */
        }
        .header-tagline {
          display: block;
          font-size: 12px;
          opacity: 0.9;
          line-height: 1.3;
        }

        /* Messages */
        .messages-container {
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 18px;
          padding: 24px;
          min-height: 470px;
          max-height: 600px;
          overflow-y: auto;
          background: linear-gradient(
            to bottom,
            rgba(20, 20, 20, 0.95),
            rgba(45, 45, 45, 0.85)
          );
          box-shadow: inset 0 4px 10px rgba(0, 0, 0, 0.3),
            0 8px 18px rgba(0, 0, 0, 0.25);
          backdrop-filter: blur(10px);
        }
        .message-row {
          display: flex;
          margin-bottom: 18px;
          opacity: 0;
          animation: fadeInUp 0.3s ease forwards;
        }
        .message-row.user {
          justify-content: flex-end;
        }
        .message-bubble {
          padding: 18px 26px;
          border-radius: 22px;
          max-width: 75%;
          word-break: break-word;
          font-size: 16px;
          line-height: 1.6;
          border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .message-bubble.user {
          background: linear-gradient(135deg, #00b4ff, #007bff);
          box-shadow: 0 8px 22px rgba(0, 180, 255, 0.3);
          border-radius: 22px 22px 0 22px;
        }
        .message-bubble.ai {
          background: linear-gradient(135deg, #3e3e3e, #2b2b2b);
          box-shadow: 0 6px 18px rgba(255, 255, 255, 0.05);
          border-radius: 22px 22px 22px 0;
        }

        .loading-row {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          padding: 20px 0;
          font-size: 16px;
          color: #aaa;
          font-style: italic;
        }
        .dots span {
          animation: blink 1.4s infinite;
          margin: 0 1px;
        }

        /* Input Area */
        .input-area {
          display: flex;
          gap: 14px;
          background: linear-gradient(135deg, #1f1f1f, #2a2a2a, #3c3c3c);
          padding: 18px;
          border-radius: 20px;
          border: 1px solid rgba(255, 255, 255, 0.05);
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
          flex-wrap: wrap;
        }
        .input-area textarea {
          flex: 1;
          padding: 18px 22px;
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          min-height: 70px;
          font-size: 16px;
          resize: none;
          outline: none;
          background: linear-gradient(135deg, #2b2b2b, #1e1e1e);
          color: #f1f1f1;
          caret-color: #00ffcc;
        }
        .input-area button {
          padding: 0 34px;
          height: 70px;
          border-radius: 16px;
          border: none;
          font-weight: bold;
          font-size: 16px;
          cursor: pointer;
          background: linear-gradient(135deg, #00ffcc, #00b894);
          color: #000;
          box-shadow: 0 8px 24px rgba(0, 255, 204, 0.35);
          transition: all 0.3s ease;
        }
        .input-area button:disabled {
          background: linear-gradient(135deg, #555, #333);
          cursor: not-allowed;
          box-shadow: none;
        }

        /* Health Check */
        .health-check {
          text-align: right;
          opacity: 0.8;
        }
        .health-check button {
          padding: 10px 22px;
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.15);
          background: linear-gradient(135deg, #28a745, #20c997);
          color: #fff;
          font-size: 14px;
          cursor: pointer;
          box-shadow: 0 5px 14px rgba(40, 167, 69, 0.35);
        }

        /* Animations */
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes blink {
          0%, 80%, 100% {
            opacity: 0.3;
          }
          40% {
            opacity: 1;
          }
        }
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
        .messages-container::-webkit-scrollbar {
          width: 8px;
        }
        .messages-container::-webkit-scrollbar-thumb {
          background: linear-gradient(#666, #333);
          border-radius: 4px;
        }

        /* 📱 Mobile Responsive - Enhanced for Header Visibility */
        @media (max-width: 768px) {
          .chat-container {
            width: 95%;
            padding: 20px;
            min-height: 90vh;
          }
          .header-bar {
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 8px;
            padding: 12px 16px;
          }
          .header-left,
          .header-right {
            flex: none;
            width: 100%;
          }
          .header-title {
            font-size: 18px;
          }
          .header-sub {
            font-size: 12px;
            text-align: center;
            line-height: 1.3;
          }
          .header-name {
            font-size: 16px; /* Slightly smaller but fully visible */
            display: block;
            margin-bottom: 2px;
          }
          .header-tagline {
            font-size: 11px;
          }
          .input-area {
            flex-direction: column;
          }
          .input-area textarea {
            font-size: 15px;
            min-height: 60px;
          }
          .input-area button {
            width: 100%;
            height: 56px;
            font-size: 15px;
          }
        }

        @media (max-width: 480px) {
          .chat-container {
            margin: 20px auto;
            padding: 16px;
          }
          .header-title {
            font-size: 16px;
          }
          .header-name {
            font-size: 15px;
          }
          .header-sub {
            font-size: 11px;
          }
          .header-tagline {
            font-size: 10px;
            line-height: 1.2;
          }
          .message-bubble {
            font-size: 15px;
            padding: 14px 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatBox;