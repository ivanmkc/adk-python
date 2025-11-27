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
Defines standard candidate AnswerGenerators for benchmarking.
This file serves as a central registry of configured generators to ensure consistency
across different evaluation runs.
"""

from benchmarks.answer_generators.adk_agents import create_default_adk_agent
from benchmarks.answer_generators.adk_answer_generator import AdkAnswerGenerator
from benchmarks.answer_generators.gemini_answer_generator import GeminiAnswerGenerator
from benchmarks.answer_generators.gemini_cli_answer_generator import GeminiCliAnswerGenerator
from benchmarks.answer_generators.ground_truth_answer_generator import GroundTruthAnswerGenerator
from benchmarks.answer_generators.trivial_answer_generator import TrivialAnswerGenerator

# Define model constants
GEMINI_2_5_FLASH = "gemini-2.5-flash"
GEMINI_2_5_PRO = "gemini-2.5-pro"

# Create pre-configured agent instances for AdkAnswerGenerator
# You can add more specialized agents here (e.g., with different instructions or tools)
# by adding them to benchmarks/answer_generators/adk_agents.py and importing them.
agent_flash = create_default_adk_agent(model_name=GEMINI_2_5_FLASH)
agent_pro = create_default_adk_agent(model_name=GEMINI_2_5_PRO)

# Dictionary of standard candidate generators
CANDIDATE_GENERATORS = {
    # ADK Agent-based generators (The primary targets for evaluation)
    "adk_gemini_2_5_flash": AdkAnswerGenerator(agent=agent_flash),
    "adk_gemini_2_5_pro": AdkAnswerGenerator(agent=agent_pro),
    
    # Direct Gemini SDK generators (Baselines)
    "gemini_sdk_2_5_flash": GeminiAnswerGenerator(model_name=GEMINI_2_5_FLASH),
    "gemini_sdk_2_5_pro": GeminiAnswerGenerator(model_name=GEMINI_2_5_PRO),
    
    # Gemini CLI generators (Alternative baseline)
    "gemini_cli_2_5_flash": GeminiCliAnswerGenerator(model_name=GEMINI_2_5_FLASH),
    
    # Control generators
    "ground_truth": GroundTruthAnswerGenerator(),
    "trivial": TrivialAnswerGenerator(),
}
