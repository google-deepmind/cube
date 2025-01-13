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

r"""Partitions the Wikidata KB into smaller parts for multicore processing.

The script reads the nodes inside Wikidata Knowledge Base (KB) and extracts
useful information from the nodes into Python dictionaries. Later those
dictionaries are saved into JSON files. The script uses the sling framework
 for KB traversal.

Example usage:

  python3 partition_kb.py --partition_dir kb_nodes --num_partitions 200
"""

import json
import os
import pathlib

from absl import app
from absl import flags
import sling  # pylint:disable=unused-import
import tqdm

from cube_t2i.cube_extraction import constants
from cube_t2i.cube_extraction import kb_utils


_PARTITION_DIR = flags.DEFINE_string(
    name="partition_dir",
    default="kb_nodes",
    help="Directory to save partitioned KB nodes",
)

_NUM_PARTITIONS = flags.DEFINE_integer(
    name="num_partitions",
    default=200,
    help="Number of partitions to create",
)


def main(_):
  home_dir = pathlib.Path.home()  # path for cloudtop root directory
  kb = kb_utils.get_kb(f"{home_dir}/{constants.KB_DUMP}")

  if not os.path.exists(_PARTITION_DIR.value):
    os.makedirs(_PARTITION_DIR.value)

  # KB is 15 GB in size, so we split it into smaller (70 MB) parts for
  # multicore processing. It is recommended to choose a partition size that
  # will fit into memory and be easy to process.
  items_per_partition = len(kb) // _NUM_PARTITIONS.value + 1

  kb_nodes = []
  partition_id = 0
  for node in tqdm.tqdm(kb):
    node_dict = kb_utils.get_node_dict(node)
    kb_nodes.append(node_dict)
    if len(kb_nodes) == items_per_partition:
      with open(
          f"kb_nodes/partition_{partition_id}.json", "w", encoding="utf-8"
      ) as f:
        json.dump(kb_nodes, f, indent=2)
      kb_nodes = []
      partition_id += 1

  with open(
      f"kb_nodes/partition_{partition_id}.json", "w", encoding="utf-8"
  ) as f:
    json.dump(kb_nodes, f, indent=2)


if __name__ == "__main__":
  app.run(main)
