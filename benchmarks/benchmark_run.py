"""Script to run benchmarks and analyze results."""

import asyncio
from typing import List

import pandas as pd

from benchmarks import benchmark_orchestrator
from benchmarks.benchmark_candidates import CANDIDATE_GENERATORS
from benchmarks.data_models import BenchmarkRunResult
from benchmarks.logger import JsonTraceLogger

# Set pandas display options
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", None)


# %%
# ANSI escape codes for colors
class Bcolors:
  HEADER = "\033[95m"
  OKBLUE = "\033[94m"
  OKCYAN = "\033[96m"
  OKGREEN = "\033[92m"
  WARNING = "\033[93m"
  FAIL = "\033[91m"
  ENDC = "\033[0m"
  BOLD = "\033[1m"
  UNDERLINE = "\033[4m"


logger = JsonTraceLogger(output_dir="traces")


# %%
async def run_comparison() -> List[BenchmarkRunResult]:
  """Sets up and runs the benchmark comparison."""
  print("Configuring benchmark run...")

  benchmark_suites = [
      "benchmarks/benchmark_definitions/api_understanding/benchmark.yaml",
      "benchmarks/benchmark_definitions/fix_errors/benchmark.yaml",
      "benchmarks/benchmark_definitions/diagnose_setup_errors_mc/benchmark.yaml",
      "benchmarks/benchmark_definitions/configure_adk_features_mc/benchmark.yaml",
      "benchmarks/benchmark_definitions/predict_runtime_behavior_mc/benchmark.yaml",
  ]

  answer_generators = CANDIDATE_GENERATORS

  print("Executing benchmarks...")
  benchmark_results = await benchmark_orchestrator.run_benchmarks(
      benchmark_suites=benchmark_suites,
      answer_generators=answer_generators,
      max_concurrency=20,
      logger=logger,
  )

  return benchmark_results


def extract_error_type(row) -> str:
  """Extracts error type from the result row."""
  if "error_type" in row and pd.notna(row["error_type"]):
    # If it's an Enum object (from pydantic validation), get its value
    et = row["error_type"]
    if hasattr(et, "value"):
      return et.value
    return str(et)
  return "OtherError"


# %%
async def main():
  # Execute the benchmarks
  benchmark_run_results = await run_comparison()

  raw_results_df = pd.DataFrame([r.model_dump() for r in benchmark_run_results])

  if not raw_results_df.empty:
    raw_results_df["suite"] = raw_results_df["suite"].apply(
        lambda x: x.split("/")[-2]
    )
    raw_results_df["final_error_type"] = raw_results_df.apply(
        extract_error_type, axis=1
    )

    # 1. General Pass/Total Summary
    summary_df = raw_results_df.groupby(["answer_generator", "suite"]).agg(
        passed=("result", "sum"),
        total=("result", "count"),
    )
    summary_df["pass_rate"] = summary_df["passed"] / summary_df["total"]

    print(f"{Bcolors.HEADER}--- Benchmark Summary ---\n{Bcolors.ENDC}")
    print(summary_df)
    print("\n")

    # 2. Detailed Error Breakdown with Ratios
    # Filter for failures only
    failed_df = raw_results_df[raw_results_df["result"] == 0]

    if not failed_df.empty:
      # Calculate counts per error type
      error_counts = (
          failed_df.groupby(["answer_generator", "suite", "final_error_type"])
          .size()
          .reset_index(name="count")
      )

      # Merge with total counts to calculate ratios relative to total runs
      # First, get total counts per generator/suite group
      total_counts = (
          raw_results_df.groupby(["answer_generator", "suite"])
          .size()
          .reset_index(name="total_runs")
      )

      # Merge error counts with totals
      error_summary = pd.merge(
          error_counts, total_counts, on=["answer_generator", "suite"]
      )

      # Calculate failure rate for each specific error type
      error_summary["failure_ratio"] = (
          error_summary["count"] / error_summary["total_runs"]
      )

      print(f"{Bcolors.HEADER}--- Detailed Error Breakdown ---\n{Bcolors.ENDC}")
      # Sort for better readability
      error_summary = error_summary.sort_values(
          ["answer_generator", "suite", "count"], ascending=[True, True, False]
      )
      print(error_summary.to_string(index=False))

      # --- DETAILED DEBUG FOR GEMINI CLI FAILURES ---
      print(
          f"\n{Bcolors.FAIL}--- DETAILED GEMINI CLI FAILURES"
          f" ---\n{Bcolors.ENDC}"
      )
      cli_failures = failed_df[
          failed_df["answer_generator"].str.contains("GeminiCliAnswerGenerator")
      ]
      if not cli_failures.empty:
        # Print just the first 3 failures to avoid overwhelming output
        for _, failure_row in cli_failures.head(3).iterrows():
          print(
              f"\nBenchmark: {failure_row['benchmark_name']} (Suite:"
              f" {failure_row['suite']})"
          )
          print(f"Error Type: {failure_row["final_error_type"]}")
          print(f"Full Validation Error:\n{failure_row["validation_error"]}")
          print("-" * 60)
      else:
        print("No Gemini CLI failures found in this run.")
      # -----------------------------------------------
    else:
      print(f"{Bcolors.OKGREEN}No failures detected!{Bcolors.ENDC}")
  else:
    print("No results returned.")


if __name__ == "__main__":
  asyncio.run(main())
