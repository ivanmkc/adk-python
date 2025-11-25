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

"""Verifies that all fix_errors benchmark snippets have required markers."""

from pathlib import Path
import pytest

# Path to the fix_errors tests directory
FIX_ERRORS_TESTS_DIR = Path(__file__).parents[1] / "benchmark_definitions" / "fix_errors" / "tests"

REQUIRED_MARKERS = [
    "# LLM_CONTEXT_BEGIN",
    "# LLM_CONTEXT_END",
    "# BEGIN: CODE",
    "# END: CODE",
]

def get_snippet_files():
    """Yields all python files in the fix_errors tests directory."""
    if not FIX_ERRORS_TESTS_DIR.exists():
        return []
    for file_path in FIX_ERRORS_TESTS_DIR.glob("test_*.py"):
        yield file_path

@pytest.mark.parametrize("file_path", get_snippet_files(), ids=lambda p: p.name)
def test_snippet_has_required_markers(file_path):
    """Checks if a snippet file contains all required markers."""
    content = file_path.read_text(encoding="utf-8")
    missing_markers = [marker for marker in REQUIRED_MARKERS if marker not in content]
    
    assert not missing_markers, f"File {file_path.name} is missing markers: {missing_markers}"
