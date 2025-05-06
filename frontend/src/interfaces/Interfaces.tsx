export interface Conversation {
  id: string;
  title: string;
  messages?: Message[];
}

// ajouter des éléments graphiques tableaux etc ? 
export interface Message {
    id: number,
    text: string;
    sender: "user" | "bot";
  }

export interface Agent {
  id: string;
  name: string;
  model: string;
  created_at: string;
  instructions: string;
}
  