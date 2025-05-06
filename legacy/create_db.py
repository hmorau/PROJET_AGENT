import sqlite3

# Connexion à la base de données (créée si elle n'existe pas)
conn = sqlite3.connect('ma_base_de_donnees.db')
cursor = conn.cursor()

# Création d'une table exemple : 'commandes'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS commandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client TEXT,
        produit TEXT,
        quantite INTEGER,
        prix REAL,
        date TEXT
    )
''')

# Insertion de données d'exemple
commandes_exemple = [
    ('Alice', 'Ordinateur portable', 1, 999.99, '2024-04-02'),
    ('Bob', 'Casque audio', 2, 199.50, '2024-04-05'),
    ('Charlie', 'Souris sans fil', 3, 29.99, '2024-03-28'),
    ('Alice', 'Clavier mécanique', 1, 89.99, '2024-04-12')
]

cursor.executemany('''
    INSERT INTO commandes (client, produit, quantite, prix, date)
    VALUES (?, ?, ?, ?, ?)
''', commandes_exemple)

# Sauvegarder et fermer la connexion
conn.commit()
conn.close()
