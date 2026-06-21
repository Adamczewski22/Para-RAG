import json
from collections.abc import Mapping
from typing import Any


def normalize_token_usage(usage: dict) -> dict:
    if not usage:
        return {}

    normalized = dict(usage)

    if "input_tokens" not in normalized and "prompt_tokens" in normalized:
        normalized["input_tokens"] = normalized["prompt_tokens"]

    if "output_tokens" not in normalized and "completion_tokens" in normalized:
        normalized["output_tokens"] = normalized["completion_tokens"]

    if "total_tokens" not in normalized:
        input_tokens = normalized.get("input_tokens", 0)
        output_tokens = normalized.get("output_tokens", 0)
        normalized["total_tokens"] = input_tokens + output_tokens

    return normalized


def extract_token_usage(response: Any) -> dict:
    usage = getattr(response, "usage_metadata", None)
    if usage:
        return dict(usage)

    metadata = getattr(response, "response_metadata", None)
    if isinstance(metadata, Mapping):
        usage = metadata.get("token_usage")
        if usage:
            return normalize_token_usage(dict(usage))

    return {}


def aggregate_token_usage(usages: list[dict]) -> dict:
    total = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }

    for usage in usages:
        total["input_tokens"] += usage.get("input_tokens", 0)
        total["output_tokens"] += usage.get("output_tokens", 0)
        total["total_tokens"] += usage.get("total_tokens", 0)

    return total


class JsonLogger:
    """Logs internal memory operations in a structured json for analysis"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.log: dict = {} #  log of a single locomo run. Each entry corresponds to a log for separate conversation sample and is indexed by sample id.
        self.current_sample_id = None
        self.current_ingestion_log = {}
        self.current_retrieval_log = []
        self.current_llm_log = []
        self.current_embedding_log = []


    def set_sample_id(self, id: str) -> None:
        """Init logger for a new conversation sample. Call before processing a sample."""
        self.current_sample_id = id
        self.current_ingestion_log = {}
        self.current_retrieval_log = []
        self.current_llm_log = []
        self.current_embedding_log = []


    def save_sample_logs(self) -> None:
        """Save sample log in memory. Call after proessing a sample"""
        sample_log = {
            "ingestion": self.current_ingestion_log,
        }
        if self.current_retrieval_log:
            sample_log["retrieval"] = self.current_retrieval_log
        if self.current_llm_log:
            sample_log["llm"] = self.current_llm_log
        if self.current_embedding_log:
            sample_log["embeddings"] = self.current_embedding_log

        self.log[self.current_sample_id] = sample_log

    def write_logs(self) -> None:
        """Saves the logs in the output file"""
        with open(self.output_path, mode="w", encoding="utf-8") as file:
            json.dump(self.log, file, indent=4, ensure_ascii=False)
    

    def log_msg(self, speaker: str, content: str, id: str) -> None:
        if self.current_sample_id is None:
            raise RuntimeError("sample id must be set before logging")
        
        msg_metadata = {
            "speaker": speaker,
            "content": content,
        }
        self.current_ingestion_log[id] = msg_metadata
    
    
    def log_extraction(self, msg_id: str, assertions: list[str]) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")
        
        self.current_ingestion_log[msg_id]["assertions"] = assertions

    
    def log_deduplication(self, msg_id: str, memories_with_decisions: list[dict]) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")
        
        self.current_ingestion_log[msg_id]["deduplication"] = memories_with_decisions

    def log_profile_update(self, msg_id: str, user: str, previous_profile: str, new_profile: str, assertions: list[str]) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")
        
        profile_update = {
            "user": user,
            "old": previous_profile,
            "new": new_profile,
            "assertions_used": assertions,
        }
        if "profile_updates" in self.current_ingestion_log[msg_id]:
            self.current_ingestion_log[msg_id]["profile_updates"].append(profile_update)
        else:
            self.current_ingestion_log[msg_id]["profile_updates"] = [profile_update]

    def log_assertions_latency(self, msg_id: str, latency: float) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["assertion_latency"] = latency

    def log_assertions_tokens(self, msg_id: str, token_usage: dict) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["assertion_tokens"] = token_usage

    def log_deduplication_latency(self, msg_id: str, latency: float) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["deduplication_latency"] = latency

    def log_deduplication_insertion_latency(self, msg_id: str, latency: float) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["deduplication_insertion_latency"] = latency

    def log_deduplication_tokens(self, msg_id: str, token_usage: dict) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["deduplication_tokens"] = token_usage

    def log_profile_update_latency(self, msg_id: str, latency: float) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["profile_update_latency"] = latency

    def log_update_latency(self, msg_id: str, latency: float) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["update_latency"] = latency

    def log_profile_update_tokens(self, msg_id: str, token_usage: dict) -> None:
        if msg_id not in self.current_ingestion_log:
            raise RuntimeError(f"msg with id {msg_id} not present in the log")

        self.current_ingestion_log[msg_id]["profile_update_tokens"] = token_usage

    def log_retrieval_tokens(self, query: str, token_usage: dict) -> None:
        self.current_retrieval_log.append(
            {
                "query": query,
                "retrieval_tokens": token_usage,
            }
        )

    def log_retrieval_latency(self, query: str, stage: str, latency: float) -> None:
        self.current_retrieval_log.append(
            {
                "query": query,
                "stage": stage,
                "latency": latency,
            }
        )

    def log_profile_retrieval_latency(self, latency: float) -> None:
        self.current_retrieval_log.append(
            {
                "stage": "profile_retrieval",
                "latency": latency,
            }
        )

    def log_llm_tokens(self, category: str, token_usage: dict) -> None:
        self.current_llm_log.append(
            {
                "category": category,
                "tokens": token_usage,
            }
        )

    def log_embedding_tokens(
        self,
        category: str,
        text: str,
        token_usage: dict,
        model: str,
        collection: str | None = None,
    ) -> None:
        self.current_embedding_log.append(
            {
                "category": category,
                "collection": collection,
                "model": model,
                "text": text,
                "embedding_tokens": token_usage,
            }
        )
