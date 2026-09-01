from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings

llm = ChatGroq(
    model=settings.CHAT_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,
)

SYSTEM_PROMPT = """Tu es un réceptionniste virtuel pour une entreprise.
Tu dois répondre aux questions des clients UNIQUEMENT en te basant sur le contexte fourni ci-dessous.

RÈGLES STRICTES :
- Si l'information demandée n'est PAS dans le contexte, réponds que tu ne disposes pas de cette information et propose de transférer la demande à un employé.
- Ne jamais inventer d'information (prix, horaires, disponibilités, etc.).
- Réponds de manière concise, polie et professionnelle.
- Réponds dans la même langue que la question du client.
"""


def generate_chat_response(user_message: str, context_chunks: list[str]) -> str:
    """
    Génère une réponse du réceptionniste IA, basée uniquement sur le contexte
    fourni (récupéré via la recherche sémantique dans les documents de l'entreprise).
    """
    if context_chunks:
        context_text = "\n\n".join(f"- {chunk}" for chunk in context_chunks)
    else:
        context_text = "(Aucune information pertinente trouvée dans la base de connaissances.)"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"CONTEXTE :\n{context_text}\n\nQUESTION DU CLIENT :\n{user_message}"),
    ]

    response = llm.invoke(messages)
    return response.content
