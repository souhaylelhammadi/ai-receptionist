import tiktoken


def split_text_into_chunks(text: str, max_tokens: int = 300, overlap_tokens: int = 50) -> list[str]:
    """
    Découpe un texte en chunks d'environ `max_tokens` tokens, avec un
    chevauchement (`overlap_tokens`) entre chunks consécutifs pour ne pas
    couper une idée importante pile à la frontière entre deux chunks.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start += max_tokens - overlap_tokens

    return chunks