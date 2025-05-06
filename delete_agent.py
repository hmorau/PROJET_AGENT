from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import os
from dotenv import load_dotenv

load_dotenv()

# Connexion au projet Azure AI
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True),
    conn_str=os.getenv("AZURE_AI_AGENT_PROJECT_CONNECTION_STRING")
)

def afficher_agents():
    agents = project_client.agents.list_agents()
    if not agents.data:
        print("Aucun agent disponible.")
    else:
        print("\nListe des agents :")
        for agent in agents.data:
            print(f"Agent ID: {agent.id}, Name: {agent.name}, Model: {agent.model}")
    return agents.data

def supprimer_agent(agent_id):
    try:
        project_client.agents.delete_agent(agent_id)
        print(f"✅ Agent {agent_id} supprimé avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la suppression de l'agent {agent_id}: {e}")

def main():
    while True:
        agents = afficher_agents()
        if not agents:
            break
        agent_id = input("\nEntrez l'ID de l'agent à supprimer (ou appuyez sur Entrée pour quitter) : ").strip()
        if not agent_id:
            print("Fin du programme.")
            break
        if any(agent.id == agent_id for agent in agents):
            supprimer_agent(agent_id)
        else:
            print("❌ Agent non trouvé. Veuillez vérifier l'ID.")

if __name__ == "__main__":
    main()
