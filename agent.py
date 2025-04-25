import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path


# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from user_functions import user_functions
import logging

# Activer les logs HTTP requests du SDK Azure
#logging.basicConfig(level=logging.DEBUG)



def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')
    print(user_functions) 

    # Load environment variables from .env file
    load_dotenv()
    PROJECT_CONNECTION_STRING= os.getenv("AZURE_AI_AGENT_PROJECT_CONNECTION_STRING")
    MODEL_DEPLOYMENT = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")


    # Connect to the Azure AI Foundry project
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential
            (exclude_environment_credential=True,
             exclude_managed_identity_credential=True),
        conn_str=PROJECT_CONNECTION_STRING
    )
    


    # Define an agent that can use the custom functions
    with project_client:

        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
               
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="support-agent",
            instructions="""
            Vous êtes un agent d'exploration de base de données. 
            Lorsque l'utilisateur a besoin d'informations sur la base de données, vous lui demandez quelles informations spécifiques il souhaite récolter.

            tu peux utiliser ces  deux fonctions : 
            Fonctions disponibles :

            query_database(sql_query: str) -> DataFrame
            get_database_schema() -> dict : récupère le schéma de la base de données (nom des tables et colonnes)

            Suivez ces étapes :
            1. Demandez à l'utilisateur de préciser les données qu'il souhaite explorer (par exemple, des colonnes spécifiques, des enregistrements, des statistiques, des relations entre tables, etc.).
            2. Une fois que l'utilisateur vous a fourni ses critères, explorez la base de données en fonction de ces informations.
            3. Fournissez à l'utilisateur les résultats sous la forme la plus claire possible (tableaux, résumés, graphiques, etc.).
            4. Si nécessaire, donnez des informations supplémentaires ou des suggestions pour affiner la recherche si les résultats sont trop généraux ou imprécis.

            N'oubliez pas de demander des clarifications si la requête de l'utilisateur est vague ou ambiguë.
                         """,
            toolset=toolset
        )

        thread = project_client.agents.create_thread()
        print(f"You're chatting with: {agent.name} ({agent.id})")


        # Loop until the user types 'quit'
        while True:
            # Get input text
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if len(user_prompt) == 0:
                print("Please enter a prompt.")
                continue

            # Send a prompt to the agent
            message = project_client.agents.create_message(
                 thread_id=thread.id,
                 role="user",
                 content=user_prompt
            )
            run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)


            # Check the run status for failures
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

                
            # Show the latest response from the agent
            messages = project_client.agents.list_messages(thread_id=thread.id)
            last_msg = messages.get_last_text_message_by_role("assistant")
            if last_msg:
                 print(f"Last Message: {last_msg.text.value}")


        # Get the conversation history
        print("\nConversation Log:\n")
        messages = project_client.agents.list_messages(thread_id=thread.id)
        for message_data in reversed(messages.data):
             last_message_content = message_data.content[-1]
             print(f"{message_data.role}: {last_message_content.text.value}\n")


        # Clean up
        project_client.agents.delete_agent(agent.id)
        project_client.agents.delete_thread(thread.id)


if __name__ == '__main__': 
    main()





















