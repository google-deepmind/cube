# Copyright 2025 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

r"""Creates a JSON file containing a list of root nodes to start KB traversal.

The script reads a dictionary of root nodes from constants.py file.
The dictionary contains Wikidata IDs as keys and names of the nodes as values.
It then creates a JSON file containing a list of dictionaries as cache to start
the KB traversal.

Example usage:

  python3 create_root_cache.py
  --concept=cuisine     --root_cache_file_dir=temps/
"""

import json
import os
from typing import Dict, List

from absl import app
from absl import flags

from cube_t2i.cube_extraction import constants


_CONCEPT = flags.DEFINE_string(
    name='concept',
    default=None,  # For list of valid concepts, refer constants.py
    help='Name of the concept that is being considered',
    required=True,
)

_ROOT_CACHE_FILE_DIR = flags.DEFINE_string(
    name='root_cache_file_dir',
    default=None,
    help='Directory to store the JSON cache file consisting of root nodes.',
    required=True,
)


def create_root_cache_nodes(root_dict: Dict[str, str]) -> List[Dict[str, str]]:
  """Create a list of dictionaries for pre-caching from a dictionary.

  Args:
    root_dict: A dictionary where keys are Wikidata IDs and values are names of
      ids.

  Returns:
    A list of dictionaries, where each dictionary represents a node with the
    keys 'id', 'name' and 'root'
  """
  cache_nodes = []
  for id_, name in root_dict.items():
    cache_nodes.append(
        {'id': id_, 'name': name, 'root': name}
    )  # root is same as name for first hop
  return cache_nodes


def main(_):
  """Create and save the root nodes to a JSON file."""

  if not os.path.exists(_ROOT_CACHE_FILE_DIR.value):
    os.makedirs(_ROOT_CACHE_FILE_DIR.value)

  output_file_path = os.path.join(
      _ROOT_CACHE_FILE_DIR.value, f'{_CONCEPT.value}_root_nodes.json'
  )

  # Check if the file exists
  if os.path.exists(output_file_path):
    return

  # Load the root nodes and make a cache json file
  # Add a new if statement for a newly introduced concept
  if _CONCEPT.value == 'cuisine':
    root_dict = constants.CUISINE_ROOT_NODES
  elif _CONCEPT.value == 'landmarks':
    root_dict = constants.LANDMARK_ROOT_NODES
  elif _CONCEPT.value == 'art':
    root_dict = constants.ART_ROOT_NODES
  else:
    raise ValueError('Invalid concept: %s' % _CONCEPT.value)

  root_cache_nodes = create_root_cache_nodes(root_dict)

  with open(output_file_path, 'w') as fp:
    json.dump(root_cache_nodes, fp, indent=2)


if __name__ == '__main__':
  app.run(main)
