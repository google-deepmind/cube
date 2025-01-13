#!/bin/bash
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


# Runs the KB traversal on Wikidata to extract cultural artifacts using SLING

# Example Usage:
#     run_kb_extraction.sh
#     Enter concept (e.g., cuisine, landmarks, art): cuisine
#     Enter number of hops: 3
#     Enter desired output directory: /path/to/output/
#     Enter desired output file name: cuisine_artifacts.json

# Get concept, number of hops, output directory, and output file name from user
IFS= read -rp "Enter directory of KB partitions: " PARTITION_DIR
IFS= read -rp "Enter concept (e.g., cuisine, landmarks, art): " CONCEPT
IFS= read -rp "Enter number of hops: " NUM_HOPS
IFS= read -rp "Enter desired output directory: " OUTPUT_DIR
IFS= read -rp "Enter desired output file name: " OUTPUT_FILE

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create a temporary directory for intermediate cache files
TEMP_DIR=$(mktemp -d -p "$OUTPUT_DIR" "temp_cache.XXXXXXXXXX")

# Create the root cache
echo "Creating root cache for concept: $CONCEPT"
python3 create_root_cache.py \
  --concept="$CONCEPT" \
  --root_cache_file_dir="$TEMP_DIR"

# Loop for the specified number of hops
for (( hop=1; hop<=$NUM_HOPS; hop++ )); do
  echo "Running hop $hop..."

  # Set CURRENT_PREV_CACHE to the root cache for the first hop
  if (( $hop == 1 )); then
    CURRENT_PREV_CACHE="$TEMP_DIR/${CONCEPT}_root_nodes.json"
  else
    CURRENT_PREV_CACHE="$TEMP_DIR/$((hop-1))_hop_next_cache.json"
  fi

  CURRENT_NEXT_CACHE="$TEMP_DIR/${hop}_hop_next_cache.json"
  # Execute a single hop of the traversal
  python3 traverse_one_hop_kb.py \
    --prev_cache_path="$CURRENT_PREV_CACHE" \
    --next_cache_path="$CURRENT_NEXT_CACHE" \
    --current_hop="$hop" \
    --output_dir="$TEMP_DIR" \
    --json_filename="out_nodes.json" \
    --partition_dir="$PARTITION_DIR"
done

# Merge the results from all hops
echo "Merging results..."

INPUT_FILES=()
for (( hop=1; hop<=$NUM_HOPS; hop++ )); do
  INPUT_FILES+=("$TEMP_DIR/${hop}_hop_out_nodes.json")
done

python3 merge_artifacts.py \
  --input_filepaths "${INPUT_FILES[@]}" \
  --output_filepath "$OUTPUT_DIR/$OUTPUT_FILE"

# Remove the temporary directory and its contents
rm -rf "$TEMP_DIR"

echo "Traversal and merging complete! Results saved to: $OUTPUT_DIR/$OUTPUT_FILE"
