"""CLI prototype for the local RAG chatbot."""

from google import genai

from config import get_gemini_api_key
from retriever import chercher


MODELE_REPONSE = "gemini-2.5-flash"


def repondre(question: str) -> str:
    """Generate an answer grounded in the retrieved document chunks."""
    chunks = chercher(question)
    if not chunks:
        return "Je n'ai trouvé aucun document pertinent dans la base locale."

    contextes = "\n\n".join(
        f"[Source: {chunk['source']} — page {chunk['page']}]\n{chunk['texte']}"
        for chunk in chunks
    )
    prompt = (
        "Réponds à la question uniquement à partir des passages fournis ci-dessous. "
        "Si la réponse n'est pas dans les passages, dis-le clairement. "
        "Cite les sources avec leur nom de fichier et leur page.\n\n"
        f"Passages:\n{contextes}\n\nQuestion:\n{question}"
    )

    client = genai.Client(api_key=get_gemini_api_key())
    reponse = client.models.generate_content(model=MODELE_REPONSE, contents=prompt)
    return reponse.text


def main() -> None:
    print("Chatbot RAG — tapez 'quit' pour quitter.")
    while True:
        question = input("\nQuestion : ").strip()
        if question.lower() in {"quit", "exit", "quitter"}:
            break
        if question:
            print("\nRéponse :")
            print(repondre(question))


if __name__ == "__main__":
    main()
