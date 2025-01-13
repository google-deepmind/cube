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

from cube_t2i.cube_extraction import create_root_cache


class CreateRootCacheTest(unittest.TestCase):
  """Test class for create_root_cache.py."""

  def setUp(self):
    super().setUp()
    self.test_dir = os.path.dirname(__file__)
    self.root_cache_dir = os.path.join(self.test_dir, "test_temp")
    flags.FLAGS([
        "test_program",  # Add a dummy program name here
        "--root_cache_file_dir",
        self.root_cache_dir,
        "--concept",
        "cuisine",
    ])

  def tearDown(self):
    super().tearDown()
    if os.path.exists(self.root_cache_dir):
      for file in os.listdir(self.root_cache_dir):
        os.remove(os.path.join(self.root_cache_dir, file))
      os.rmdir(self.root_cache_dir)

  @flagsaver.flagsaver
  def test_create_root_cache_cuisine(self):
    """Test the create_root_cache function for cuisine."""
    flags.FLAGS.concept = "cuisine"
    flags.FLAGS.root_cache_file_dir = self.root_cache_dir
    create_root_cache.main([])

    expected_file_path = os.path.join(
        self.root_cache_dir, "cuisine_root_nodes.json"
    )
    self.assertTrue(os.path.exists(expected_file_path))

    with open(expected_file_path, "r") as f:
      data = json.load(f)
      self.assertIsInstance(data, list)
      self.assertTrue(all(isinstance(item, dict) for item in data))
      # Check that the data matches the constants
      self.assertEqual(
          data,
          [
              {"id": "Q2095", "name": "food", "root": "food"},
              {"id": "Q746549", "name": "dish", "root": "dish"},
              {
                  "id": "Q19861951",
                  "name": "type of food or dish",
                  "root": "type of food or dish",
              },
          ],
      )

  @flagsaver.flagsaver
  def test_create_root_cache_invalid_concept(self):
    """Test handling of invalid concept."""
    flags.FLAGS.concept = "invalid_concept"
    flags.FLAGS.root_cache_file_dir = self.root_cache_dir

    with self.assertRaises(ValueError):
      create_root_cache.main([])

  def test_create_root_cache_nodes(self):
    """Test the create_root_cache_nodes function."""
    root_dict = {"Q1": "Test1", "Q2": "Test2"}
    result = create_root_cache.create_root_cache_nodes(root_dict)
    expected_result = [
        {"id": "Q1", "name": "Test1", "root": "Test1"},
        {"id": "Q2", "name": "Test2", "root": "Test2"},
    ]
    self.assertEqual(result, expected_result)


if __name__ == "__main__":
  app.run(lambda argv: unittest.main(argv=argv))
