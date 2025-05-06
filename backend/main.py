import traceback
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
from admin_routes import admin_router

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
            name="support-agent",
            instructions="""
    Vous êtes un agent d'exploration de bases de données.

    Lorsqu'un utilisateur souhaite interagir avec une base :
    - Utilisez list_available_connections() pour lister les connexions disponibles.
    - Demandez à l'utilisateur laquelle utiliser.
    - Récupérez la connection string via get_connection_string(name).
    - Créez un moteur de connexion via get_engine(connection_string).

    Puis utilisez :
    - query_database(sql_query: str, connection_string: str)
    - get_database_schema(connection_string: str)
    - create_plot_from_query(sql_query: str, x_column: str, y_column: str, plot_type: str, connection_string: str)

    execute_sql(sql_query: str, connection_string: str) -> str permet d'insérer des données.

    Présentez les résultats clairement et proposez des suggestions si nécessaire.
    """,
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

@router.get("/api/conversations")
def get_conversations():
    #TODO : A corriger
    try:
        # Récupérer les threads depuis Azure AI
        response = project_client.agents.list_threads()
        
        if not response.get('data'):
            return {"conversations": []}
        
        conversations_list = []
        for thread in response['data']:
            thread_id = thread['id']
            
            # Récupérer les messages de ce thread
            messages_response = project_client.agents.list_messages(thread_id=thread_id)
            messages = messages_response.get('data', [])
            
            # Chercher le premier message utilisateur dans le thread
            title = "Nouvelle conversation"
            for msg in sorted(messages, key=lambda x: x['created_at']):
                if msg['role'] == "user":
                    title = msg['content'][0]['text']['value'] if msg['content'] else "Message sans contenu"
                    break
            
            conversations_list.append({
                "id": thread_id,
                "title": title
            })
        
        return {"conversations": conversations_list}

    except Exception as e:
        print(f"Erreur lors de la récupération des conversations : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des conversations : {str(e)}")

    
@router.get("/api/conversations/{conversation_id}/messages")
def get_messages(conversation_id: str):
    try:
        # Récupérer les messages du thread depuis Azure AI
        response = project_client.agents.list_messages(thread_id=conversation_id)
        
        # Vérification si des messages sont présents
        if not response.get('data'):
            raise HTTPException(status_code=404, detail="Aucun message trouvé pour cette conversation.")
        
        # Trier les messages par 'created_at' (date de création)
        sorted_messages = sorted(response['data'], key=lambda x: x['created_at'])
        
        # Formatage des messages pour l'API
        formatted_messages = []
        for msg in sorted_messages:
            # Accéder au texte et au rôle de l'agent/utilisateur
            message_text = msg['content'][0]['text']['value'] if msg['content'] else ''
            formatted_messages.append({
                "id": msg['id'],  # ID du message
                "text": message_text,  # Texte du message
                "sender": msg['role'],  # Rôle (assistant ou user)
                "created_at": msg['created_at']  # Ajout de la date de création pour le tri
            })
        
        return {"messages": formatted_messages}
    
    except Exception as e:
        print(f"Erreur lors de la récupération des messages : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des messages : {str(e)}")

    
@router.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        thread_id = request.conversationId
        # Si pas de conversation, créer un nouveau thread
        if not thread_id:
            thread = project_client.agents.create_thread()
            thread_id = thread.id
        
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
    

        return ChatResponse(answer=last_msg.text.value, conversationId=thread_id)

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Inclure le router dans l'application FastAPI
app.include_router(router)
app.include_router(admin_router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
