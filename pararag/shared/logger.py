import json

class JsonLogger:
    """Logs internal memory operations in a structured json for analysis"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.log: dict = {} #  log of a single locomo run. Each entry corresponds to a log for separate conversation sample and is indexed by sample id.
        self.current_sample_id = None
        self.current_ingestion_log = {}


    def set_sample_id(self, id: str) -> None:
        """Init logger for a new conversation sample. Call before processing a sample."""
        self.current_sample_id = id
        self.current_ingestion_log = {}


    def save_sample_logs(self) -> None:
        """Save sample log in memory. Call after proessing a sample"""
        self.log[self.current_sample_id] = {
            "ingestion": self.current_ingestion_log,
        }

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
