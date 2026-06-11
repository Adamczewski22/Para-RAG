from argparse import ArgumentParser
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
MEMOBASE_DIR = ROOT / "external/memobase/docs/experiments/locomo-benchmark"
RESULTS_DIR = ROOT / "results/locomo"
DATASET_PATH = ROOT / "data/locomo/locomo10_rag_with_metadata.json"

RUN_LOCOMO_MODULE = "benchmarks.run_locomo_pararag"
RERUN_LOCOMO_MODULE_PATH = ROOT / "benchmarks/rerun_locomo_from_results.py"
RERUN_DEDUPLICATION_MODULE = "benchmarks.run_locomo_deduplication"
RERUN_PROFILES_MODULE = "benchmarks.run_locomo_profiles"

EVAL_SCRIPT_PATH = MEMOBASE_DIR / "evals.py"
GEN_SCORE_SCRIPT_PATH = MEMOBASE_DIR / "generate_scores.py"


def run_cmd(cmd: list[str], cwd: Path | None = None) -> None:
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True) # Default cwd is the current working directory


def main(
    iteration_name: str,
    version: str,
    rerun: bool,
    previous_result_path: str,
    deduplication_rerun: bool,
    previous_logs_path: str | None,
    rerun_retrieval: bool,
    rerun_profiles: bool,
) -> None:
    result_file_name = f"{iteration_name}_result_{version}.json"
    result_path = RESULTS_DIR / result_file_name

    logs_file_name = f"{iteration_name}_logs_{version}.html"
    logs_path = RESULTS_DIR / logs_file_name

    json_logs_file_name = f"{iteration_name}_logs_{version}.json"
    json_logs_path = RESULTS_DIR / "debug" / json_logs_file_name

    # Standard locomo run
    if not rerun and not deduplication_rerun and not rerun_profiles:
        cmd = [
            sys.executable, # current Python executable (venv)
            "-m", RUN_LOCOMO_MODULE,
            "--memory-version", iteration_name,
            "--dataset-path", str(DATASET_PATH),
            "--output-path", str(result_path),
            "--logs-path", str(logs_path),
            "--json-logs-path", str(json_logs_path),
        ]
        # Add rerun retrieval flag if true
        if rerun_retrieval:
            cmd.append("--rerun-retrieval")

        # Run command
        run_cmd(cmd, cwd=ROOT)

    # Locomo rerun
    elif rerun:
        run_cmd([
            sys.executable,
            str(RERUN_LOCOMO_MODULE_PATH),
            "--results-path", previous_result_path,
            "--output-path", str(result_path),
        ])
    
    # Deduplication rerun
    elif deduplication_rerun:
        run_cmd([
            sys.executable,
            "-m", RERUN_DEDUPLICATION_MODULE,
            "--memory-version", iteration_name,
            "--dataset-path", str(DATASET_PATH),
            "--output-path", str(result_path),
            "--logs-path", str(logs_path),
            "--json-logs-path", str(json_logs_path),
            "--previous-json-logs-path", previous_logs_path,
        ])

    # Profiles rerun
    elif rerun_profiles:
        run_cmd([
            sys.executable,
            "-m", RERUN_PROFILES_MODULE,
            "--memory-version", iteration_name,
            "--dataset-path", str(DATASET_PATH),
            "--output-path", str(result_path),
            "--logs-path", str(logs_path),
            "--json-logs-path", str(json_logs_path),
            "--previous-json-logs-path", previous_logs_path,
        ])

    # Run evaluation
    eval_file_name = f"{iteration_name}_eval_{version}.json"
    eval_path = RESULTS_DIR / eval_file_name
    run_cmd([
        sys.executable,
        str(EVAL_SCRIPT_PATH),
        "--input_file", str(result_path),
        "--output_file", str(eval_path),
    ], cwd=MEMOBASE_DIR)

    # Generate scores
    run_cmd([
        sys.executable,
        str(GEN_SCORE_SCRIPT_PATH),
        "--input_path", str(eval_path),
    ], cwd=MEMOBASE_DIR)
    

if __name__ == "__main__":
    parser = ArgumentParser()

    # Positional args
    parser.add_argument(
        "iteration_name",
        type=str,
    )
    parser.add_argument(
        "version",
        type=str,
    )
    # Rerun locomo mode
    parser.add_argument(
        "--rerun",
        action="store_true",
    )
    parser.add_argument(
        "--previous-result-path",
        type=str,
        default=str(RESULTS_DIR / "simple_decomposition_result_2.json"),
    )
    # Rerun deduplication mode
    parser.add_argument(
        "--rerun-deduplication",
        action="store_true",
    )
    parser.add_argument(
        "--previous-logs-path",
        type=str,
    )
    # Rerun retrieval mode
    parser.add_argument(
        "--rerun-retrieval",
        action="store_true",
    )
    # Rerun profiles mode
    parser.add_argument(
        "--rerun-profiles",
        action="store_true",
    )
    args = parser.parse_args()

    main(
        iteration_name=args.iteration_name,
        version=args.version,
        rerun=args.rerun,
        previous_result_path=args.previous_result_path,
        deduplication_rerun=args.rerun_deduplication,
        previous_logs_path=args.previous_logs_path,
        rerun_retrieval=args.rerun_retrieval,
        rerun_profiles=args.rerun_profiles,
    )
