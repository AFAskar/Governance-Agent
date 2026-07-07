"""Tests for Qdrant client initialization configuration."""

import os
from unittest import mock

from src.embeddings.qdrant_manager import initialize_qdrant


def test_initialize_qdrant_uses_qdrant_url_env() -> None:
    with mock.patch.dict(os.environ, {"QDRANT_URL": "http://qdrant:6333"}, clear=False):
        with mock.patch("src.embeddings.qdrant_manager.QdrantClient") as mock_client:
            mock_client.return_value.get_collection.side_effect = Exception("missing")
            initialize_qdrant("ndi_rag", vector_size=768)

    mock_client.assert_called_once()
    assert mock_client.call_args.kwargs["url"] == "http://qdrant:6333"
