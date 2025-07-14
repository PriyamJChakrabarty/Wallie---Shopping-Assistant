"use client";
import { useState } from "react";

export default function ChatPage() {
  const [listening, setListening] = useState(false);
  const [chat, setChat] = useState([]); // { role: 'user' | 'agent', text: string }

  const handleVoiceInput = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    setListening(true);
    recognition.start();

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      setListening(false);
      addMessage("user", transcript);
      await sendToBackend(transcript);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setListening(false);
    };

    recognition.onend = () => setListening(false);
  };

  const sendToBackend = async (text) => {
    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      const reply = data.reply;
      addMessage("agent", reply);
      speak(reply);
    } catch (err) {
      console.error("Backend error:", err);
    }
  };

  const speak = (text) => {
    if (!text.trim()) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "hi-IN";
    window.speechSynthesis.speak(utterance);
  };

  const addMessage = (role, text) => {
    setChat((prev) => [...prev, { role, text }]);
  };

  return (
    <div style={{
      maxWidth: "700px",
      margin: "2rem auto",
      padding: "1rem",
      fontFamily: "sans-serif",
      border: "1px solid #ddd",
      borderRadius: "8px",
      background: "#fff",
    }}>
      <h1>🛍️ Voice Shopping Chat</h1>
      <p>Press the button and speak in Hinglish. The assistant will respond back.</p>

      <div style={{
        height: "400px",
        overflowY: "auto",
        border: "1px solid #eee",
        padding: "1rem",
        margin: "1rem 0",
        borderRadius: "6px",
        background: "#fdfdfd",
        display: "flex",
        flexDirection: "column",
        gap: "0.75rem"
      }}>
        {chat.map((msg, index) => (
          <div key={index} style={{
            alignSelf: msg.role === "user" ? "flex-start" : "flex-end",
            background: msg.role === "user" ? "#e0f7fa" : "#dcedc8",
            padding: "0.75rem 1rem",
            borderRadius: "16px",
            maxWidth: "70%",
            wordWrap: "break-word",
          }}>
            {msg.text}
          </div>
        ))}
      </div>

      <button
        onClick={handleVoiceInput}
        style={{
          padding: "0.6rem 1.2rem",
          fontSize: "1rem",
          backgroundColor: listening ? "#ccc" : "#0070f3",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}
        disabled={listening}
      >
        {listening ? "🎙️ Listening..." : "🎤 Speak"}
      </button>
    </div>
  );
}
