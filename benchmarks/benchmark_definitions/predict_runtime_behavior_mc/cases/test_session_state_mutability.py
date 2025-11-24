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

import pytest
from google.adk.sessions import Session
from pydantic import ValidationError

def test_session_state_mutability():
    """
    Validates session state mutability (Predict Error).
    """
    # Expected behavior: The session state is mutable.
    session = Session(id="123", user_id="user", app_name="test_app")
    session.state["user"] = "Alice"
    session.state["count"] = 1
    session.state["count"] += 1
    assert session.state == {"user": "Alice", "count": 2}

    # Assert incorrect options:
    # Option A: No error is raised, the state is mutable.
    # Option B: No ValueError is raised.
    # Option C, D: The final count is 2.
