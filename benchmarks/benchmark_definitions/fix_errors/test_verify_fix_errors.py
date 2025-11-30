import ast
from pathlib import Path
import pytest
import yaml


def _check_function_exists(file_path: Path, func_name: str) -> bool:
    """Checks if a Python file contains a function definition with the given name."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return True
        return False
    except SyntaxError:
        pytest.fail(f"Syntax error in {file_path}. Cannot parse for function existence.")
    except FileNotFoundError:
        # Should be caught by earlier checks, but defensive
        return False

def test_verify_fix_errors():
    """
    Verification script for fix_errors/benchmark.yaml.
    This script verifies the integrity and structure of fix_error benchmark definitions:
    1. All referenced `test_file`, `unfixed_file`, and `fixed_file` paths exist.
    2. `unfixed.py` and `fixed.py` each contain a `create_agent` function.
    """
    base_dir = Path(__file__).parent
    yaml_path = base_dir / "benchmark.yaml"

    if not yaml_path.exists():
        pytest.fail(f"Error: {yaml_path} does not exist.")

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    benchmarks = data.get("benchmarks", [])
    print(f"Found {len(benchmarks)} benchmarks defined in {yaml_path.name}.")

    issues = []
    for bm in benchmarks:
        name = bm.get("name", "Unknown Benchmark")
        test_file_path_str = bm.get("test_file")
        unfixed_file_path_str = bm.get("unfixed_file")
        fixed_file_path_str = bm.get("fixed_file")

        # 1. Verify file existence
        if not test_file_path_str:
            issues.append(f"Benchmark '{name}': missing 'test_file' field.")
            continue
        if not unfixed_file_path_str:
            issues.append(f"Benchmark '{name}': missing 'unfixed_file' field.")
            continue
        if not fixed_file_path_str:
            issues.append(f"Benchmark '{name}': missing 'fixed_file' field.")
            continue

        test_full_path = Path(test_file_path_str)
        unfixed_full_path = Path(unfixed_file_path_str)
        fixed_full_path = Path(fixed_file_path_str)

        if not test_full_path.exists():
            issues.append(f"Benchmark '{name}': Test file not found: {test_full_path}")
        if not unfixed_full_path.exists():
            issues.append(f"Benchmark '{name}': Unfixed file not found: {unfixed_full_path}")
        if not fixed_full_path.exists():
            issues.append(f"Benchmark '{name}': Fixed file not found: {fixed_full_path}")
        
        # Only proceed to function checks if files exist to avoid FileNotFoundError during ast.parse
        if not (test_full_path.exists() and unfixed_full_path.exists() and fixed_full_path.exists()):
            continue

        # 2. Verify `create_agent` function exists in unfixed.py and fixed.py
        if not _check_function_exists(unfixed_full_path, "create_agent"):
            issues.append(f"Benchmark '{name}': 'create_agent' function not found in {unfixed_full_path.name}.")
        if not _check_function_exists(fixed_full_path, "create_agent"):
            issues.append(f"Benchmark '{name}': 'create_agent' function not found in {fixed_full_path.name}.")

    if issues:
        pytest.fail(f"FAILED: {len(issues)} issues found in benchmark configuration:\n" + "\n".join(issues))
    else:
        print("\nAll fix_error benchmark files verified successfully.")


if __name__ == "__main__":
    # Allow running as a script manually if needed
    test_verify_fix_errors()
