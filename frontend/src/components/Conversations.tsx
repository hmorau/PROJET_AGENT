import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Conversation } from "../interfaces/Interfaces";
import { getConversations, deleteConversation } from "../services/ConversationService"
import './Conversations.css'; // Importez le fichier CSS

const Conversations: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    getConversations()
      .then((data) => setConversations(data))
      .catch((err) => {
        console.error(err);
        setError("Erreur lors du chargement des conversations.");
      });
  }, []);

  const handleClick = (conversation: Conversation) => {
    console.log("Conversation sélectionnée :", conversation);
    navigate(`/conversation/${conversation.id}`);
  };

  const handleDelete = (id: string) => {
    deleteConversation(id)
      .then(() => {
        setConversations(prev => prev.filter(conv => conv.id !== id));
      })
      .catch((err: any) => {
        console.error(err);
        setError("Erreur lors de la suppression de la conversation.");
      });
  };

  const truncateText = (text: string, maxLength: number) => {
   if (text.length <= maxLength) {
     return text;
   }
    return text.substring(0, maxLength) + "...";
  };

  if (error) {
    return <div>{error}</div>;
  }

  if (conversations.length === 0) {
    return <div>Aucune conversation trouvée.</div>;
  }

  return (
    <div>
      <ul className="conversation-list">
        {conversations.map((conversation) => (
          <li key={conversation.id} className="conversation-item">
            <span onClick={() => handleClick(conversation)}>
              {truncateText(conversation.title, 15)}
            </span>
            <button onClick={() => handleDelete(conversation.id)}>
              -
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Conversations;