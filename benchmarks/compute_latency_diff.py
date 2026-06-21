from argparse import ArgumentParser
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
STATS_DIR = ROOT_DIR / "results" / "locomo" / "stats"


def percent_diff(first: float, second: float) -> str:
    sign = "+" if first > second else "-"
    diff = abs(first / second * 100 - 100)
    return f"{sign}{diff:.2f}%"


def main(first_file: str, second_file: str, output_file):
    first_path = STATS_DIR / first_file
    second_path = STATS_DIR / second_file
    output_path = STATS_DIR / output_file
    result = {"update": {}, "retrieval": {}}

    with open(first_path, mode="r", encoding="utf-8") as file:
        first_stats = json.load(file)
    
    with open(second_path, mode="r", encoding="utf-8") as file:
        second_stats = json.load(file)

    for metric, first_val in first_stats["update"]["latency"].items():
        second_val = second_stats["update"]["latency"][metric]
        diff = percent_diff(first_val, second_val)
        result["update"][f"{metric}_diff"] = diff
    
    for metric, first_val in first_stats["retrieval"]["latency"].items():
        second_val = second_stats["retrieval"]["latency"][metric]
        diff = percent_diff(first_val, second_val)
        result["retrieval"][f"{metric}_diff"] = diff

    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--first", type=str, default="pararag_parallel_stats_7.json")
    parser.add_argument("--second", type=str, default="pararag_sequential_stats_7.json")
    parser.add_argument("--output-file", type=str, default="parallel_to_sequential_latency_diff.json")

    args = parser.parse_args()

    main(
        first_file=args.first,
        second_file=args.second,
        output_file=args.output_file,
    )
