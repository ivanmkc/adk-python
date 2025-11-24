import asyncio
import itertools
from typing import List
from pathlib import Path
from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import (
    AdkAnswerGenerator,
    GeminiAnswerGenerator,
    GroundTruthAnswerGenerator,
    TrivialAnswerGenerator,
)
from benchmarks.data_models import BenchmarkRunResult
import pandas as pd

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

# Define contexts
llms_context_path = Path("llms.txt")
llm_relevant_context_path = Path("llm-relevant.txt")

try:
    with open("llms.txt", "r", encoding="utf-8") as f:
        llms_context_str = f.read()
except FileNotFoundError:
    print(f"{bcolors.WARNING}Warning: llms.txt not found. Proceeding without context.{bcolors.ENDC}")
    llms_context_str = ""

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
        # Use a lower concurrency to avoid rate limits
        GeminiAnswerGenerator(model_name="gemini-2.5-flash", context=None),
        # GeminiAnswerGenerator(model_name="gemini-2.5-flash", context=llms_context_str),
        GeminiAnswerGenerator(model_name="gemini-2.5-flash", context=llm_relevant_context_path), 
    ]
    
    print("Executing benchmarks...")
    # We pass max_concurrency=10 here to limit parallel calls
    results = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites=benchmark_suites, 
        answer_generators=answer_generators,
        max_concurrency=10
    )
    
    return results

async def main():
    try:
        results = await run_comparison()
        raw_results_df = pd.DataFrame([r.model_dump() for r in results])
        
        if 'suite' in raw_results_df.columns:
            raw_results_df["suite"] = raw_results_df["suite"].apply(lambda x: x.split("/")[-2])
        
        summary_df = (
            raw_results_df.groupby(["answer_generator", "suite"])
            .agg(
                passed=("result", "sum"),
                total=("result", "count"),
            )
        )
        summary_df["pass_rate"] = summary_df["passed"] / summary_df["total"]
        
        print(f"{bcolors.HEADER}--- Benchmark Summary ---{bcolors.ENDC}")
        print(summary_df)
        
    except Exception as e:
        print(f"{bcolors.FAIL}Error running benchmarks: {e}{bcolors.ENDC}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
