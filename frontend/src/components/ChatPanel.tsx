"use client";

import { Bot, Send, X } from "lucide-react";
import { FormEvent, useState, useTransition } from "react";

import { chatWithDataset } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

type ChatPanelProps = {
  datasetId: string;
  suggestions: string[];
  isOpen: boolean;
  onToggle: () => void;
};

export function ChatPanel({
  datasetId,
  suggestions,
  isOpen,
  onToggle,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Ask me about your data. I can answer row counts, averages, trends, anomalies, and business-oriented questions.",
    },
  ]);
  const [question, setQuestion] = useState("");
  const [isPending, startTransition] = useTransition();

  const submitQuestion = (nextQuestion: string) => {
    const trimmed = nextQuestion.trim();
    if (!trimmed) return;

    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setQuestion("");

    startTransition(async () => {
      try {
        const response = await chatWithDataset(datasetId, trimmed);
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content: `${response.answer}\n\n${response.reasoning}`,
          },
        ]);
      } catch (error) {
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content:
              error instanceof Error ? error.message : "Unable to answer right now.",
          },
        ]);
      }
    });
  };

  return (
    <>
      <button
        type="button"
        className="floating-chat-button"
        onClick={onToggle}
        aria-expanded={isOpen}
        aria-controls="ai-chat-widget"
      >
        <span className="floating-chat-glow" />
        <Bot size={18} />
        Chat with AI
      </button>

      {isOpen && <div className="chat-overlay" onClick={onToggle} />}

      <section
        className={`chat-widget ${isOpen ? "open" : ""}`}
        id="ai-chat-widget"
      >
        <div className="chat-widget-header">
          <div>
            <p className="eyebrow">AI Copilot</p>
            <h2>Chat with your dataset</h2>
          </div>
          <button
            type="button"
            className="chat-close-button"
            onClick={onToggle}
            aria-label="Close AI chat"
          >
            <X size={18} />
          </button>
        </div>

        <div className="suggestion-row compact">
          {suggestions.map((item) => (
            <button
              key={item}
              type="button"
              className="pill-button"
              onClick={() => submitQuestion(item)}
            >
              {item}
            </button>
          ))}
        </div>

        <div className="chat-shell">
          {messages.map((message, index) => (
            <article
              key={`${message.role}-${index}`}
              className={`chat-bubble ${message.role}`}
            >
              <span>{message.role === "assistant" ? "AI" : "You"}</span>
              <p>{message.content}</p>
            </article>
          ))}
          {isPending && (
            <div className="chat-bubble assistant pending">Thinking...</div>
          )}
        </div>

        <form
          className="chat-form"
          onSubmit={(event: FormEvent) => {
            event.preventDefault();
            submitQuestion(question);
          }}
        >
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about totals, top segments, anomalies, or trends..."
          />
          <button type="submit" disabled={isPending}>
            <Send size={16} />
            Send
          </button>
        </form>
      </section>
    </>
  );
}
