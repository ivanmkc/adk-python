import asyncio
from typing import List
from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import (
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

async def run_comparison() -> List[BenchmarkRunResult]:
    """Sets up and runs the benchmark comparison."""
    print("Configuring benchmark run...")
    
    benchmark_suites = [
        # "benchmarks/benchmark_definitions/fix_error_benchmarks.yaml",
        "benchmarks/benchmark_definitions/api_understanding_benchmarks.yaml",
    ]
    
    answer_generators = [
        GroundTruthAnswerGenerator(), 
        TrivialAnswerGenerator()
    ]
    
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
    results = asyncio.run(run_comparison())
    raw_results_df = pd.DataFrame([r.model_dump() for r in results])

    # Calculate summary from raw results
    summary_df = (
      raw_results_df.groupby("answer_generator")["result"]
      .agg(["sum", "count"])
      .rename(columns={"sum": "passed", "count": "total"})
    )
    summary_df["pass_rate"] = summary_df["passed"] / summary_df["total"]

    print(f"{bcolors.HEADER}--- Benchmark Summary ---{bcolors.ENDC}")
    print(summary_df)
            
    # --- Configuration ---
    generator_to_analyze = 'GroundTruthAnswerGenerator' 
    result_type_to_see = 'fail' 

    analyze_logs(
        results_df=raw_results_df,
        generator_name=generator_to_analyze,
        result_type=result_type_to_see
    )

if __name__ == "__main__":
    main()



