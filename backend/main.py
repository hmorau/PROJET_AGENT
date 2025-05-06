from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from user_functions import user_functions
import os 

# Load env
load_dotenv()
PROJECT_CONNECTION_STRING = os.getenv("AZURE_AI_AGENT_PROJECT_CONNECTION_STRING")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")

credential = DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True)
project_client = AIProjectClient.from_connection_string(credential=credential, conn_str=PROJECT_CONNECTION_STRING)

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

agent = project_client.agents.create_agent(
    model=MODEL_DEPLOYMENT,
    name="support-agent-api",
    instructions="""...""",
    toolset=toolset
)

# Stocker les threads en mémoire (sinon DB recommandée)
threads = {}

router = APIRouter()
app = FastAPI()

# Autoriser l'accès depuis votre application frontend
origins = [
    "http://localhost:5173",
    # Vous pouvez ajouter d'autres domaines si nécessaire
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Autoriser ces origines spécifiques
    allow_credentials=True,
    allow_methods=["*"],             # Autoriser toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],             # Autoriser tous les headers
)

# Définir le modèle de données pour la requête
class ChatRequest(BaseModel):
    question: str
    conversationId: Optional[str] = None # Optionnel, si non fourni, la conversation sera créée

class ChatResponse(BaseModel):
    answer: str
    conversationId: str
    
@router.get("/api/conversations/{conversation_id}/messages")
def get_messages(conversation_id: str):
    # Vérifier si la conversation existe
    if conversation_id not in threads:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    
    thread = threads[conversation_id]
    messages = [
        {"id": 1, "text": thread['premiere_question'], "sender": "user"},
        {"id": 2, "text": thread['premiere_reponse'], "sender": "bot"},
    ]
    return {"messages": messages}

@router.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        thread_id = request.conversationId
        # Si pas de conversation, créer un nouveau thread
        if not thread_id:
            thread = project_client.agents.create_thread()
            thread_id = thread.id
            threads[thread_id] = {'premiere_question': request.question, 'premiere_reponse': ""}
        
        # Envoyer le message utilisateur
        project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=request.question
        )

        # Lancer le traitement
        run = project_client.agents.create_and_process_run(thread_id=thread_id, agent_id=agent.id)

        if run.status == "failed":
            raise HTTPException(status_code=500, detail="L'agent a échoué à traiter la demande.")

        # Récupérer dernier message assistant
        messages = project_client.agents.list_messages(thread_id=thread_id)
        last_msg = messages.get_last_text_message_by_role("assistant")

        if not last_msg:
            raise HTTPException(status_code=500, detail="Aucune réponse de l'agent.")
        
        # Mettre à jour la réponse dans le dictionnaire
        threads[thread_id]['premiere_reponse'] = last_msg.text.value

        return ChatResponse(answer=last_msg.text.value, conversationId=thread_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Inclure le router dans l'application FastAPI
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
