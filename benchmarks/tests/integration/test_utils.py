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

"""Shared utilities for integration tests."""

from pathlib import Path
from benchmarks.data_models import FixErrorBenchmarkCase

def create_fix_error_benchmark_case(
    case_path: Path,
    name: str = "Test Fix Error",
    description: str = "Fix a bug",
    requirements: list[str] | None = None
) -> FixErrorBenchmarkCase:
    """
    Creates a standardized FixErrorBenchmarkCase for testing.
    
    Args:
        case_path: The directory containing the test files (unfixed.py, fixed.py, test_agent.py).
        name: The name of the benchmark case.
        description: The description of the benchmark case.
        requirements: Optional list of requirements for the case.
        
    Returns:
        A configured FixErrorBenchmarkCase instance.
    """
    test_file_path = case_path / "test_agent.py"
    unfixed_file_path = case_path / "unfixed.py"
    fixed_file_path = case_path / "fixed.py"

    return FixErrorBenchmarkCase(
        name=name,
        description=description,
        test_file=test_file_path,
        unfixed_file=unfixed_file_path,
        fixed_file=fixed_file_path,
        requirements=requirements
    )
