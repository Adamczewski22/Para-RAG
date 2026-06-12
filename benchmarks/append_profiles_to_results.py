from argparse import ArgumentParser
from pathlib import Path
import json
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "results" / "locomo"


def add_profiles(data: dict, profiles: str) -> int:
    appended_count = 0

    for qa_items in data.values():
        for qa_item in qa_items:
            qa_item["profiles"] = profiles
            appended_count += 1

    return appended_count


def main(iteration: str, version: str, results_dir: Path) -> None:
    profiles = sys.stdin.read().rstrip("\n")
    results_path = results_dir / f"{iteration}_result_{version}.json"
    output_path = results_dir / f"{iteration}_result_{version}_with_profiles.json"

    with open(results_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)

    appended_count = add_profiles(data, profiles)

    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Written {output_path}: added profiles to {appended_count} result items.")


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "iteration", 
        type=str,
    )
    parser.add_argument(
        "version", 
        type=str,
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
    )
    args = parser.parse_args()

    main(
        iteration=args.iteration,
        version=args.version,
        results_dir=args.results_dir,
    )
