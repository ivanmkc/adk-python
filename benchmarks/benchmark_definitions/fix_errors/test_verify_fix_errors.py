# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Verification script for fix_errors/benchmark.yaml.
This script verifies that all test files referenced in the benchmark YAML actually exist.
"""

from pathlib import Path
import pytest
import yaml


def test_verify_fix_errors():
    # Define paths
    base_dir = Path(__file__).parent
    yaml_path = base_dir / "benchmark.yaml"

    if not yaml_path.exists():
        pytest.fail(f"Error: {yaml_path} does not exist.")

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    benchmarks = data.get("benchmarks", [])
    print(f"Found {len(benchmarks)} benchmarks defined in {yaml_path.name}.")

    missing_files = []
    for bm in benchmarks:
        test_file_path_str = bm.get("test_file")
        if not test_file_path_str:
            print(
                f"Warning: Benchmark '{bm.get('name')}' is missing 'test_file' field."
            )
            continue

        full_path = Path(test_file_path_str)

        if not full_path.exists():
            print(f"Error: Test file not found: {full_path}")
            missing_files.append(test_file_path_str)
        else:
            # Verify placeholder presence
            try:
                content = full_path.read_text()
                if "# BEGIN: CODE" not in content or "# END: CODE" not in content:
                    print(
                        f"Error: Test file {full_path.name} missing '# BEGIN: CODE' or '# END: CODE' placeholders."
                    )
                    missing_files.append(full_path.name)
            except Exception as e:
                print(f"Error reading {full_path}: {e}")
                missing_files.append(full_path.name)

    if missing_files:
        pytest.fail(f"FAILED: {len(missing_files)} issues found. See stdout.")
    else:
        print("\nAll fix_error benchmark files verified successfully.")


if __name__ == "__main__":
    # Allow running as a script manually if needed
    test_verify_fix_errors()