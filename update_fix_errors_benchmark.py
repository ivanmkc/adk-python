import ast
from pathlib import Path
import yaml
import textwrap

def extract_docstring_and_name(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    module = ast.parse(content)
    docstring = ast.get_docstring(module)
    
    # The name in benchmark.yaml is the full docstring.
    # The description can also be the docstring for simplicity.
    name = docstring.strip() if docstring else file_path.stem.replace('_', ' ').title()
    description = name # For now, use the same as name

    return name, description


all_benchmarks_data = []
test_files = [
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_02_agent_with_tool.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_01_single_llm_agent.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_03_agent_with_output_schema.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_04_sequential_agent.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_05_parallel_agent.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_06_loop_agent.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_07_agent_delegation.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_08_custom_agent.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_10_agent_with_state_management.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_11_in_memory_runner_direct.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_12_app_with_plugin.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_13_code_executor.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_14_agent_with_litellm_openai.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_15_callbacks.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_16_generate_content_config.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_17_input_schema.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_18_include_contents_none.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_19_artifacts.py",
    "/Users/ivanmkc/Documents/code/adk-python/benchmarks/benchmark_definitions/fix_errors/tests/test_20_expanded_callbacks.py"
]

for test_file_path_abs in test_files:
    test_file_path = Path(test_file_path_abs)
    name, description = extract_docstring_and_name(test_file_path)
    
    # Relative path from project root
    relative_path_str = str(test_file_path.relative_to(Path.cwd()))

    benchmark_entry = {
        "name": name,
        "description": description,
        "benchmark_type": "fix_error",
        "test_file": relative_path_str,
        "start_line": 1, # Placeholder
        "end_line": 1,   # Placeholder
    }
    all_benchmarks_data.append(benchmark_entry)

# Write to benchmark.yaml
output_yaml_path = Path("benchmarks/benchmark_definitions/fix_errors/benchmark.yaml")
with open(output_yaml_path, "w", encoding="utf-8") as f:
    yaml.dump({"benchmarks": all_benchmarks_data}, f, sort_keys=False, indent=2)

print(f"Updated {output_yaml_path} with {len(all_benchmarks_data)} benchmark entries.")
