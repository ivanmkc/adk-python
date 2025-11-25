
import asyncio
import itertools
from typing import List
from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import (
    AdkAnswerGenerator,
    GeminiAnswerGenerator,
    GroundTruthAnswerGenerator,
    TrivialAnswerGenerator,
)
from benchmarks.data_models import BenchmarkRunResult
import pandas as pd
from pathlib import Path
from benchmarks.logger import JsonTraceLogger


# Set pandas display options
pd.set_option('display.max_colwidth', None)

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

logger = JsonTraceLogger(output_dir="traces")

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
    
    answer_generators = [
        GroundTruthAnswerGenerator(),
        TrivialAnswerGenerator(),
        *permute(
            GeminiAnswerGenerator,
            model_name=["gemini-2.5-flash"],
            context=[None, Path("llms.txt"), Path("llms-relevant.txt")],
        ),
        # AdkAnswerGenerator(),
    ]
    
    print("Executing benchmarks...")
    results = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites=benchmark_suites, 
        answer_generators=answer_generators,
        max_concurrency=50,
        logger=logger,
    )
    
    return results

def analyze_logs(
    results_df: pd.DataFrame, generator_name: str, result_type: str = 'fail'
) -> None:
    """Filters and displays benchmark results for a specific generator and result type."""
    
    print(f"{bcolors.HEADER}--- Analyzing {result_type.upper()}S for {generator_name} ---{bcolors.ENDC}")
    
    if result_type.lower() == 'pass':
         filtered_df = results_df[
            (results_df['answer_generator'] == generator_name) & 
            (results_df['result_type'] == 'pass')
        ]
    elif result_type.lower() == 'fail':
        # Match any fail
        filtered_df = results_df[
            (results_df['answer_generator'] == generator_name) & 
            (results_df['result_type'] != 'pass')
        ]
    else:
        # specific fail type
        filtered_df = results_df[
            (results_df['answer_generator'] == generator_name) & 
            (results_df['result_type'] == result_type)
        ]
    
    if filtered_df.empty:
        print(f"{bcolors.OKGREEN}No {result_type}s found for {generator_name}.{bcolors.ENDC}")
        return
    
    for _, row in filtered_df.iterrows():
        print(f"{bcolors.WARNING}Suite: {row['suite']}{bcolors.ENDC}")
        print(f"{bcolors.WARNING}Benchmark: {row['benchmark_name']}{bcolors.ENDC}")
        print(f"{bcolors.WARNING}Result Type: {row['result_type']}{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}  Answer:{bcolors.ENDC}\n    {row['answer']}")
        if row['result_type'] != 'pass':
            print(f"{bcolors.FAIL}  Validation Error:{bcolors.ENDC}\n    {row['validation_error']}")
            if "temp_test_file" in row and pd.notna(row["temp_test_file"]):
                print(f"{bcolors.OKBLUE}  Temp File:{bcolors.ENDC} {row['temp_test_file']}")
        print("-" * 40)

async def main():
    # Execute the benchmarks
    results = await run_comparison()
    raw_results_df = pd.DataFrame([r.model_dump() for r in results])

    print(raw_results_df.columns)
    raw_results_df["suite"] = raw_results_df["suite"].apply(lambda x: x.split("/")[-2])

    # Calculate summary from raw results
    summary_df = (
        raw_results_df.groupby(["answer_generator", "suite", "result_type"])
        .size()
        .unstack(fill_value=0)
    )

    if "pass" in summary_df.columns:
        summary_df["total"] = summary_df.sum(axis=1)
        summary_df["pass_rate"] = summary_df["pass"] / summary_df["total"]
    else:
        # Handle case where no tests passed
        summary_df["total"] = summary_df.sum(axis=1)
        summary_df["pass_rate"] = 0.0

    print(f"{bcolors.HEADER}--- Benchmark Summary ---{bcolors.ENDC}")
    print(summary_df)

if __name__ == "__main__":
    asyncio.run(main())
