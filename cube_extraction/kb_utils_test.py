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

import unittest
import sling
from cube_t2i.cube_extraction import kb_utils


class KbUtilsTest(unittest.TestCase):
  """Test class for kb_utils.py."""

  @unittest.mock.patch("sling.Store")
  def test_get_kb(self, mock_store):
    """Test the get_kb function."""

    kb_path = "dummy_path"

    # Mock the behavior of sling.Store
    mock_store_instance = unittest.mock.MagicMock()
    mock_store.return_value = mock_store_instance

    result = kb_utils.get_kb(kb_path)

    mock_store.assert_called_once()
    mock_store_instance.load.assert_called_once_with(kb_path)
    mock_store_instance.freeze.assert_called_once()
    self.assertEqual(result, mock_store_instance)

  def test_get_node_dict(self):
    """Test the get_node_dict function."""

    mock_node = unittest.mock.MagicMock(spec=sling.Frame)
    mock_node.id = "Q123"
    mock_node.name = "FakeName"
    mock_node.data.return_value = (
        "{\n  P31: Q456\n  P279: Q789\n  description: FakeDescription\n}\n"
    )

    result = kb_utils.get_node_dict(mock_node)

    self.assertEqual(result["id"], "Q123")
    self.assertEqual(result["name"], "FakeName")
    self.assertEqual(result["P31"], ["Q456"])
    self.assertEqual(result["P279"], ["Q789"])
    self.assertEqual(result["description"], "FakeDescription")


if __name__ == "__main__":
  unittest.main()
