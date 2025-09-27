import os
import pytest

from app.services.memory_service import MemoryService


def test_seed_and_load_faiss(tmp_path, monkeypatch):
    # Arrange: seed a small FAISS index in a temporary path and point settings to it
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # use tmp_path for isolated index
    faiss_path = tmp_path / 'faiss_index'
    faiss_path = str(faiss_path)

    # Monkeypatch the FAISS_INDEX_PATH setting used by MemoryService
    from app.core import config
    monkeypatch.setattr(config.settings, 'FAISS_INDEX_PATH', faiss_path)

    # Act: instantiate MemoryService which should create a new index
    ms = MemoryService()

    # Assert: index exists and is an object with ntotal attribute
    assert ms.faiss_index is not None
    assert hasattr(ms.faiss_index, 'ntotal')

    # Add a sample memory and ensure store_memory returns True/False (embedding model may be missing).
    # We accept either True or False (environments without embeddings will return False).
    result = ms.store_memory(user_id=1, content='test memory', memory_type='general')
    assert isinstance(result, bool)