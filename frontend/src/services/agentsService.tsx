import type { Agent } from "../interfaces/Interfaces";

const apiUrl = import.meta.env.VITE_API_URL;

export const getAgents = async (): Promise<Agent[]> => {
  if (!apiUrl) throw new Error("L'URL de l'API n'est pas définie.");

  const response = await fetch(`${apiUrl}/admin/agents`);
  if (!response.ok) throw new Error("Erreur lors de la récupération des agents.");

  const data = await response.json();
  return data.agents;
};

export const deleteAgent = async (id: string): Promise<void> => {
  const response = await fetch(`${apiUrl}/admin/agents/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Erreur lors de la suppression de l'agent.");
  }
};

export const updateAgent = async (id: string, updatedFields: Partial<Agent>): Promise<void> => {
  const response = await fetch(`${apiUrl}/admin/agents/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(updatedFields),
  });
  if (!response.ok) {
    throw new Error("Erreur lors de la mise à jour de l'agent.");
  }
};
