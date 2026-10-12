# retriever.py — Transforme une question en vecteur et récupère les chunks proches.
from pathlib import Path
import chromadb
from google import genai

DOSSIER_DB   = str(Path.home() / "rag_db")
MODELE_EMB   = "gemini-embedding-001"  # même modèle qu'à l'indexation : OBLIGATOIRE
NB_RESULTATS = 4                       # nombre de chunks cités dans la réponse

client_gemini = genai.Client()
client_chroma = chromadb.PersistentClient(path=DOSSIER_DB)
collection    = client_chroma.get_collection("mes_documents")

def chercher(question: str) -> list[dict]:
    """1. Vectorise la question (une seule requête API, très légère).
       2. Interroge Chroma : renvoie les NB_RESULTATS chunks les plus proches,
          avec leur distance (0 = identique, 1 = opposé)."""
    vec_question = client_gemini.models.embed_content(
        model=MODELE_EMB, contents=question).embeddings[0].values

    resultats = collection.query(
        query_embeddings=[vec_question],
        n_results=NB_RESULTATS,
        include=["documents", "metadatas", "distances"])

    chunks_trouves = []
    for doc, meta, dist in zip(resultats["documents"][0],
                               resultats["metadatas"][0],
                               resultats["distances"][0]):
        chunks_trouves.append({
            "texte": doc,
            "source": Path(meta["source"]).name,  # nom court, sans le chemin
            "page": meta["page"],
            "distance": round(dist, 3),
        })
    return chunks_trouves

if __name__ == "__main__":
    q = input("Ta question : ")
    for i, c in enumerate(chercher(q), 1):
        print(f"\n[{i}] {c['source']} (p.{c['page']}) — distance {c['distance']}")
        print(c["texte"][:200], "...")
