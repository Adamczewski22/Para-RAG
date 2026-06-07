from argparse import ArgumentParser
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCOMO_DIR = ROOT_DIR / "results" / "locomo"
DEBUG_DIR = LOCOMO_DIR / "debug"
EXTRACTIONS_DIR = LOCOMO_DIR / "extractions"


def main(iteration: str, version: str):
    logs_file = f"{iteration}_logs_{version}.json"
    output_file = f"{iteration}_extraction_{version}.json"
    logs_path = DEBUG_DIR / logs_file
    output_path = EXTRACTIONS_DIR / output_file

    # Load ingestion logs
    with open(logs_path, mode="r", encoding="utf-8") as file:
        debug_data = json.load(file)
    
    _, sample_logs = next(iter(debug_data.items())) # Assume a single conversational sample
    ingestion_logs = sample_logs["ingestion"]

    # Aggregate assertions extracted from all questions
    assertions: list[str] = []
    for _, msg_metadata in ingestion_logs.items():
        assertions.extend(msg_metadata["assertions"])
    
    # Write assertions
    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(assertions, file)
    
    print(f"Obtained {len(assertions)} assertions")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--iteration",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--version",
        type=str,
        required=True,
    )

    args = parser.parse_args()

    main(
        iteration=args.iteration,
        version=args.version,
    )
