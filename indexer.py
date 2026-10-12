# indexer.py — Envoie les chunks dans ChromaDB via les embeddings Gemini.
from pathlib import Path
import time
import chromadb
from google import genai
from loader import charger_documents, decouper_en_chunks

DOSSIER_DOCS = str(Path.home() / "docs")
DOSSIER_DB   = str(Path.home() / "rag_db")   # la DB persiste ici, sur disque
MODELE_EMB   = "gemini-embedding-001"        # modèle d'embeddings imposé
TAILLE_LOT   = 50  # chunks par requête API : économise le quota gratuit

client_gemini = genai.Client()  # lit GEMINI_API_KEY dans l'environnement

def embedder(textes: list[str]) -> list[list[float]]:
    """Appelle Gemini une fois par LOT de textes (jamais un par un).
    Retry simple si on heurte la limite de requêtes/min du tier gratuit."""
    resultat = client_gemini.models.embed_content(
        model=MODELE_EMB, contents=textes)
    return [e.values for e in resultat.embeddings]

def indexer_tout():
    # 1. Charger la DB existante (la crée si première fois)
    client_chroma = chromadb.PersistentClient(path=DOSSIER_DB)
    collection = client_chroma.get_or_create_collection(
        name="mes_documents", metadata={"hnsw:space": "cosine"})
    # "cosine" = similarité par angle, standard pour comparer du texte

    # 2. Index incrémental : IDs déjà stockés -> on les saute
    deja_la = set(collection.get()["ids"])

    # 3. Extraire et découper (étape 2)
    chunks = decouper_en_chunks(charger_documents(DOSSIER_DOCS))
    nouveaux = [c for c in chunks if c["id"] not in deja_la]
    print(f"{len(chunks)} chunks détectés, {len(deja_la)} déjà indexés, "
          f"{len(nouveaux)} à traiter.")

    # 4. Envoyer par lots de TAILLE_LOT (batch : une seule écriture disque
    #    et une seule requête API par lot — doux pour le HDD et le quota)
    for i in range(0, len(nouveaux), TAILLE_LOT):
        lot = nouveaux[i:i + TAILLE_LOT]
        vecteurs = embedder([c["texte"] for c in lot])
        collection.add(
            ids=[c["id"] for c in lot],
            embeddings=vecteurs,
            documents=[c["texte"] for c in lot],
            metadatas=[{"source": c["source"], "page": c["page"]} for c in lot],
        )
        print(f"  Lot {i // TAILLE_LOT + 1} indexé ({len(lot)} chunks).")
        time.sleep(2)  # laisse souffler le rate-limit du tier gratuit

    print(f"\n✔ Terminé. {collection.count()} chunks dans la base.")

if __name__ == "__main__":
    indexer_tout()
