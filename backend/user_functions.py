import sqlite3
import pandas as pd
from typing import Any, Callable, Set
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def create_plot_from_query(sql_query: str, x_column: str, y_column: str, 
                           plot_type: str = 'bar', db_path: str = 'ma_base_de_donnees.db',
                           output_dir: str = 'plots') -> str:
    """
    Exécute une requête SQL, génère un graphique et enregistre l'image.

    :param sql_query: La requête SQL à exécuter.
    :param x_column: Le nom de la colonne à utiliser en abscisse.
    :param y_column: Le nom de la colonne à utiliser en ordonnée.
    :param plot_type: Le type de graphique ('bar', 'line', 'scatter').
    :param db_path: Chemin vers le fichier de base de données SQLite.
    :param output_dir: Dossier de destination pour sauvegarder l'image.
    :return: Chemin du fichier image ou message d'erreur au format JSON.
    """
    try:
        # Connexion et récupération des données
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()

        if x_column not in df.columns or y_column not in df.columns:
            return json.dumps({"error": f"Colonnes '{x_column}' ou '{y_column}' introuvables dans les résultats."}, ensure_ascii=False)

        # Création du dossier si nécessaire
        os.makedirs(output_dir, exist_ok=True)

        # Création du graphique
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

        # Génération d'un nom de fichier unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plot_type}_plot_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)

        # Sauvegarde de l'image
        plt.savefig(filepath)
        plt.close()

        return json.dumps({"image_path": filepath}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

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
    get_database_schema,
    create_plot_from_query
}
