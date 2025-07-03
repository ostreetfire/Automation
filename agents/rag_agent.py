from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List


@dataclass
class StoredDocument:
    """Represents a chunk of text stored in the vector index."""

    text: str
    source: str


# -------- Text processing helpers -------- #


def extract_text(file_path: Path) -> str:
    """Extract text from a PDF or plain text file."""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception:  # pragma: no cover - optional dependency
            try:
                from PyPDF2 import PdfReader  # type: ignore
            except Exception as exc:  # pragma: no cover - optional dependency
                raise ImportError(
                    "Please install 'pypdf' or 'PyPDF2' to read PDF files"
                ) from exc
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def split_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    chunks: List[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start = end - overlap
    return chunks


# -------- Embedding helpers -------- #


def load_embedder(model: str = "openai") -> Callable[[List[str]], List[List[float]]]:
    """Return a function that converts a list of texts to embeddings."""

    if model == "openai":
        try:
            import openai
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "openai package is required for OpenAI embeddings"
            ) from exc

        engine = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-ada-002")

        def embed(texts: List[str]) -> List[List[float]]:
            response = openai.Embedding.create(input=texts, model=engine)
            return [d["embedding"] for d in response["data"]]

        return embed

    # fall back to HuggingFace sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "sentence-transformers package is required for HuggingFace embeddings"
        ) from exc

    transformer = SentenceTransformer(model)

    def embed(texts: List[str]) -> List[List[float]]:
        return transformer.encode(texts, convert_to_numpy=False).tolist()

    return embed


# -------- Vector store helpers -------- #


def build_faiss_index(vectors: List[List[float]], index_path: Path) -> None:
    """Build and persist a FAISS index."""
    try:
        import faiss
        import numpy as np
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "faiss and numpy are required for FAISS vector store"
        ) from exc

    dim = len(vectors[0]) if vectors else 0
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype("float32"))
    faiss.write_index(index, str(index_path))


def load_faiss_index(index_path: Path):
    """Load a FAISS index from disk."""
    try:
        import faiss
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("faiss is required for FAISS vector store") from exc

    return faiss.read_index(str(index_path))


def search_faiss(index, query_vector: List[float], top_k: int) -> List[int]:
    """Return indices of top_k nearest vectors from a FAISS index."""
    import numpy as np  # type: ignore

    distances, indices = index.search(np.array([query_vector]).astype("float32"), top_k)
    return indices[0].tolist()


# -------- High level API -------- #


def build_case_vector_index(
    files: List[str],
    case_id: str,
    *,
    storage_root: Path = Path("storage/vector_indices"),
    embedding_model: str = "openai",
    vector_store: str = "faiss",
) -> None:
    """Create a vector index for a list of files associated with a case."""

    storage_root.mkdir(parents=True, exist_ok=True)
    case_dir = storage_root / str(case_id)
    case_dir.mkdir(parents=True, exist_ok=True)

    texts: List[StoredDocument] = []
    for file in files:
        path = Path(file)
        raw_text = extract_text(path)
        for chunk in split_text(raw_text):
            texts.append(StoredDocument(text=chunk, source=str(path)))

    embed = load_embedder(embedding_model)
    embeddings = embed([doc.text for doc in texts])

    if vector_store == "faiss":
        index_path = case_dir / "index.faiss"
        build_faiss_index(embeddings, index_path)
    elif vector_store == "chroma":
        try:
            import chromadb
            from chromadb.utils import embedding_functions
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "chromadb package is required for Chroma vector store"
            ) from exc

        client = chromadb.PersistentClient(path=str(case_dir))
        collection = client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            ),
        )
        for i, (doc, embedding) in enumerate(zip(texts, embeddings)):
            collection.add(
                ids=str(i),
                embeddings=[embedding],
                documents=[doc.text],
                metadatas={"source": doc.source},
            )
    else:
        raise ValueError(f"Unknown vector store: {vector_store}")

    with (case_dir / "docs.json").open("w", encoding="utf-8") as f:
        json.dump([doc.__dict__ for doc in texts], f, ensure_ascii=False, indent=2)


def _load_case_docs(case_dir: Path) -> List[StoredDocument]:
    """Load stored document chunks for a case."""
    with (case_dir / "docs.json").open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [StoredDocument(**d) for d in data]


def query_case_docs(
    question: str,
    case_id: str,
    *,
    storage_root: Path = Path("storage/vector_indices"),
    embedding_model: str = "openai",
    vector_store: str = "faiss",
    top_k: int = 3,
    llm_model: str | None = None,
) -> str:
    """Query case documents with a natural language question using RAG."""

    case_dir = storage_root / str(case_id)
    if not case_dir.exists():
        raise FileNotFoundError(f"No index found for case {case_id}")

    docs = _load_case_docs(case_dir)

    embed = load_embedder(embedding_model)
    question_vec = embed([question])[0]

    if vector_store == "faiss":
        index = load_faiss_index(case_dir / "index.faiss")
        matches = search_faiss(index, question_vec, top_k)
    elif vector_store == "chroma":
        try:
            import chromadb
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "chromadb package is required for Chroma vector store"
            ) from exc
        client = chromadb.PersistentClient(path=str(case_dir))
        collection = client.get_collection("documents")
        results = collection.query(query_embeddings=[question_vec], n_results=top_k)
        matches = results["ids"][0]
    else:
        raise ValueError(f"Unknown vector store: {vector_store}")

    context = "\n".join(docs[i].text for i in matches)

    # ----- Generate answer -----
    if llm_model is None:
        llm_model = os.getenv("OPENAI_LLM_MODEL", "gpt-3.5-turbo")

    try:
        import openai
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError("openai package is required for LLM answering") from exc

    prompt = f"Answer the question based on the context.\nContext:\n{context}\nQuestion: {question}".strip()
    chat_response = openai.ChatCompletion.create(
        model=llm_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return chat_response["choices"][0]["message"]["content"].strip()


__all__ = [
    "build_case_vector_index",
    "query_case_docs",
]
