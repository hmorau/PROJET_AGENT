import React, { useState, useRef } from "react";
import TextareaAutosize from "react-textarea-autosize";
import "./ChatInput.css";

interface ChatInputProps {
  onSend: (message: string, file?: File) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend }) => {
  const [message, setMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const handleSubmit = (e: React.FormEvent | React.KeyboardEvent) => {
    e.preventDefault();
    if (message.trim() !== "" || selectedFile) {
      onSend(message, selectedFile || undefined);
      setMessage("");
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };
  // Gestion de l'appui sur entrée
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Si 'Enter' est pressé sans 'Shift' => envoyer le message
    if (e.key === "Enter" && !e.shiftKey) {
      handleSubmit(e);
    }
  };
  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <TextareaAutosize
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Tapez un message..."
        className="chat-input-input"
        minRows={1}
        style={{ resize: "none" }} // Désactive le redimensionnement manuel
      />
      <div className="chat-input-button-row">
        <div className="chat-input-file">
          <input
            type="file"
            id="fileUpload"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <button
            type="button"
            className="file-upload-btn"
            onClick={() => fileInputRef.current?.click()}
          >
            Joindre un document
          </button>
          {selectedFile && (
            <span className="file-name">{selectedFile.name}</span>
          )}
        </div>
        <button type="submit" className="chat-input-button">
          Envoyer
        </button>
      </div>
    </form>
  );
};
export default ChatInput;