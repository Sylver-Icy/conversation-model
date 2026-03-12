"""
Embedding-based retrieval for the Veyra help knowledge base.

On first use, embeds every section of HELP_KNOWLEDGE and caches the result
to disk.  On subsequent startups the cache is reused unless the knowledge
base has changed (detected via MD5 hash).
"""

import hashlib
import pickle
from pathlib import Path

import numpy as np

from prompts.help_knowledge import HELP_KNOWLEDGE
from state.client import client
from logger import logger

_CACHE_PATH = Path("cache/help_embeddings.pkl")


def _split_sections(text: str) -> list[dict]:
    """Split the knowledge base on '## SECTION:' markers."""
    chunks = text.split("## SECTION:")
    sections = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.splitlines()
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        sections.append({"title": title, "content": f"{title}\n\n{body}"})
    return sections


def _knowledge_hash() -> str:
    return hashlib.md5(HELP_KNOWLEDGE.encode()).hexdigest()


class HelpRetriever:
    """
    Lazily initialised retriever.  The first call to retrieve() triggers
    embedding generation (or loads from cache).  Subsequent calls are fast.
    """

    def __init__(self) -> None:
        self._data: list[dict] | None = None  # list of {title, content, embedding}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def retrieve(
        self,
        query: str,
        req_id: str = "?",
        top_k: int = 2,
        score_threshold: float = 0.35,
    ) -> list[str]:
        """Return the top_k most relevant section texts for the query.

        The top match is always included.  Subsequent matches are only included
        if their cosine similarity meets score_threshold, preventing low-signal
        sections from muddying the context.
        """
        await self._ensure_loaded()

        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=query.strip(),
        )
        q_emb = np.array(response.data[0].embedding)

        scored = []
        for sec in self._data:
            emb = sec["embedding"]
            sim = float(np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb)))
            scored.append((sim, sec["title"], sec["content"]))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Log top-5 candidates so we can see what the retriever considered
        logger.debug(
            "[REQ: %s][HelpRetriever] Top-5 candidates for query %r:",
            req_id,
            query,
        )
        for rank, (sim, title, _) in enumerate(scored[:5], start=1):
            logger.debug("[REQ: %s][HelpRetriever]   #%d  score=%.4f  section='%s'", req_id, rank, sim, title)

        # Always take the top match; only add more if they clear the threshold
        selected: list[str] = []
        for i, (sim, title, content) in enumerate(scored[:top_k]):
            if i == 0 or sim >= score_threshold:
                selected.append(content)
                logger.info(
                    "[REQ: %s][HelpRetriever] SELECTED #%d  score=%.4f  section='%s'",
                    req_id, i + 1, sim, title,
                )
            else:
                logger.info(
                    "[REQ: %s][HelpRetriever] DROPPED  #%d  score=%.4f  section='%s' (below threshold %.2f)",
                    req_id, i + 1, sim, title, score_threshold,
                )

        return selected

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _ensure_loaded(self) -> None:
        if self._data is not None:
            return
        self._data = await self._load_or_build()

    async def _load_or_build(self) -> list[dict]:
        current_hash = _knowledge_hash()

        if _CACHE_PATH.exists():
            try:
                with open(_CACHE_PATH, "rb") as f:
                    cache = pickle.load(f)
                if cache.get("hash") == current_hash:
                    logger.info("[HelpRetriever] Loaded %d section embeddings from cache.", len(cache["sections"]))
                    return cache["sections"]
                logger.info("[HelpRetriever] Knowledge base changed — rebuilding embeddings.")
            except (pickle.UnpicklingError, KeyError, EOFError, OSError) as e:
                logger.warning("[HelpRetriever] Cache load failed (%s), rebuilding.", e)
        else:
            logger.info("[HelpRetriever] No cache found — building embeddings for the first time.")

        return await self._build_and_save(current_hash)

    async def _build_and_save(self, knowledge_hash: str) -> list[dict]:
        sections = _split_sections(HELP_KNOWLEDGE)

        for sec in sections:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=sec["content"],
            )
            sec["embedding"] = np.array(response.data[0].embedding)

        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_CACHE_PATH, "wb") as f:
            pickle.dump({"hash": knowledge_hash, "sections": sections}, f)

        logger.info("[HelpRetriever] Built and cached %d section embeddings.", len(sections))
        return sections
