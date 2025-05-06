from fastapi import APIRouter, HTTPException
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_CONNECTION_STRING = os.getenv("AZURE_AI_AGENT_PROJECT_CONNECTION_STRING")
credential = DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True)
project_client = AIProjectClient.from_connection_string(credential=credential, conn_str=PROJECT_CONNECTION_STRING)

admin_router = APIRouter(prefix="/admin")

# GET agents list
@admin_router.get("/agents")
def get_agents():
    print("debut get agents")
    try:
        # Récupérer tous les agents
        response = project_client.agents.list_agents()
        
        # Formatage pour le frontend
        agents_list = []
        for agent in response.data:
            agents_list.append({
                "id": agent.id,
                "name": agent.name,
                "model": agent.model,
                "created_at": agent.created_at,
                "instructions": agent.instructions[:200] + "..."  # preview partiel si tu veux
            })
        
        return {"agents": agents_list}
    
    except Exception as e:
        print(f"Erreur lors de la récupération des agents : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des agents : {str(e)}")

# DELETE agent
@admin_router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    try:
        project_client.agents.delete_agent(agent_id)
        return {"message": "Agent supprimé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT (update) agent
from pydantic import BaseModel
from typing import Optional

class UpdateAgentRequest(BaseModel):
    name: Optional[str] = None
    instructions: Optional[str] = None

@admin_router.put("/agents/{agent_id}")
def update_agent(agent_id: str, update_data: UpdateAgentRequest):
    try:
        agent = project_client.agents.get_agent(agent_id)

        # MàJ des champs si fournis
        if update_data.name:
            agent.name = update_data.name
        if update_data.instructions:
            agent.instructions = update_data.instructions

        project_client.agents.update_agent(agent_id, agent)
        return {"message": "Agent mis à jour avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
