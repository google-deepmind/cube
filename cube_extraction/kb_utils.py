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

"""Utility functions for interacting with Wikidata KB."""

import logging
from typing import Dict, List, Union

import sling

from cube_t2i.cube_extraction import constants


USEFUL_EDGES = constants.PROPERTY_2_ID.values()


def get_kb(kb_path: str) -> sling.Store:
  """Retrieves KB from the given path.

  Args:
    kb_path: path to the local Wikidata KB.

  Returns:
    Retrieved KB in sling.Store format.
  """
  kb = sling.Store()
  kb.load(kb_path)  # load the KB from the sling file
  kb.freeze()  # making the store read-only
  return kb


def get_node_dict(
    node: sling.Frame,
) -> Union[Dict[str, List[str]], Dict[str, str]]:
  """Convert a sling KB node to a dictionary with useful nodes.

  This function converts the node to a list of strings, where each string
  represents a claim about a Wikidata entity, and extracts the values for
  properties defined in 'USEFUL_EDGES'. A claim is a linearized string
  representation of a node info.

  Args:
    node: sling node containing information from Wikidata KB.

  Returns:
    A dictionary where the keys are Wikidata property IDs from `USEFUL_EDGES`
    and the values are lists of strings representing the values.
  """

  node_str = node.data(pretty=True)
  node_claims = node_str.splitlines()

  node_dict = {key: [] for key in USEFUL_EDGES}
  node_dict['id'] = node.id
  for item in node_claims:
    if ':' not in item:  # Skip lines without property values
      continue
    slot, value = item.split(':', 1)
    slot = slot.strip()
    if slot in USEFUL_EDGES:
      node_dict[slot].append(value.strip())
    if slot == 'description':
      node_dict[slot] = value.strip()

  try:
    node_dict['name'] = str(node.name)
  except ValueError as e:
    logging.warning('Error getting name for node with ID %s: %s', node.id, e)

  return node_dict
