"""
Shared RAG helper — Chroma + sentence-transformers embeddings.
Each agent gets its own collection (namespace) so memories don't bleed.
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Persist Chroma to disk so memory survives across container restarts.
CHROMA_DIR = os.getenv("NEURA_CHROMA_DIR", "./chroma_store")

# Free, local embedding model — runs on CPU, ~80MB, good enough for code/design.
EMBED_MODEL = os.getenv("NEURA_EMBED_MODEL", "all-MiniLM-L6-v2")


class NeuraRAG:
    """
    Per-agent vector memory. Usage:
        rag = NeuraRAG(collection="architect")
        rag.add(["doc1 text", "doc2 text"], metadatas=[{"src": "v1"}, {"src": "v2"}])
        hits = rag.search("how do we do auth?", k=3)
    """

    _client = None  # singleton — Chroma client should be reused

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            cls._client = chromadb.PersistentClient(
                path=CHROMA_DIR,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
        return cls._client

    def __init__(self, collection: str):
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        self.collection = self._get_client().get_or_create_collection(
            name=collection,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        if not documents:
            return
        if ids is None:
            existing = self.collection.count()
            ids = [f"doc-{existing + i}" for i in range(len(documents))]
        self.collection.add(
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids,
        )

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Returns list of {document, metadata, distance} sorted by relevance."""
        if self.collection.count() == 0:
            return []
        res = self.collection.query(query_texts=[query], n_results=min(k, self.collection.count()))
        hits = []
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            hits.append({"document": doc, "metadata": meta, "distance": dist})
        return hits

    def context_block(self, query: str, k: int = 5) -> str:
        """Returns retrieved docs formatted as a 'Context:' block for prompts."""
        hits = self.search(query, k=k)
        if not hits:
            return ""
        lines = ["Relevant prior context:"]
        for i, h in enumerate(hits, 1):
            lines.append(f"[{i}] {h['document']}")
        return "\n".join(lines)
