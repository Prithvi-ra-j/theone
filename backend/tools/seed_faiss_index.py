"""Seed a tiny FAISS index used by the app for local development.

This script creates a small IndexFlatIP index with dimension 384, inserts
some random vectors and writes the index to the default data path used by
the project (backend/data/faiss_index).

Run from repository root or backend folder:
    python tools/seed_faiss_index.py
"""
import os
import numpy as np
import faiss


def main():
    # default path used by settings.FAISS_INDEX_PATH (relative to backend)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'faiss_index')
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    dimension = 384
    n_vectors = 8

    # create random unit vectors
    rng = np.random.RandomState(42)
    vectors = rng.randn(n_vectors, dimension).astype('float32')
    # normalize for cosine-like similarity
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / (norms + 1e-12)

    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    faiss.write_index(index, out_path)
    print(f'Wrote FAISS index with {n_vectors} vectors to: {out_path}')


if __name__ == '__main__':
    main()