import React, { useEffect, useRef } from "react";
import "./ChatMessages.css";
import type { Message } from "../interfaces/Interfaces";

interface ChatMessagesProps {
  messages: Message[];
}
const ChatMessages: React.FC<ChatMessagesProps> = ({ messages }) => {
  // Référence vers l'élément de fin de messages
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // Scroll automatique vers le dernier message à chaque mise à jour des messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);
  return (
    <div className="chat-messages">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`message-item ${msg.sender === "user" ? "message-user" : "message-bot"}`}
        >
          <div className="message-bubble">{msg.text}</div>
        </div>
      ))}
      {/* Élément de référence pour assurer le scroll vers le bas */}
      <div ref={messagesEndRef} />
    </div>
  );
};
export default ChatMessages;