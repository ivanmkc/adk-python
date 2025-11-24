import asyncio
import pandas as pd
from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import (
    GeminiAnswerGenerator,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def main():
    benchmark_suites = [
        "benchmarks/benchmark_definitions/fix_errors/benchmark.yaml",
    ]
    answer_generators_to_test = [
        GeminiAnswerGenerator(),
    ]
    
    # Clear trace file before running for full suite
    with open("trace.md", "w", encoding="utf-8") as f:
        f.write("# Benchmark Trace (Full Fix Errors Suite)\n\n")

    print("Executing full fix_errors benchmark evaluation...")
    results = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites,
        answer_generators_to_test,
        # No case_name filter here to run all cases
    )
    raw_results_df = pd.DataFrame([r.model_dump() for r in results])

    # Calculate summary from raw results
    summary_df = (
        raw_results_df.groupby("answer_generator")
        .agg(
            passed=("result", "sum"),
            total=("result", "count"),
            mean_latency=("latency", "mean"),
        )
    )
    summary_df["pass_rate"] = summary_df["passed"] / summary_df["total"]

    print("\n--- Evaluation Summary (Full Fix Errors Suite) ---")
    print(summary_df)

    print("\n--- Raw Results (Full Fix Errors Suite) ---")
    print(raw_results_df)

    # Print failures
    failed_df = raw_results_df[raw_results_df["result"] == 0]
    if not failed_df.empty:
        print("\n--- Failures ---")
        for _, row in failed_df.iterrows():
            print(f"Benchmark: {row['benchmark_name']}")
            print(f"Generator: {row['answer_generator']}")
            print(f"Error: {row['validation_error']}\n")


if __name__ == "__main__":
    asyncio.run(main())
