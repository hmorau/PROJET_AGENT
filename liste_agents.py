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

# Liste des agents
agents = project_client.agents.list_agents()

# Affichage des agents
for agent in agents.data:
    print(f"Agent ID: {agent.id}, Name: {agent.name}, Model: {agent.model}")
