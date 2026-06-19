from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCOMO_DIR = ROOT_DIR / "data" / "locomo"
RESULTS_DIR = ROOT_DIR / "results" / "locomo"

SAMPLES_COUNT = 10

def main():
    all_results = {}
    for i in range(SAMPLES_COUNT):
        sample_nr = i + 1
        results_file_name = f"pararag_final_result_{sample_nr}.json"
        results_path = RESULTS_DIR / results_file_name
        
        with open(results_path, mode="r", encoding="utf-8") as file:
            data = json.load(file)
        
        all_results.update(data)
    
    output_file_name = "pararag_final_result.json"
    output_path = RESULTS_DIR / output_file_name

    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(all_results, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()