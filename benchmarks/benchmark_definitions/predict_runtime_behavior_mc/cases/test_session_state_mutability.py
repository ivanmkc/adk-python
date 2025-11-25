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

from google.adk.sessions import Session


# --8<-- [start:session_state_mutability]
def code_under_test():
    session = Session(id="123", user_id="user", app_name="test_app")
    session.state["user"] = "Alice"
    session.state["count"] = 1
    session.state["count"] += 1
    return session
# --8<-- [end:session_state_mutability]


def test_session_state_mutability():
    """
    Validates session state mutability (Predict Error).
    """
    # Expected behavior: The session state is mutable.
    session = code_under_test()
    assert session.state == {"user": "Alice", "count": 2}