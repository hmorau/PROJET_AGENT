import React, { useEffect, useState } from "react";
import { getAgents, deleteAgent, updateAgent } from "../services/agentsService";
import type { Agent } from "../interfaces/Interfaces";
import "./AdminAgents.css";

const AdminAgents: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = async () => {
    try {
      const data = await getAgents();
      setAgents(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleDelete = async (id: string) => {
    if (window.confirm("Confirmer la suppression de cet agent ?")) {
      try {
        await deleteAgent(id);
        await fetchAgents();
      } catch (err: any) {
        alert(err.message);
      }
    }
  };

  const handleEdit = async (agent: Agent) => {
    const newName = window.prompt("Nouveau nom de l'agent :", agent.name);
    if (newName && newName !== agent.name) {
      try {
        await updateAgent(agent.id, { name: newName });
        await fetchAgents();
      } catch (err: any) {
        alert(err.message);
      }
    }
  };

  if (loading) return <p>Chargement des agents...</p>;
  if (error) return <p>Erreur : {error}</p>;

  return (
    <div className="admin-agents">
      <h2>Liste des agents</h2>
      {agents.length === 0 ? (
        <p>Aucun agent trouvé.</p>
      ) : (
        <ul className="agent-list">
          {agents.map((agent) => (
            <li key={agent.id} className="agent-item">
              <h3>{agent.name}</h3>
              <p><strong>Modèle :</strong> {agent.model}</p>
              <p><strong>Créé le :</strong> {new Date(agent.created_at).toLocaleString()}</p>
              <p><strong>Instructions :</strong> {agent.instructions}</p>
              <div className="agent-actions">
                <button onClick={() => handleEdit(agent)}>Modifier</button>
                <button onClick={() => handleDelete(agent.id)}>Supprimer</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AdminAgents;
