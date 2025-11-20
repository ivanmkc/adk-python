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


# Read context from llms.txt
try:
    with open("llms.txt", "r", encoding="utf-8") as f:
        llms_context = f.read()
except FileNotFoundError:
    print(f"{bcolors.WARNING}Warning: llms.txt not found. Proceeding without context.{bcolors.ENDC}")
    llms_context = ""

def permute(cls, **kwargs):
    """Helper to generate permutations of class instances."""
    keys = kwargs.keys()
    values = kwargs.values()
    for instance_values in itertools.product(*values):
        yield cls(**dict(zip(keys, instance_values)))

async def run_comparison(
    benchmark_suites: List[str], answer_generators
) -> List[BenchmarkRunResult]:
    """Sets up and runs the benchmark comparison."""
    print("Configuring benchmark run...")

    print("Executing benchmarks...")
    results = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites=benchmark_suites, answer_generators=answer_generators
    )

    return results


def analyze_logs(
    results_df: pd.DataFrame, generator_name: str, result_type: str = 'fail'
) -> None:
    """Filters and displays benchmark results for a specific generator and result type."""
    
    result_value = 1 if result_type.lower() == 'pass' else 0
    
    print(f"\n{bcolors.HEADER}--- Analyzing {result_type.upper()}S for {generator_name} ---{bcolors.ENDC}\n")
    
    filtered_df = results_df[
        (results_df['answer_generator'] == generator_name) & 
        (results_df['result'] == result_value)
    ]
    
    if filtered_df.empty:
        print(f"{bcolors.OKGREEN}No {result_type}s found for {generator_name}.{bcolors.ENDC}")
        return
    
    for _, row in filtered_df.iterrows():
        print(f"{bcolors.WARNING}Suite: {row['suite']}{bcolors.ENDC}")
        print(f"{bcolors.WARNING}Benchmark: {row['benchmark_name']}{bcolors.ENDC}")
        print(f"{bcolors.OKCYAN}  Answer:{bcolors.ENDC}\n    {row['answer']}")
        if result_type.lower() == 'fail':
            print(f"{bcolors.FAIL}  Validation Error:{bcolors.ENDC}\n    {row['validation_error']}")
            if "temp_test_file" in row and pd.notna(row["temp_test_file"]):
                print(f"{bcolors.OKBLUE}  Temp File:{bcolors.ENDC} {row['temp_test_file']}")
        print("-" * 40)


def main() -> None:
    """Runs the benchmark comparison and displays results."""
    benchmark_suites = [
        "benchmarks/benchmark_definitions/api_understanding_benchmarks.yaml",
        "benchmarks/benchmark_definitions/fix_error_benchmarks.yaml",
        "benchmarks/benchmark_definitions/multiple_choice_benchmarks.yaml",
    ]
    
    answer_generators = [
        GroundTruthAnswerGenerator(),
        TrivialAnswerGenerator(),
        *permute(
            GeminiAnswerGenerator,
            model_name=["gemini-2.5-flash", "gemini-2.5-pro"],
            context=[None, llms_context]
        ),
        # AdkAnswerGenerator(),
    ]

    results = asyncio.run(run_comparison(benchmark_suites, answer_generators))
    raw_results_df = pd.DataFrame([r.model_dump() for r in results])

    # Calculate summary from raw results
    summary_df = (
      raw_results_df.groupby("answer_generator")
      .agg(
          passed=("result", "sum"),
          total=("result", "count"),
          mean_latency=("latency", "mean"),
          p50_latency=("latency", lambda x: x.quantile(0.5)),
          p90_latency=("latency", lambda x: x.quantile(0.9)),
          p99_latency=("latency", lambda x: x.quantile(0.99)),
      )
    )
    summary_df["pass_rate"] = summary_df["passed"] / summary_df["total"]

    print(f"{bcolors.HEADER}--- Benchmark Summary ---{bcolors.ENDC}")
    print(summary_df)
            
    # --- Configuration ---
    # Dynamically determine the name of one of the GeminiAnswerGenerators to analyze
    gemini_generators = [
        gen.name for gen in answer_generators if isinstance(gen, GeminiAnswerGenerator)
    ]
    generator_to_analyze = gemini_generators[0] if gemini_generators else ""
    result_type_to_see = 'fail' # or 'pass'

    # If the default analysis is not useful, the user can manually change the
    # `generator_to_analyze` and `result_type_to_see` variables above to focus
    # on specific results.


if __name__ == "__main__":
    main()



