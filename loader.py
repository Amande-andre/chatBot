# loader.py — Charge ~/docs et découpe en chunks.
# Aucune dépendance lourde : pypdf (déjà installé) + bibliothèque standard.

from pathlib import Path  # manipulation de chemins, plus sûr que les strings
import re                 # expressions régulières pour nettoyer le texte
from pypdf import PdfReader

# ------------------------------------------------------------- Extraction

def extraire_txt(chemin: Path) -> list[tuple[int, str]]:
    """Lit un fichier .txt. Retourne [(numéro_page, texte)].
    Un .txt n'a pas de pages : on utilise 0 pour compatibilité avec les PDF."""
    texte = chemin.read_text(encoding="utf-8", errors="replace")
    return [(0, texte)]

def extraire_pdf(chemin: Path) -> list[tuple[int, str]]:
    """Lit un PDF page par page. Retourne [(numéro_page, texte)].
    On garde le numéro de page : servira pour CITER la source à l'étape 5."""
    reader = PdfReader(str(chemin))
    pages = []
    for i, page in enumerate(reader.pages):
        pages.append((i + 1, page.extract_text() or ""))  # or "" : une page
    return pages                                            # scannée -> texte vide

def charger_documents(dossier: str) -> list[dict]:
    """Parcourt le dossier ~/docs et extrait TOUT en une seule passe disque
    (important sur HDD mécanique : chaque lecture est coûteuse)."""
    docs = []
    for chemin in sorted(Path(dossier).rglob("*")):  # rglob = récursif
        if chemin.suffix.lower() == ".txt":
            pages = extraire_txt(chemin)
        elif chemin.suffix.lower() == ".pdf":
            pages = extraire_pdf(chemin)
        else:
            continue  # on ignore les autres formats pour l'instant
        for num_page, texte in pages:
            docs.append({"source": str(chemin), "page": num_page, "texte": texte})
    return docs

# ------------------------------------------------------------- Découpage

def normaliser(texte: str) -> list[str]:
    """Découpe en paragraphes. Si le texte n'a pas de paragraphes (PDF mal
    formaté), retombe sur les sauts de ligne. Dernier recours : phrases."""
    texte = texte.replace("\x00", " ")  # caractères nuls = poison pour pypdf
    paras = [p.strip() for p in re.split(r"\n\s*\n", texte) if p.strip()]
    if not paras:
        paras = [l.strip() for l in texte.split("\n") if l.strip()]
    return paras

def decouper_en_chunks(docs: list[dict],
                       taille_max: int = 800,
                       chevauchement: int = 120) -> list[dict]:
    """Fusionne les paragraphes en chunks d'au plus `taille_max` caractères.
    - Un paragraphe seul trop long est coupé 'à la tronçonneuse' (rare).
    - Chaque nouveau chunk reprend la fin du précédent (chevauchement)."""
    chunks = []
    for doc in docs:
        courant, numero = "", 0
        for para in normaliser(doc["texte"]):
            while len(para) > taille_max:  # paragraphe géant : on le coupe
                morceau, para = para[:taille_max], para[taille_max - chevauchement:]
                chunks.append({"id": f'{doc["source"]}::p{doc["page"]}::{numero}', "texte": morceau,
                               "source": doc["source"], "page": doc["page"]})
                numero += 1
            if len(courant) + len(para) + 1 > taille_max and courant:
                chunks.append({"id": f'{doc["source"]}::p{doc["page"]}::{numero}', "texte": courant,
                               "source": doc["source"], "page": doc["page"]})
                numero += 1
                courant = courant[-chevauchement:] + "\n" + para  # overlap
            else:
                courant = f"{courant}\n{para}" if courant else para
        if courant:  # ne pas oublier le dernier morceau
            chunks.append({"id": f'{doc["source"]}::p{doc["page"]}::{numero}', "texte": courant,
                           "source": doc["source"], "page": doc["page"]})
    return chunks

# ------------------------------------------------------------- Test

if __name__ == "__main__":
    docs = charger_documents(str(Path.home() / "docs"))
    chunks = decouper_en_chunks(docs)
    print(f"{len(docs)} pages lues  ->  {len(chunks)} chunks créés")
    vides = [d for d in docs if not normaliser(d["texte"])]
    if vides:  # piège classique : PDF scanné = aucun texte extractible
        print("⚠ Pages sans texte (PDF scannés ?) :", len(vides))
    if chunks:
        c = chunks[len(chunks) // 2]  # un chunk du milieu, pour l'exemple
        print(f"\n--- Exemple de chunk (id: {c['id']}) ---")
        print(c["texte"][:300], "...")
