from pathlib import Path
import json


ROOT_DIR = Path(__file__).resolve().parent.parent
LOCOMO_DIR = ROOT_DIR / "data" / "locomo"
SAMPLE_COUNT = 10
OUTPUT_PATH = LOCOMO_DIR / "locomo_samples_merged.json"


def main() -> None:
    merged = {}

    for sample_nr in range(1, SAMPLE_COUNT + 1):
        sample_path = LOCOMO_DIR / f"locomo_sample_{sample_nr}.json"

        with open(file=sample_path, mode="r", encoding="utf-8") as file:
            sample = json.load(file)

        if not isinstance(sample, dict):
            raise TypeError(f"Expected {sample_path} to contain a JSON object")

        merged.update(sample)

    with open(file=OUTPUT_PATH, mode="w", encoding="utf-8") as file:
        json.dump(merged, file, indent=2, ensure_ascii=False)

    print(f"Merged {len(merged)} samples into {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
