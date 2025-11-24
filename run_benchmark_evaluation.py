import argparse
import asyncio
import json
from pathlib import Path

from benchmarks.benchmark_orchestrator import run_benchmarks
from benchmarks.data_models import BenchmarkRunResult
from benchmarks.answer_generators.gemini_answer_generator import (
    GeminiAnswerGenerator,
)
from benchmarks.logger import JsonTraceLogger


async def main() -> None:
    """Runs a benchmark suite and prints the results."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "benchmark_suite",
        type=str,
        help="Path to the benchmark suite file (e.g., 'benchmarks/benchmark_definitions/fix_errors/benchmark.yaml').",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="benchmark_results.json",
        help="Path to the output file for the results.",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="gemini-2.5-flash",
        help="The name of the model to use for the Gemini answer generator.",
    )
    parser.add_argument(
        "--max_concurrency",
        type=int,
        default=1, # Setting to 1 for predictability
        help="The maximum number of concurrent benchmark runs.",
    )
    parser.add_argument(
        "--trace_output_dir", # NEW ARGUMENT
        type=Path,
        default=None,
        help="Directory to save JSONL trace logs.",
    )
    args = parser.parse_args()

    # Removed clearing of trace.md

    answer_generators = [
        GeminiAnswerGenerator(model_name=args.model_name),
    ]

    # Instantiate logger if trace_output_dir is provided
    logger = None
    if args.trace_output_dir:
        logger = JsonTraceLogger(output_dir=args.trace_output_dir)

    results: list[BenchmarkRunResult] = await run_benchmarks(
        benchmark_suites=[args.benchmark_suite],
        answer_generators=answer_generators,
        max_concurrency=args.max_concurrency,
        logger=logger,
    )

    results_dict = [result.model_dump() for result in results]

    # Create the directory for the output file if it doesn't exist
    Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(results_dict, f, indent=2)

    print(f"Benchmark results saved to {args.output_file}")


if __name__ == "__main__":
    asyncio.run(main())
