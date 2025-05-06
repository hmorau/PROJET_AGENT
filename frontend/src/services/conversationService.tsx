import type { Conversation, Message } from "../interfaces/Interfaces"

const apiUrl = import.meta.env.VITE_API_URL;

export const getConversations = async (): Promise<Conversation[]> => {
  if (!apiUrl) {
    throw new Error("L'URL de l'API n'est pas définie.");
  }
  const response = await fetch(`${apiUrl}/api/conversations`);
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des conversations.");
  }
  const conversations: Conversation[] = await response.json();
  return conversations;
};

// Fonction pour supprimer une conversation en fonction de son id
export const deleteConversation = async (id: string): Promise<void> => {
  const response = await fetch(`${apiUrl}/api/conversations/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    console.error("Erreur lors de la suppression de la conversation :", response.statusText);
    throw new Error("Erreur lors de la suppression de la conversation");
  }
};

export const askQuestion = async (question: string, conversationId?: string): Promise<string> => {
  console.log("debut askQuestion");
  if (!apiUrl) {
    throw new Error("L'URL de l'API n'est pas définie dans les variables d'environnement");
  }
  // Construire le payload sans inclure conversationId si celle-ci est undefined
  const payload: any = { question };
  if (conversationId) {
    payload.conversationId = conversationId;
  }
  const response = await fetch(`${apiUrl}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Erreur lors de la communication avec le serveur");
  }
  const data = await response.json();
  return data.answer;
};

export const createConversation = async (initialMessage: string): Promise<{ id: string }> => {
  try {
    console.log("debut creation service");
    // Pour créer une conversation, on envoie uniquement le champ "question"
    const response = await fetch(`${apiUrl}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: initialMessage }),
    });
    if (!response.ok) {
      throw new Error("Erreur lors de la création de la conversation");
    }
    const data = await response.json();
    return { id: data.conversationId };
  } catch (error) {
    console.error("Erreur en créant la conversation", error);
    throw error;
  }
};

export const getMessages = async (conversationId: string): Promise<Message[]> => {
  if (!apiUrl) {
    throw new Error("L'URL de l'API n'est pas définie.");
  }
  const response = await fetch(`${apiUrl}/api/conversations/${conversationId}/messages`);
  if (!response.ok) {
    throw new Error("Erreur lors de la récupération des messages.");
  }
  const data = await response.json(); // data contient l'objet avec `messages`
  if (!data.messages || !Array.isArray(data.messages)) {
    throw new Error("Les messages ne sont pas sous forme de tableau.");
  }

  const messages: Message[] = await data.messages;
  return messages;
};