// ChatApp.tsx
import React, { useState, useRef, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ChatInput from "./ChatInput";
import ChatMessages  from "./ChatMessages";
import type { Message } from "../interfaces/Interfaces"
import { askQuestion, getMessages, createConversation } from "../services/ConversationService"

const ChatApp: React.FC = () => {
  // Récupération du paramètre conversationId depuis l'URL
  const { conversationId: routeConversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();

  // On initialise le state avec la valeur issue de l'URL, et on le synchronise ensuite
  const [conversationId, setConversationId] = useState<string | undefined>(routeConversationId);
  const [messages, setMessages] = useState<Message[]>([]);
  const idCounterRef = useRef<number>(0);

  // Synchronisation du state avec le paramètre d'URL
  useEffect(() => {
    setConversationId(routeConversationId);
  }, [routeConversationId]);
  
  const addMessage = (text: string, sender: "user" | "bot") => {
    const id = idCounterRef.current;
    setMessages((prevMessages) => [...prevMessages, { id, text, sender }]);
    idCounterRef.current += 1;
  };

  const handleSend = async (userMessage: string) => {
    console.log("début handleSend");
    // Affiche immédiatement le message de l'utilisateur
    addMessage(userMessage, "user");
    // Si aucune conversation n'existe, la crée et met à jour l'URL
    if (!conversationId) {
      try {
        const newConversation = await createConversation(userMessage);
        setConversationId(newConversation.id);
        navigate(`/conversation/${newConversation.id}`, { replace: true });
        // Ici, on peut directement afficher la réponse déjà renvoyée par createConversation si besoin
        // Exemple : addMessage(newConversation.answer, "bot");
        return; // On retourne pour ne pas continuer et appeler askQuestion
      } catch (error) {
        console.error("Erreur lors de la création de la conversation", error);
        addMessage("Erreur lors de la création de la conversation.", "bot");
        return;
      }
    }
    // Envoie du message et récupération de la réponse du bot dans le cas d'une conversation existante
    try {
      const answer = await askQuestion(userMessage, conversationId);
      addMessage(answer, "bot");
    } catch (error) {
      console.error(error);
      addMessage("Erreur lors de la récupération de la réponse.", "bot");
    }
  };

  // Fonction pour charger les messages depuis le backend
  const loadMessages = async (convId: string) => {
    console.log("debut load messages");
    try {
      const fetchedMessages = await getMessages(convId);

      // Transformer les messages pour qu'ils correspondent au format attendu par ChatMessages
      const mappedMessages = fetchedMessages.map((m: any) => ({
        id: m.id,
        text: m.text, 
        sender: m.sender
      }));

      setMessages(mappedMessages);
    } catch (error) {
      console.error(error);
      addMessage("Erreur lors du chargement des messages depuis le serveur.", "bot");
    }
  };

  // Recharge les messages quand conversationId change
  useEffect(() => {
    if (conversationId) {
      loadMessages(conversationId);
    }
  }, [conversationId]);

  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      idCounterRef.current = 0;
    }
  }, [conversationId]);
  
  return (
    <div className="chat-container">
      {messages.length === 0 && (
        <div className="chat-greeting">Comment puis-je vous aider ?</div>
      )}
      <ChatMessages messages={messages} />
      <ChatInput onSend={handleSend} />
    </div>
  );
};
export default ChatApp;