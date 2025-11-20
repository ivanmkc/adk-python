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

"""Tests for the ground truth files."""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

# Ensure src is in path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from google.genai import types

GROUND_TRUTH_DIR = Path("benchmarks/ground_truth/fix_error_suite")
GROUND_TRUTH_FILES = list(GROUND_TRUTH_DIR.glob("test_*.py"))


@pytest.mark.parametrize(
    "ground_truth_file",
    GROUND_TRUTH_FILES,
    ids=[f.name for f in GROUND_TRUTH_FILES],
)
@pytest.mark.asyncio
async def test_ground_truth_file(ground_truth_file: Path, mocker):
  """Tests a single ground truth file."""
  mock_generate_content = mocker.patch(
      "google.adk.models.google_llm.GoogleLlm.generate_content_async"
  )
  response = types.GenerateContentResponse()
  response.candidates = [
      types.Candidate(
          content=types.Content(
              parts=[types.Part(text="This is a mocked response.")], role="model"
          )
      )
  ]
  mock_generate_content.return_value = response

  module_name = ".".join(ground_truth_file.with_suffix("").parts)
  module = importlib.import_module(module_name)

  test_functions = [
      obj
      for name, obj in inspect.getmembers(module)
      if inspect.iscoroutinefunction(obj) and name.startswith("test_")
  ]

  for test_func in test_functions:
    await test_func()
