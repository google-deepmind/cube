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

r"""Traverses the WikiData from the loaded root nodes by 1 hop.

The script reads the root cache file or the prev cache file and traverses the
Wikidata knowledge base by 1 hop using the algorithm described in CUBE paper:
https://arxiv.org/abs/2407.06863. The script uses the sling framework for KB traversal.

Example usage:

  python3 traverse_one_hop_kb.py --prev_cache_path temp/cuisine_root_nodes.json \
      --next_cache_path temp/next_cache.json \
      --current_hop 1 \
      --output_dir outs \
      --json_filename out_nodes.json
"""

import itertools
import json
import logging
import multiprocessing
import os
from typing import Dict, List
from absl import app
from absl import flags
import sling  # pylint:disable=unused-import
import tqdm


from cube_t2i.cube_extraction import constants

_PREV_CACHE_PATH = flags.DEFINE_string(
    name='prev_cache_path',
    default=None,
    help='Path to the previous cache file.',
    required=True,
)
_NEXT_CACHE_PATH = flags.DEFINE_string(
    name='next_cache_path',
    default=None,
    help='Path to the next cache file.',
    required=True,
)
_CURRENT_HOP = flags.DEFINE_string('current_hop', '1', 'current hop')

_OUTPUT_DIR = flags.DEFINE_string(
    name='output_dir',
    default=None,
    help='Directory to save the output file.',
    required=True,
)
_JSON_FILENAME = flags.DEFINE_string(
    name='json_filename',
    default=None,
    help='Filename of the JSON file to store the outputs',
    required=True,
)
_PARTITION_DIR = flags.DEFINE_string(
    name='partition_dir',
    default=None,
    help='Directory containing KB partitions.',
    required=True,
)
_NUM_PROCESSES = flags.DEFINE_integer(
    name='num_processes',
    default=64,
    help='Number of processes to use for multicore processing.',
)
USEFUL_EDGES = constants.PROPERTY_2_ID.values()


def to_clean_dict(node_claims: List[str]) -> Dict[str, List[str]]:
  """Convert a list of KB node items as strings, to a dictionary with useful nodes.

  This function takes a list of strings, where each string represents a claim
  about a Wikidata entity, and extracts the values for properties defined in
  'USEFUL_EDGES'. A claim is a linearized string representation of a node info.

  Example of a claim:
  ["P279: Q746549", "P495: Q172579", "P31: Q5" ]

  Args:
    node_claims: List of strings containing node information extracted from the
      Wikidata KB.

  Returns:
    A dictionary where the keys are Wikidata property IDs from `USEFUL_EDGES`
    and the values are lists of strings representing the values.
  """

  node_dict = {key: [] for key in USEFUL_EDGES}
  for item in node_claims:
    if ':' not in item:  # Skip lines without property values
      continue
    slot, value = item.split(':', 1)
    slot = slot.strip()
    if slot in USEFUL_EDGES:
      node_dict[slot].append(value.strip())

  return node_dict


def _is_connected_to_root(
    node_dict: Dict[str, str], root_id: str, property_name: str
) -> bool:
  """Checks if the node is connected to the root node via the given property.

  Args:
    node_dict: Dictionary containing node information.
    root_id: Wikidata ID of the root node.
    property_name: Name of the property to check for.

  Returns:
    Whether the node is connected to the root via the given property.
  """
  return bool(
      root_id in node_dict.get(constants.PROPERTY_2_ID[property_name], [])
  )


def _is_connected_by(node_dict: Dict[str, str], property_name: str) -> bool:
  """Checks if the node is connected to any node via the given property.

  Args:
    node_dict: Dictionary containing node information.
    property_name: Name of the property to check for.

  Returns:
    Whether the node is connected to any node via the given property.
  """
  return bool(node_dict.get(constants.PROPERTY_2_ID[property_name], []))


def _is_instance_of_root(node_dict: Dict[str, str], root_id: str) -> bool:
  """Checks if the node is connected to the root via 'instance of' property."""
  return _is_connected_to_root(node_dict, root_id, 'instance of')


def _is_subclass_of_root(node_dict: Dict[str, str], root_id: str) -> bool:
  """Checks if the node is connected to the root via 'subclass of' property."""
  return _is_connected_to_root(node_dict, root_id, 'subclass of')


def _has_country_property(node_dict: Dict[str, str]) -> bool:
  """Checks if the node has a country association in WikiData."""

  return _is_connected_by(node_dict, 'country of origin') or _is_connected_by(
      node_dict, 'country'
  )


def _one_partition_traversal(
    partition_path: str,
    prev_cache_ids: List[str],
    prev_cache_id_to_root: Dict[str, str],
) -> Dict[str, List[Dict[str, str]]]:
  """Traverses one partition of the Wikidata KB.

  Args:
    partition_path: Path to the KB partition to traverse.
    prev_cache_ids: List of Wikidata IDs from the previous cache.
    prev_cache_id_to_root: Dictionary mapping Wikidata IDs from the previous
      cache to their root nodes.

  Returns:
    A dictionary containing the results (output nodes and next cache nodes)
    of the traversal.
  """
  full_partition_path = os.path.join(_PARTITION_DIR.value, partition_path)
  with open(full_partition_path, 'r', encoding='utf-8') as partition_file:
    kb_nodes = json.load(partition_file)

  partition_result = {'output_nodes': [], 'next_cache_nodes': []}
  for node_dict in tqdm.tqdm(kb_nodes):
    # Look for nodes along the 'subclass of' and 'instance of' edges.
    for root_id in prev_cache_ids:
      if _is_subclass_of_root(node_dict, root_id) or _is_instance_of_root(
          node_dict, root_id
      ):

        node_dict['root'] = prev_cache_id_to_root[root_id]
        if _has_country_property(node_dict):  # if a node has country property
          partition_result['output_nodes'].append(node_dict)
        else:
          partition_result['next_cache_nodes'].append(
              node_dict
          )  # add to next cache
  return partition_result


def main(_):
  # Access cache file paths from flags

  logger = logging.getLogger()
  logger.setLevel(logging.ERROR)

  prev_cache_path = _PREV_CACHE_PATH.value
  next_cache_path = _NEXT_CACHE_PATH.value
  output_filename = f'{_CURRENT_HOP.value}_hop_{_JSON_FILENAME.value}'
  output_path = os.path.join(_OUTPUT_DIR.value, output_filename)

  if not os.path.exists(_OUTPUT_DIR.value):
    os.makedirs(_OUTPUT_DIR.value)

  output_nodes = []
  next_cache_nodes = []

  with open(prev_cache_path, 'r', encoding='utf-8') as prev_cache_file:
    prev_cache_nodes = json.load(prev_cache_file)
  prev_cache_ids = []

  prev_cache_id_to_root = {}
  for cache_node in prev_cache_nodes:
    prev_cache_ids.append(cache_node['id'])
    prev_cache_id_to_root[cache_node['id']] = cache_node['root']

  kb_partition_dir = os.listdir(_PARTITION_DIR.value)
  with multiprocessing.Pool(_NUM_PROCESSES.value) as pool:
    partition_results = list(
        pool.starmap(
            _one_partition_traversal,
            zip(
                kb_partition_dir,
                itertools.repeat(prev_cache_ids),
                itertools.repeat(prev_cache_id_to_root),
            ),
        )
    )
    pool.close()
    pool.join()

  for partition_result in partition_results:
    output_nodes.extend(partition_result['output_nodes'])
    next_cache_nodes.extend(partition_result['next_cache_nodes'])

  with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_nodes, f, indent=2)

  with open(next_cache_path, 'w', encoding='utf-8') as f:
    json.dump(next_cache_nodes, f, indent=2)


if __name__ == '__main__':
  app.run(main)
