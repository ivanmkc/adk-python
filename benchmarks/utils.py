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

"""Utility functions for benchmarks."""

import itertools

def permute(cls, **kwargs):
    """Helper to generate permutations of class instances.
    
    Args:
        cls: The class to instantiate.
        **kwargs: Dictionary where keys are argument names and values are lists of possible values.
        
    Yields:
        Instances of cls with all combinations of arguments.
    """
    keys = kwargs.keys()
    values = kwargs.values()
    for instance_values in itertools.product(*values):
        yield cls(**dict(zip(keys, instance_values)))
