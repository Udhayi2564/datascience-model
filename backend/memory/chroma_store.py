"""
ChromaDB workflow memory — stores & retrieves reusable pipeline summaries.
"""
import json
import hashlib
from typing import Dict, Any, Optional
import chromadb
from config import get_settings

settings = get_settings()


class ChromaWorkflowStore:
    def __init__(self):
        try:
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            self.collection = self.client.get_or_create_collection(
                name="automl_workflows",
                metadata={"description": "AutoML pipeline workflow memory"},
            )
        except Exception:
            self.client = None
            self.collection = None

    def _fingerprint(self, metadata: Dict) -> str:
        key = f"{metadata.get('row_count')}_{metadata.get('col_count')}_{sorted(metadata.get('numerical_features', []))}"
        return hashlib.md5(key.encode()).hexdigest()

    def store_workflow(self, job_id: str, metadata: Dict, workflow_summary: Dict) -> None:
        if not self.collection:
            return
        try:
            fp = self._fingerprint(metadata)
            doc = json.dumps(workflow_summary, default=str)
            self.collection.upsert(
                ids=[fp],
                documents=[doc],
                metadatas=[{"job_id": job_id, "task": workflow_summary.get("task", "unknown")}],
            )
        except Exception:
            pass

    def retrieve_similar(self, metadata: Dict, n_results: int = 3) -> Optional[list]:
        if not self.collection:
            return None
        try:
            fp = self._fingerprint(metadata)
            results = self.collection.query(
                query_texts=[fp],
                n_results=min(n_results, self.collection.count()),
            )
            return results.get("documents", [[]])[0]
        except Exception:
            return None
