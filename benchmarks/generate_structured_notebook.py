"""Utility to generate a structured Jupyter Notebook for benchmark analysis."""

import nbformat as nbf


def create_notebook():
  nb = nbf.v4.new_notebook()

  # --- Cell 1: Imports & Setup ---
  source_1 = r"""
import asyncio
import itertools
from typing import List
from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import (
    AdkAnswerGenerator,
    GeminiAnswerGenerator,
    GeminiCliAnswerGenerator,
    GroundTruthAnswerGenerator,
    TrivialAnswerGenerator,
)
from benchmarks.data_models import BenchmarkRunResult
import pandas as pd
from pathlib import Path
from benchmarks.logger import JsonTraceLogger
import re

# Set pandas display options
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

logger = JsonTraceLogger(output_dir="traces")
"""

  # --- Cell 2: Helpers ---
  source_2 = r'''
# ANSI escape codes for colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def permute(cls, **kwargs):
    """Helper to generate permutations of class instances."""
    keys = kwargs.keys()
    values = kwargs.values()
    for instance_values in itertools.product(*values):
        yield cls(**dict(zip(keys, instance_values)))

def extract_error_type(row) -> str:
    """Extracts error type from the result row."""
    if "error_type" in row and pd.notna(row["error_type"]):
        # If it's an Enum object (from pydantic validation), get its value
        et = row["error_type"]
        if hasattr(et, "value"):
            return et.value
        return str(et)
    return "OtherError"
'''

  # --- Cell 3: Configuration ---
  source_3 = r"""
benchmark_suites = [
    "benchmarks/benchmark_definitions/api_understanding/benchmark.yaml",
    "benchmarks/benchmark_definitions/fix_errors/benchmark.yaml",
    "benchmarks/benchmark_definitions/diagnose_setup_errors_mc/benchmark.yaml",
    "benchmarks/benchmark_definitions/configure_adk_features_mc/benchmark.yaml",
    "benchmarks/benchmark_definitions/predict_runtime_behavior_mc/benchmark.yaml",
]

answer_generators = [
    GroundTruthAnswerGenerator(),
    TrivialAnswerGenerator(),
    *permute(
        GeminiAnswerGenerator,
        model_name=["gemini-2.5-flash"],
        context=[None, Path("llms.txt"), Path("llms-relevant.txt")],
    ),
    GeminiCliAnswerGenerator(model_name="gemini-2.5-flash"),
]
"""

  # --- Cell 4: Execution Logic ---
  source_4 = r'''
async def run_comparison() -> List[BenchmarkRunResult]:
    """Sets up and runs the benchmark comparison."""
    print("Configuring benchmark run...")
    
    print("Executing benchmarks...")
    results = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites=benchmark_suites, 
        answer_generators=answer_generators,
        max_concurrency=20,
        logger=logger,
    )
    
    return results
'''

  # --- Cell 5: Run Benchmarks ---
  source_5 = r"""
# Execute the benchmarks
# Note: In a notebook environment (IPykernel), top-level await is supported.
results = await run_comparison()
"""

  # --- Cell 6: Data Processing ---
  source_6 = r"""
raw_results_df = pd.DataFrame([r.model_dump() for r in results])

if not raw_results_df.empty:
    raw_results_df["suite"] = raw_results_df["suite"].apply(lambda x: x.split("/")[-2])
    raw_results_df["final_error_type"] = raw_results_df.apply(extract_error_type, axis=1)
else:
    print("No results returned.")
"""

  # --- Cell 7: Summary Analysis ---
  source_7 = r"""
if not raw_results_df.empty:
    # 1. General Pass/Total Summary
    summary_df = (
        raw_results_df.groupby(["answer_generator", "suite"])
        .agg(
            passed=("result", "sum"),
            total=("result", "count"),
        )
    )
    summary_df["pass_rate"] = summary_df["passed"] / summary_df["total"]

    print(f"{bcolors.HEADER}--- Benchmark Summary ---\n{bcolors.ENDC}")
    print(summary_df)
"""

  # --- Cell 8: Detailed Error Breakdown ---
  source_8 = r"""
if not raw_results_df.empty:
    # 2. Detailed Error Breakdown with Ratios
    failed_df = raw_results_df[raw_results_df["result"] == 0]
    
    if not failed_df.empty:
        # Calculate counts per error type
        error_counts = (
            failed_df.groupby(["answer_generator", "suite", "final_error_type"])
            .size()
            .reset_index(name="count")
        )
        
        # Merge with total counts to calculate ratios relative to total runs
        total_counts = raw_results_df.groupby(["answer_generator", "suite"]).size().reset_index(name="total_runs")
        
        # Merge error counts with totals
        error_summary = pd.merge(error_counts, total_counts, on=["answer_generator", "suite"])
        
        # Calculate failure rate
        error_summary["failure_ratio"] = error_summary["count"] / error_summary["total_runs"]
        
        print(f"{bcolors.HEADER}--- Detailed Error Breakdown ---\n{bcolors.ENDC}")
        # Sort for better readability
        error_summary = error_summary.sort_values(["answer_generator", "suite", "count"], ascending=[True, True, False])
        print(error_summary.to_string(index=False))
    else:
        print(f"{bcolors.OKGREEN}No failures detected!\n{bcolors.ENDC}")
"""

  # --- Cell 9: Log Inspection (Deep Dive) ---
  # Note escaping for f-string newline
  source_9 = r"""
# Debug Logs for specific generators
if not raw_results_df.empty:
    failed_df = raw_results_df[raw_results_df["result"] == 0]
    
    # --- DETAILED DEBUG FOR GEMINI CLI FAILURES ---
    print(f"\n{bcolors.FAIL}--- DETAILED GEMINI CLI FAILURES ---\n{bcolors.ENDC}")
    cli_failures = failed_df[failed_df["answer_generator"].str.contains("GeminiCliAnswerGenerator")]
    
    if not cli_failures.empty:
        # Print just the first 3 failures to avoid overwhelming output
        for idx, row in cli_failures.head(3).iterrows():
            print(f"\nBenchmark: {row['benchmark_name']} (Suite: {row['suite']})")
            print(f"Error Type: {row['final_error_type']}")
            print(f"Full Validation Error:\n{row['validation_error']}")
            print("-" * 60)
    else:
        print("No Gemini CLI failures found in this run.")
"""

  nb.cells = [
      nbf.v4.new_code_cell(source_1),
      nbf.v4.new_code_cell(source_2),
      nbf.v4.new_code_cell(source_3),
      nbf.v4.new_code_cell(source_4),
      nbf.v4.new_code_cell(source_5),
      nbf.v4.new_code_cell(source_6),
      nbf.v4.new_code_cell(source_7),
      nbf.v4.new_code_cell(source_8),
      nbf.v4.new_code_cell(source_9),
  ]

  with open("benchmark_run.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

  print("Successfully created benchmark_run.ipynb with structured cells.")


if __name__ == "__main__":
  create_notebook()
