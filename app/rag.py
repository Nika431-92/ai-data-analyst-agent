
import os
import math
import json
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "data" / "knowledge"
CACHE_PATH = BASE_DIR / "data" / "knowledge_embeddings.json"

EMBEDDING_MODEL = "gemini-embedding-001"

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your project's .env file."
    )

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# Load Knowledge Documents
# --------------------------------------------------

def load_documents():
    """Load Markdown files while preserving section headings."""

    documents = []

    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge directory not found: {KNOWLEDGE_DIR}"
        )

    for file_path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        current_section = "General"

        for line in content.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                current_section = line.lstrip("#").strip()
                continue

            documents.append({
                "text": f"{current_section}: {line}",
                "source": file_path.name,
            })

    return documents


# --------------------------------------------------
# Cosine Similarity
# --------------------------------------------------

def cosine_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two embedding vectors."""

    if len(vector_a) != len(vector_b):
        raise ValueError("Embedding dimensions do not match.")

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


# --------------------------------------------------
# Gemini Embeddings
# --------------------------------------------------

def embed_text(text):
    """Generate an embedding using Gemini."""

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )

    if not response.embeddings:
        raise ValueError("Gemini returned no embeddings.")

    return response.embeddings[0].values


# --------------------------------------------------
# Document Embedding Cache
# --------------------------------------------------

def get_document_embeddings(documents):
    """
    Load cached document embeddings when available.
    Regenerate them if the documents or model changes.
    """

    document_signature = hashlib.sha256(
        json.dumps(
            {
                "model": EMBEDDING_MODEL,
                "documents": documents,
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    # Try to reuse the existing cache.
    if CACHE_PATH.exists():
        try:
            cache = json.loads(
                CACHE_PATH.read_text(encoding="utf-8")
            )

            if cache.get("signature") == document_signature:
                embeddings = cache.get("embeddings", [])

                if (
                    len(embeddings) == len(documents)
                    and all(isinstance(vector, list) for vector in embeddings)
                ):
                    print("Using cached document embeddings.")
                    return embeddings

        except (OSError, ValueError, TypeError):
            print("Embedding cache is invalid. Rebuilding it.")

    # Generate embeddings if no valid cache exists.
    print("Generating document embeddings...")

    embeddings = [
        embed_text(document["text"])
        for document in documents
    ]

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    cache_data = {
        "signature": document_signature,
        "embeddings": embeddings,
    }

    CACHE_PATH.write_text(
        json.dumps(cache_data),
        encoding="utf-8",
    )

    print(f"Cached {len(embeddings)} document embeddings.")

    return embeddings


# --------------------------------------------------
# Retrieve Relevant Documents
# --------------------------------------------------

def retrieve_documents(question, top_k=3):
    """Return the most relevant knowledge passages for a question."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    documents = load_documents()

    if not documents:
        return []

    # Embed the new question.
    question_embedding = embed_text(question.strip())

    # Reuse stored document embeddings.
    document_embeddings = get_document_embeddings(documents)

    results = []

    for document, document_embedding in zip(
        documents,
        document_embeddings,
    ):
        score = cosine_similarity(
            question_embedding,
            document_embedding,
        )

        results.append({
            **document,
            "score": score,
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]
