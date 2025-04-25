import sqlite3
import pandas as pd
from typing import Any, Callable, Set
import json

def query_database(sql_query: str, db_path: str = 'ma_base_de_donnees.db') -> pd.DataFrame:
    """
    Exécute une requête SQL sur la base de données spécifiée et retourne les résultats sous forme de DataFrame.

    :param sql_query: La requête SQL à exécuter.
    :param db_path: Chemin vers le fichier de base de données SQLite (par défaut 'ma_base_de_donnees.db').
    :return: DataFrame contenant les résultats de la requête.
    """
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)

        # Exécution de la requête et récupération dans un DataFrame
        df = pd.read_sql_query(sql_query, conn)

        # Fermeture de la connexion
        conn.close()

        return df.to_json(orient='records', force_ascii=False)

    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return json.dumps({"error": str(e)})


def get_database_schema(db_path: str = 'ma_base_de_donnees.db'):
    """
    Récupère et affiche le schéma de la base de données (noms des tables et leurs colonnes).
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Récupérer la liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = {}

    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [{'colonne': col[1], 'type': col[2]} for col in columns]

    conn.close()
    return json.dumps(schema, ensure_ascii=False)

# Define a set of callable functions
user_functions: Set[Callable[..., Any]] = {
    query_database,
    get_database_schema
 }