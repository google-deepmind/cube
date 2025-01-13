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

r"""Merges Wikidata nodes from multiple hop files and groups by country.

This script takes multiple JSON files, each representing Wikidata nodes
reached after a certain number of hops from a root node. It merges these nodes,
extracts nodes associated with countries of interest, and groups them by
country. The final output is saved as a JSON file.

Example Usage:
  python3 merge_artifacts.py \
      --input_filepaths=outs/1_hop_out_nodes.json,outs/2_hop_out_nodes.json \
      --output_filepath=outs/cultural_artifacts.json

"""

import json
import logging
import os
import pathlib
from typing import Dict

from absl import app
from absl import flags
import sling
import tqdm

from cube_t2i.cube_extraction import constants


_INPUT_FILEPATHS = flags.DEFINE_list(
    name='input_filepaths',
    default=None,
    help='List of paths to input hop files.',
    required=True,
)
_OUTPUT_FILEPATH = flags.DEFINE_string(
    name='output_filepath',
    default=None,
    help='Path to the output JSON file.',
    required=True,
)


def load_qid_mapping(sling_wiki_mapping_file: str) -> Dict[str, str]:
  """Load a mapping from Wikidata QIDs to Wikipedia page titles.

  Args:
    sling_wiki_mapping_file: Path to the Sling file containing the mapping.

  Returns:
    A dictionary where keys are Wikidata QIDs and values are corresponding
    Wikipedia page titles.
    For example, {'Q920940': 'dosa'}
  """
  commons = sling.Store()
  commons.load(sling_wiki_mapping_file)
  commons.freeze()
  qid_mapping = {}
  for f in commons:
    if constants.WIKI_QID not in f:
      continue
    try:
      pg = (
          f.id[len(constants.WIKI) :]
          if f.id.startswith(constants.WIKI)
          else f.id
      )
      qid_mapping[f[constants.WIKI_QID].id] = pg
    except UnicodeDecodeError:
      logging.warning('UnicodeDecodeError while processing frame: %s', f)

  logging.info('Extracted %d mappings', len(qid_mapping))
  return qid_mapping


def main(_):
  """Merge Wikidata nodes from input files and group them by country."""

  home = pathlib.Path.home()  # path for cloudtop root directory
  logger = logging.getLogger()
  logger.setLevel(logging.ERROR)

  # Load the QID to Wikipedia title mapping.
  qid_mapping = load_qid_mapping(f'{home}/{constants.SLING_PATH}')

  # Merge nodes from all input files.
  all_items = []
  for file_path in _INPUT_FILEPATHS.value:
    # Check if the file exists
    if not os.path.exists(file_path):
      logging.error('Input file not found: %s. Skipping...', file_path)
      continue  # Skip to the next file

    with open(file_path, 'r') as f:
      all_items.extend(json.load(f))

  # Artifact nodes grouped by country
  country_ids = constants.ID_2_COUNTRY.keys()
  cultural_artifacts = {key: [] for key in constants.ID_2_COUNTRY.values()}

  # Group nodes by country and add Wikipedia titles.
  for item in tqdm.tqdm(all_items):
    item_countries = set()  # Set of country IDs associated with the item.
    item_countries.update(
        item.get('P495', [])
    )  # 'P495' represents 'country of origin'.
    item_countries.update(item.get('P17', []))  # 'P17' represents 'country'.
    item['title'] = qid_mapping.get(item['id'], 'Title Not Found')
    # Note that a single item may have multiple countries associated with it.
    # In such cases, the item is added to the set of artifacts for each country.
    # For example, pasta (Q178) has a 'country of origin' as both
    # Italy and China. Refer here: https://www.wikidata.org/wiki/Q178

    for country_id in item_countries:
      if country_id in country_ids:
        country_name = constants.ID_2_COUNTRY[country_id]
        if item not in cultural_artifacts[country_name]:
          cultural_artifacts[country_name].append(item)

  # Save the grouped nodes to the output JSON file.

  with open(_OUTPUT_FILEPATH.value, 'w') as fp:
    json.dump(cultural_artifacts, fp, indent=2)


if __name__ == '__main__':
  app.run(main)
