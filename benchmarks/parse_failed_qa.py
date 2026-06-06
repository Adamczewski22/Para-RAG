from argparse import ArgumentParser
from pathlib import Path
import json

# Mind that this script only works for locomo results from a single conversational sample

ROOT_DIR = Path(__file__).parent.parent
RESULTS_DIR = ROOT_DIR / "results" / "locomo"
LOCOMO_DIR = ROOT_DIR / "data" / "locomo"
DEBUG_DIR = RESULTS_DIR / "debug"


def main(iteration: str, version: str, locomo_file: str):
    results_file = f"{iteration}_result_{version}.json"
    eval_file = f"{iteration}_eval_{version}.json"
    logs_file = f"{iteration}_logs_{version}.json"
    output_file = f"{iteration}_debug_{version}.json"
    
    results_path = RESULTS_DIR / results_file
    eval_path = RESULTS_DIR / eval_file
    locomo_path = LOCOMO_DIR / locomo_file
    logs_path = RESULTS_DIR / "debug" / logs_file
    output_path = DEBUG_DIR / output_file

    # Get question metadata for which the system failed
    failed_questions: list[dict] = []
    
    with open(eval_path, mode="r", encoding="utf-8") as file:
        eval_data = json.load(file)
    
    _, qa_items = next(iter(eval_data.items())) # Assume single conversational sample

    for qa_item in qa_items:
        if qa_item["llm_score"] == 0:
            failed_questions.append({
                "question": qa_item["question"],
                "correct_answer": qa_item["answer"],
                "given_answer": qa_item["response"],
            })

    # Include msg IDs which are evidence for a failed question in QA task
    msg_ids_by_question: dict[str, list[str]] = {}

    with open(locomo_path, mode="r", encoding="utf-8") as file:
        locomo_data = json.load(file)

    _, sections = next(iter(locomo_data.items())) # Assume single conversational sample
    qa_items = sections["question"]

    for qa_item in qa_items:
        question = qa_item["question"]
        evidence_ids = qa_item["evidence"]
        msg_ids_by_question[question] = evidence_ids
    
    for question in failed_questions:
        question["evidence"] = msg_ids_by_question[question["question"]]

    # Include the retrieved memories for a failed question in QA task
    memories_by_question: dict[str, str] = {}
    
    with open(results_path, mode="r", encoding="utf-8") as file:
        results_data = json.load(file)
    
    _, qa_items = next(iter(results_data.items()))

    for qa_item in qa_items:
        question = qa_item["question"]
        memories = qa_item["context"]
        memories_by_question[question] = memories

    for question in failed_questions:
        question["memories"] = memories_by_question[question["question"]]

    # Include the ingestion logs for each message specified as evidence (if present)
    if logs_path.exists():
        with open(logs_path, mode="r", encoding="utf-8") as file:
            log_data = json.load(file)
        
        _, log = next(iter(log_data.items())) # Assume a single conversational sample

        for question in failed_questions:
            evidence_ingestions = {}
            for msg_id in question["evidence"]:
                msg_ingestion_logs = log["ingestion"][msg_id]
                evidence_ingestions[msg_id] = msg_ingestion_logs

            question["ingestions"] = evidence_ingestions

    # Write resuling failed qa items to a file
    with open(output_path, mode="w", encoding="utf-8") as file:
        json.dump(failed_questions, file, indent=4, ensure_ascii=False)
        print(f"Written metadata of {len(failed_questions)} failed question items")


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

    parser.add_argument(
        "--locomo-set",
        type=str,
        default="locomo10_rag_with_metadata.json"
    )

    args = parser.parse_args()

    main(
        iteration=args.iteration,
        version=args.version,
        locomo_file=args.locomo_set,
    )