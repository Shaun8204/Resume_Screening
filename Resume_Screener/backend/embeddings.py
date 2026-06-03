import os
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def _normalize(v: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return v / norms


def cosine_sim(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # a: (1, dim) or (n, dim), b: (m, dim)
    a_n = _normalize(a)
    b_n = _normalize(b)
    return np.dot(a_n, b_n.T)


def embeddings_with_sentence_transformers(texts: List[str]) -> np.ndarray:
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as e:
        raise RuntimeError("sentence-transformers not available: install it to use local embeddings") from e

    model_name = os.environ.get("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)
    vecs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return vecs.astype(np.float32)


def get_embeddings(texts: List[str]) -> np.ndarray:
    """Return a 2D numpy array of embeddings for the given texts.

    Preference order:
      1. sentence-transformers if installed
      2. TF-IDF fallback
    """
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)

    try:
        return embeddings_with_sentence_transformers(texts)
    except Exception:
        # Last-resort: use TF-IDF vectors as a lightweight semantic fallback
        vectorizer = TfidfVectorizer(max_features=50000, stop_words="english")
        X = vectorizer.fit_transform(texts)
        return X.toarray().astype(np.float32)
