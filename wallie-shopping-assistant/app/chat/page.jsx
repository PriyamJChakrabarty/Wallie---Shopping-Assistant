"use client";
import { useState } from "react";

export default function ChatPage() {
  const [spokenText, setSpokenText] = useState("");
  const [listening, setListening] = useState(false);

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert("Speech recognition not supported in this browser.");
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = 'en-IN';      // 👈 best for Hinglish in English alphabet
    recognition.continuous = false;
    recognition.interimResults = false;

    setListening(true);
    recognition.start();

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setSpokenText(transcript);
      setListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error', event.error);
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
    };
  };

  return (
    <div style={{
      maxWidth: "600px",
      margin: "2rem auto",
      padding: "1rem",
      fontFamily: "sans-serif",
      border: "1px solid #ddd",
      borderRadius: "8px"
    }}>
      <h1>🎤 Hinglish Voice to Text</h1>
      <p>Press the button and speak in Hinglish (Hindi in English alphabet). Your words will appear below.</p>

      <button
        onClick={handleVoiceInput}
        style={{
          padding: "0.5rem 1rem",
          fontSize: "1rem",
          backgroundColor: listening ? "#ccc" : "#0070f3",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}
        disabled={listening}
      >
        {listening ? "Listening..." : "🎤 Speak Hinglish"}
      </button>

      <div style={{
        marginTop: "2rem",
        padding: "1rem",
        background: "#f9f9f9",
        border: "1px solid #eee",
        borderRadius: "4px",
        minHeight: "100px"
      }}>
        {spokenText
          ? <p>{spokenText}</p>
          : <p style={{ color: "#888" }}>Your speech will appear here.</p>
        }
      </div>
    </div>
  );
}
