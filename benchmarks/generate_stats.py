from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm
import numpy as np
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCOMO_DIR = ROOT_DIR / "results" / "locomo"
STATS_DIR = LOCOMO_DIR / "stats"
DEBUG_DIR = LOCOMO_DIR / "debug"

SAMPLE_COUNT = 10


def main(run_name: str):
    log_file_name = f"{run_name}_logs.json"
    result_file_name = f"{run_name}_result.json"
    output_file_name = f"{run_name}_stats.json"

    log_path = DEBUG_DIR / log_file_name
    result_path = LOCOMO_DIR / result_file_name
    output_path = STATS_DIR / output_file_name

    with open(log_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)

    with open(result_path, mode="r", encoding="utf-8") as file:
        results = json.load(file)

    # ==== Retrieval stats ====

    # Latency
    retrieval_latencies = []
    decomposition_latencies = []
    concurrent_retrieval_latencies = []

    # Tokens
    retrieval_total_tokens = []
    retrieval_input_tokens = []
    retrieval_output_tokens = []

    # Embeddings
    retrieval_embedding_tokens = []
    
    # ==== Update stats ====

    # Latency
    update_latencies = []
    assertion_latencies = []
    deduplication_latencies = []
    profile_update_latencies = []

    # Tokens
    update_input_tokens = []
    update_output_tokens = []
    update_total_tokens = []
    assertion_tokens = []
    deduplication_tokens = []
    profile_update_tokens = []

    # Embeddings
    update_embedding_tokens = []

    # ==== Iterate over samples ====
    for sample_id, sample_logs in tqdm(data.items(), desc="Processing samples"):
        
        # ==== Iterate over update logs ====
        for _, ingestion_logs in sample_logs["ingestion"].items():
            # ==== Latencies ====

            # Total update and assertion extraction
            update_latencies.append(ingestion_logs["update_latency"])
            assertion_latencies.append(ingestion_logs["assertion_latency"])

            # Deduplication
            deduplication_latency = ingestion_logs.get("deduplication_latency")
            if deduplication_latency is not None:
                deduplication_latencies.append(ingestion_logs["deduplication_latency"])
            else:
                print("deduplication latency missing")
            
            # Profile
            profile_latency = ingestion_logs.get("profile_update_latency")
            if profile_latency is not None:
                profile_update_latencies.append(ingestion_logs["profile_update_latency"])

            # ==== Tokens ====
            
            # Assertions
            total_tokens = ingestion_logs["assertion_tokens"]["total_tokens"]
            input_tokens = ingestion_logs["assertion_tokens"]["input_tokens"]
            output_tokens = ingestion_logs["assertion_tokens"]["output_tokens"]

            assertion_tokens.append(ingestion_logs["assertion_tokens"]["total_tokens"])

            # Deduplication
            dedup_tokens = ingestion_logs.get("deduplication_tokens")
            if dedup_tokens is not None:
                total_dedup = dedup_tokens["total_tokens"]
                input_dedup = dedup_tokens["input_tokens"]
                output_dedup = dedup_tokens["output_tokens"]

                total_tokens += total_dedup
                input_tokens += input_dedup
                output_tokens += output_dedup
                deduplication_tokens.append(total_dedup)
            
            # Profile update
            profile_tokens = ingestion_logs.get("profile_update_tokens")
            if profile_tokens is not None:
                total_profile = profile_tokens["total_tokens"]
                input_profile = profile_tokens["input_tokens"]
                output_profile = profile_tokens["output_tokens"]

                total_tokens += total_profile
                input_tokens += input_profile
                output_tokens += output_profile
                profile_update_tokens.append(total_profile)
            
            # Total update tokens
            update_total_tokens.append(total_tokens)
            update_input_tokens.append(input_tokens)
            update_output_tokens.append(output_tokens)
            
        # ==== Iterate over retrieval logs ====
        for retrieval_log in sample_logs["retrieval"]:
            # Latencies
            if "latency" in retrieval_log:
                stage = retrieval_log["stage"]
                latency = retrieval_log["latency"]

                if stage == "decomposition":
                    decomposition_latencies.append(latency)

                elif stage == "concurrent_retrieval":
                    concurrent_retrieval_latencies.append(latency)

                else:
                    raise RuntimeError(f"Invalid retrieval stafe {stage}")

            # Tokens
            else:
                tokens = retrieval_log["retrieval_tokens"]
                retrieval_total_tokens.append(tokens["total_tokens"])
                retrieval_input_tokens.append(tokens["input_tokens"])
                retrieval_output_tokens.append(tokens["output_tokens"])
        
        # ==== Iterate over embedding logs ====
        for embedding_log in sample_logs["embeddings"]:
            category = embedding_log["category"]
            tokens = embedding_log["embedding_tokens"]

            if category == "update":
                update_embedding_tokens.append(tokens["total_tokens"])
            elif category == "retrieval":
                retrieval_embedding_tokens.append(tokens["total_tokens"])

        # ==== Iterate over results ====
        sample_result = results[sample_id]
        for qa_item in sample_result:
            retrieval_latencies.append(qa_item["search_time"])

        # ==== Compute stats ====
        update_total_tokens_sum = np.sum(update_total_tokens)

        stats = {
            "update": {
                "latency": {
                    "avg_latency": np.mean(update_latencies),
                    "p95_latency": np.percentile(update_latencies, 95),
                    "assertion_avg_latency": np.mean(assertion_latencies),
                    "deduplication_avg_latency": np.mean(deduplication_latencies),
                    "profile_update_avg_latency": np.mean(profile_update_latencies),
                },
                "tokens": {
                    "avg_total_tokens": np.mean(update_total_tokens),
                    "avg_input_tokens": np.mean(update_input_tokens),
                    "avg_output_tokens": np.mean(update_output_tokens),
                    "assertion_tokens_fraction": np.sum(assertion_tokens) / update_total_tokens_sum,
                    "deduplication_tokens_fraction": np.sum(deduplication_tokens) / update_total_tokens_sum,
                    "profile_update_tokens_fraction": np.sum(profile_update_tokens) / update_total_tokens_sum,
                    "avg_embedding_tokens": np.mean(update_embedding_tokens),
                }
            },
            "retrieval": {
                "latency": {
                    "avg_latency": np.mean(retrieval_latencies),
                    "p95_latency": np.percentile(retrieval_latencies, 95),
                    "decomposition_avg_latency": np.mean(decomposition_latencies),
                    "concurrent_retrieval_avg_latency": np.mean(concurrent_retrieval_latencies),
                },
                "tokens": {
                    "avg_total_tokens": np.mean(retrieval_total_tokens),
                    "avg_input_tokens": np.mean(retrieval_input_tokens),
                    "avg_output_tokens": np.mean(retrieval_output_tokens),
                    "avg_embedding_tokens": np.mean(retrieval_embedding_tokens),
                }
            },
        }

        # Save stats
        with open(output_path, mode="w", encoding="utf-8") as file:
            json.dump(stats, file, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "run_name",
        type=str,
    )
    args = parser.parse_args()

    main(args.run_name)
