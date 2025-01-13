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

import json
import os
import unittest

from absl import app
from absl import flags
from absl.testing import flagsaver

from cube_t2i.cube_extraction import merge_artifacts


class MergeArtifactsTest(unittest.TestCase):
  """Test class for merge_artifacts.py."""

  def setUp(self):
    super().setUp()
    self.test_dir = os.path.dirname(__file__)
    self.output_filepath = os.path.join(self.test_dir, "merged_artifacts.json")

    # Create dummy input files
    self.input_filepaths = []
    for i in range(2):
      filepath = os.path.join(self.test_dir, f"input_file_{i}.json")
      with open(filepath, "w") as f:
        json.dump([{"id": f"Q{i}", "P495": ["Q155"]}], f)
      self.input_filepaths.append(filepath)

    flags.FLAGS([
        "test_program",
        "--input_filepaths",
        ",".join(self.input_filepaths),
        "--output_filepath",
        self.output_filepath,
    ])

  def tearDown(self):
    """Clean up the test directory after each test."""
    super().tearDown()
    for filepath in self.input_filepaths:
      if os.path.exists(filepath):
        os.remove(filepath)
    if os.path.exists(self.output_filepath):
      os.remove(self.output_filepath)

  @flagsaver.flagsaver
  def test_main(self, mock_load_qid_mapping):
    """Test the main function."""
    mock_load_qid_mapping.return_value = {"Q0": "Title0", "Q1": "Title1"}

    merge_artifacts.main([])

    self.assertTrue(os.path.exists(self.output_filepath))
    with open(self.output_filepath, "r") as f:
      data = json.load(f)
      self.assertIn("Brazil", data)
      self.assertEqual(len(data["Brazil"]), 2)
      self.assertEqual(data["Brazil"][0]["title"], "Title0")


if __name__ == "__main__":
  app.run(lambda argv: unittest.main(argv=argv))
