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

from cube_t2i.cube_extraction import kb_utils
from cube_t2i.cube_extraction import partition_kb


class PartitionKbTest(unittest.TestCase):
  """Test class for partition_kb.py."""

  def setUp(self):
    super().setUp()
    self.test_dir = os.path.dirname(__file__)
    self.partition_dir = os.path.join(self.test_dir, "kb_partitions")
    flags.FLAGS([
        "test_program",
        "--partition_dir",
        self.partition_dir,
        "--num_partitions",
        "2",
    ])

  def tearDown(self):
    super().tearDown()
    if os.path.exists(self.partition_dir):
      for file in os.listdir(self.partition_dir):
        os.remove(os.path.join(self.partition_dir, file))
      os.rmdir(self.partition_dir)

  @flagsaver.flagsaver
  def test_main_creates_partitions(self, mock_get_kb):
    """Test the main function."""
    mock_kb = unittest.mock.MagicMock()
    mock_kb.__len__ = unittest.mock.MagicMock(return_value=10)
    mock_kb.__iter__ = unittest.mock.MagicMock(
        return_value=iter([{"id": f"Q{i}"} for i in range(10)])
    )
    mock_get_kb.return_value = mock_kb

    # Mock get_node_dict
    with unittest.mock.patch.object(
        kb_utils, "get_node_dict", return_value={"id": "Q1", "name": "Node1"}
    ):
      partition_kb.main([])

    self.assertTrue(os.path.exists(self.partition_dir))
    partition_files = os.listdir(self.partition_dir)
    self.assertEqual(len(partition_files), 3)  # 2 partitions + 1 leftover

    for file in partition_files:
      with open(os.path.join(self.partition_dir, file), "r") as f:
        data = json.load(f)
        self.assertIsInstance(data, list)

  @flagsaver.flagsaver
  def test_main_handles_empty_kb(self):
    """Test the main function with an empty KB."""
    mock_get_kb = unittest.mock.MagicMock()
    mock_get_kb.return_value = []
      partition_kb.main([])

    self.assertTrue(os.path.exists(self.partition_dir))
    partition_files = os.listdir(self.partition_dir)
    self.assertEqual(len(partition_files), 1)  # Only the leftover partition


if __name__ == "__main__":
  app.run(lambda argv: unittest.main(argv=argv))
