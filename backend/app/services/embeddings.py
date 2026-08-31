from sentence_transformers import SentenceTransformer

from app.config import settings

_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    """
    Génère un embedding localement avec un modèle open-source,
    sans appel à une API externe.
    """
    return _model.encode(text).tolist()


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Génère les embeddings pour plusieurs textes en une seule passe.
    """
    return _model.encode(texts).tolist()
