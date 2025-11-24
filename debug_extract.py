from pathlib import Path
import re
import textwrap

def _extract_code_snippet(file_path: Path) -> str:
    """Extracts the code snippet from a file."""
    with open(file_path, "r") as f:
        content = f.read()
    
    match = re.search(r"# BEGIN: CODE\n(.*?)
# END: CODE", content, re.DOTALL)
    if not match:
        # Try finding it with looser constraints to see why it failed
        print("Regex failed to match exactly.")
        m1 = re.search(r"# BEGIN: CODE", content)
        m2 = re.search(r"# END: CODE", content)
        print(f"BEGIN found: {m1 is not None}")
        print(f"END found: {m2 is not None}")
        raise ValueError(f"Could not find code snippet in {file_path}")
    
    raw_snippet = match.group(1)
    print(f"--- Raw Snippet ---\n{repr(raw_snippet)}")
    
    dedented = textwrap.dedent(raw_snippet)
    print(f"--- Dedented ---\n{repr(dedented)}")
    
    stripped = dedented.strip()
    print(f"--- Stripped ---\n{repr(stripped)}")
    return stripped

path = Path("benchmarks/ground_truth/fix_errors/test_01_single_llm_agent.py")
try:
    code = _extract_code_snippet(path)
    print(f"--- Final Code ---\n{code}")
except Exception as e:
    print(e)