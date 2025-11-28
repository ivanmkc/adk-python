
import json
import yaml
from pathlib import Path
import difflib
import sys

def load_benchmark_map():
    yaml_path = Path("benchmarks/benchmark_definitions/fix_errors/benchmark.yaml")
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    mapping = {}
    for bm in data.get("benchmarks", []):
        mapping[bm['name']] = bm['test_file']
    return mapping

def extract_code_block(content):
    """Extracts code between BEGIN: CODE and END: CODE markers."""
    import re
    match = re.search(r"# BEGIN: CODE\n(.*?)# END: CODE", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def analyze_trace(trace_file):
    print(f"Analyzing trace: {trace_file}")
    
    benchmark_map = load_benchmark_map()
    
    with open(trace_file, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
                
            if event.get("event_type") == "test_result" and event.get("data", {}).get("result") != "pass":
                data = event["data"]
                bm_name = data.get("benchmark_name")
                
                # We only care about fix_errors for code diffs
                if bm_name not in benchmark_map:
                    continue
                    
                print(f"\n{'='*80}")
                print(f"FAILURE: {bm_name}")
                print(f"Validation Error: {data.get('validation_error')}")
                
                temp_file = data.get("temp_test_file")
                original_file = benchmark_map.get(bm_name)
                
                if temp_file and Path(temp_file).exists() and original_file and Path(original_file).exists():
                    temp_content = Path(temp_file).read_text()
                    orig_content = Path(original_file).read_text()
                    
                    actual_code = extract_code_block(temp_content)
                    expected_code = extract_code_block(orig_content)
                    
                    if actual_code and expected_code:
                        print(f"\n--- Expected Code ({original_file}) ---")
                        print(expected_code)
                        print(f"\n--- Actual Generated Code ({temp_file}) ---")
                        print(actual_code)
                        
                        print("\n--- Diff ---")
                        diff = difflib.unified_diff(
                            expected_code.splitlines(),
                            actual_code.splitlines(),
                            fromfile="Expected",
                            tofile="Actual",
                            lineterm=""
                        )
                        for line in diff:
                            print(line)
                    else:
                        print("Could not extract code blocks for comparison.")
                else:
                    print(f"Files missing for comparison.\nTemp: {temp_file} (Exists: {Path(temp_file).exists() if temp_file else False})\nOriginal: {original_file} (Exists: {Path(original_file).exists() if original_file else False})")

if __name__ == "__main__":
    analyze_trace("traces/trace_2025-11-27_16-29-11.jsonl")
