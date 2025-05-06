import sqlite3
import pandas as pd
from typing import Any, Callable, Set
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from sqlalchemy import create_engine, inspect
import sqlalchemy

def get_engine(connection_string: str):
    return create_engine(connection_string)

def query_database(sql_query: str, connection_string: str) -> str:
    try:
        engine = get_engine(connection_string)
        df = pd.read_sql_query(sql_query, con=engine)
        return df.to_json(orient='records', force_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_database_schema(connection_string: str):
    try:
        engine = get_engine(connection_string)
        inspector = inspect(engine)

        schema = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            schema[table_name] = [{'colonne': col['name'], 'type': str(col['type'])} for col in columns]

        return json.dumps(schema, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})
    

def execute_sql(sql_query: str, connection_string: str) -> str:
    try:
        engine = get_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(sql_query))
            conn.commit()
        return json.dumps({"message": "Requête exécutée avec succès."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def create_plot_from_query(sql_query: str, x_column: str, y_column: str, 
                           plot_type: str = 'bar', connection_string: str = 'sqlite:///ma_base.db',
                           output_dir: str = 'plots') -> str:
    try:
        engine = get_engine(connection_string)
        df = pd.read_sql_query(sql_query, con=engine)

        if x_column not in df.columns or y_column not in df.columns:
            return json.dumps({"error": f"Colonnes '{x_column}' ou '{y_column}' introuvables."}, ensure_ascii=False)

        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(10, 6))

        if plot_type == 'bar':
            sns.barplot(x=x_column, y=y_column, data=df)
        elif plot_type == 'line':
            sns.lineplot(x=x_column, y=y_column, data=df)
        elif plot_type == 'scatter':
            sns.scatterplot(x=x_column, y=y_column, data=df)
        else:
            return json.dumps({"error": f"Type de graphique '{plot_type}' non supporté."}, ensure_ascii=False)

        plt.title(f"{plot_type.capitalize()} plot de {y_column} en fonction de {x_column}")
        plt.xticks(rotation=45)
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plot_type}_plot_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)

        plt.savefig(filepath)
        plt.close()

        return json.dumps({"image_path": filepath}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def list_available_connections():
    try:
        with open("connections.json", "r") as f:
            connections = json.load(f)

        if not isinstance(connections, list):
            raise ValueError("Le fichier connections.json doit contenir une liste de connexions.")

        connection_names = [conn["name"] for conn in connections if "name" in conn]

        return json.dumps({"connections": connection_names}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)



def get_connection_string(name: str):
    try:
        with open("connections.json", "r") as f:
            connections = json.load(f)

        for conn in connections:
            if conn["name"] == name:
                return json.dumps({"connection_string": conn["connection_string"]}, ensure_ascii=False)

        return json.dumps({"error": f"Connexion '{name}' introuvable."}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# Define a set of callable functions
user_functions: Set[Callable[..., Any]] = {
    get_engine,
    query_database,
    get_database_schema,
    create_plot_from_query,
    list_available_connections,
    get_connection_string,
    execute_sql
}
