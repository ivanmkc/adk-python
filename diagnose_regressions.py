import asyncio
import pandas as pd
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from benchmarks import benchmark_orchestrator
from benchmarks.answer_generators import GeminiAnswerGenerator
from benchmarks.data_models import BenchmarkRunResult

# Colors for output
class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

async def diagnose():
    print(f"{bcolors.HEADER}Starting Regression Diagnosis Run...{bcolors.ENDC}")

    # 1. Load Context
    try:
        with open("llms.txt", "r", encoding="utf-8") as f:
            llms_context = f.read()
    except FileNotFoundError:
        print("Error: llms.txt not found.")
        return

    # 2. Configure Generators
    gen_no_context = GeminiAnswerGenerator(model_name="gemini-2.5-flash")
    gen_with_context = GeminiAnswerGenerator(model_name="gemini-2.5-flash", context=llms_context)
    
    # Label them for easier analysis later (monkey-patching or just using the string repr)
    # The orchestrator uses str(generator) for the 'answer_generator' column.
    # GeminiAnswerGenerator's __str__ typically includes the model name.
    # We might need to rely on the orchestrator's output to distinguish them if __str__ isn't unique enough
    # but the class usually formats it well. Let's check the previous output:
    # "GeminiAnswerGenerator(gemini-2.5-flash)" vs "GeminiAnswerGenerator(gemini-2.5-flash-with-context)"
    # It seems the class handles the naming if context is passed.

    generators = [gen_no_context, gen_with_context]

    # 3. Configure Suites (The ones with regressions)
    suites = [
        "benchmarks/benchmark_definitions/configure_adk_features_mc/benchmark.yaml",
        "benchmarks/benchmark_definitions/predict_runtime_behavior_mc/benchmark.yaml"
    ]

    # 4. Run Benchmarks
    print(f"Running suites: {suites}")
    results = await benchmark_orchestrator.run_benchmarks(
        benchmark_suites=suites, 
        answer_generators=generators
    )

    df = pd.DataFrame([r.model_dump() for r in results])
    
    # 5. Analyze Regressions
    # We need to pivot or self-join to compare the two generators side-by-side for each question.
    
    # Clean suite names
    df["suite"] = df["suite"].apply(lambda x: x.split("/")[-2])
    
    # Identify generator names from the dataframe
    gen_names = df['answer_generator'].unique()
    print(f"Found generators: {gen_names}")
    
    # Assuming gen_names[0] is no-context and gen_names[1] is context, but strictly:
    name_no_ctx = "GeminiAnswerGenerator(gemini-2.5-flash)"
    name_ctx = "GeminiAnswerGenerator(gemini-2.5-flash-with-context)"
    
    # Filter
    df_no = df[df['answer_generator'] == name_no_ctx].set_index(['suite', 'benchmark_name'])
    df_ctx = df[df['answer_generator'] == name_ctx].set_index(['suite', 'benchmark_name'])
    
    # Join
    comparison = df_no.join(df_ctx, lsuffix='_no', rsuffix='_ctx')
    
    # Find Regressions: Passed without context (result_no=1), Failed with context (result_ctx=0)
    regressions = comparison[(comparison['result_no'] == 1) & (comparison['result_ctx'] == 0)]
    
    print(f"\n{bcolors.BOLD}--- DIAGNOSIS REPORT ---{bcolors.ENDC}")
    print(f"Total Regressions found: {len(regressions)}")
    
    if not regressions.empty:
        for idx, row in regressions.iterrows():
            suite, name = idx
            print(f"\n{bcolors.FAIL}[REGRESSION] {suite} :: {name}{bcolors.ENDC}")
            print(f"  {bcolors.OKGREEN}No Context Answer:{bcolors.ENDC} {row['answer_no']}")
            print(f"  {bcolors.FAIL}With Context Answer:{bcolors.ENDC} {row['answer_ctx']}")
            # print(f"  Failure Reason: {row['validation_error_ctx']}") # Usually explains why the answer was wrong
            
    # Save full log for inspection
    df.to_csv("regression_debug_results.csv", index=False)
    print(f"\nFull results saved to 'regression_debug_results.csv'")

if __name__ == "__main__":
    asyncio.run(diagnose())
