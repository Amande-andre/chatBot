# chatBot
Un prototype RAG en ligne de commande, conçu pour fonctionner sur une petite configuration.

## Installation

```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

Renseignez `GEMINI_API_KEY` dans le fichier `.env`. La clé ne doit jamais être
commitée dans le dépôt.

Placez les fichiers `.txt` et `.pdf` à indexer dans `~/docs`.

## Utilisation

Indexez les documents :

```bash
python indexer.py
```

Puis lancez le chatbot :

```bash
python rag.py
```

Tapez `quit` pour quitter. L'index local est conservé par Chroma dans `~/rag_db`.
