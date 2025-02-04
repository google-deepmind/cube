

## Code for [Beyond Aesthetics: Cultural Competence in Text-to-Image Models](https://arxiv.org/abs/2407.06863) published in NeurIPS 2024 (Track on Datasets and Benchmarks)


Current T2I benchmarks primarily focus on faithfulness, aesthetics, and realism of generated images, overlooking the critical dimension of cultural competence. In this work, we introduce a framework to evaluate cultural competence of T2I models along two crucial dimensions: cultural awareness and cultural diversity, and present a scalable approach using a combination of structured knowledge base  (KB) and large language models (LLMs) to build a large dataset of cultural artifacts to enable this evaluation. In particular, we apply this approach to build CUBE (CUltural BEnchmark for Text-to-Image models), a first-of-its-kind benchmark to evaluate cultural competence of T2I models. CUBE covers cultural artifacts associated with 8 countries across different geo-cultural regions and along 3 concepts: cuisine, landmarks, and art. We also introduce cultural diversity as a novel T2I evaluation component, leveraging quality-weighted Vendi score. In this repository, we release the 1) code for CUBE extraction from WikiData, 2) a notebook [![Open In
Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-deepmind/cube/blob/master/cultural_diversity.ipynb) with the  implementation of the cultural diversity evaluation aspect for T2I and 3) CUBE dataset containing CUBE CSpace and CUBE-1K prompts.

## CUBE Extraction

### Setup

#### Fetching latest KB dump (redoing this will refresh latest Wikidata dump)

```
python3.8 -m venv wikidata
source wikidata/bin/activate
pip3 install https://ringgaard.com/data/dist/sling-3.0.0-py3-none-linux_x86_64.whl
pip install urllib3
pip install absl-py
pip install pandas
pip install requests
sling fetch --dataset kb,mapping
```



### Usage


Move to CUBE directory

```
cd cube_extraction
```

Partition KB into smaller parts for easy multiprocessing (this step needs to be
done only once)

```
python3 partition_kb.py
```

Bash execute permissions

```
chmod +x run_kb_extraction.sh
```

#### Extract cultural artifacts

```
sh run_kb_extraction.sh

# Example usage with arguments:
#     sh run_kb_extraction.sh
#     Enter directory of KB partitions: /path/to/kb_nodes/  (Local cloudtop path)
#     Enter concept (e.g., cuisine, landmarks, art): cuisine
#     Enter number of hops: 3
#     Enter desired output directory: /path/to/output/  (Local cloudtop path)
#     Enter desired output file name: cuisine_artifacts.json
```

## Cultural Diversity

###  Setup

```
conda create -n cd python=3.10 && conda activate cd
pip install -r requirements.txt
```

### Usage

Refer to the cultural_diversity.ipynb [![Open In
Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/google-deepmind/cube/blob/master/cultural_diversity.ipynb) for a sample usage of the evaluation metric.


## Dataset

CUBE dataset contains cultural artifacts across 8 countries (Brazil, France, India, Italy, Japan, Nigeria, Turkey, and USA) and 3 domains (cuisine, landmarks, art). 

The dataset is divided into two parts:
1. **CUBE-CSpace**: a collection of 300k cultural artifacts, intended to be used as grounding for diversity evaluation. For example,
* Japanese Cuisine: Ramen, Soba, Sushi, Katsu sandwich
* France Landmarks: Eiffel Tower, Mont Saint-Michel, Palace of Versailles
* Indian Art/Clothing: Kurta, Lehanga Choli, Dhoti, Patola Saree

2. **CUBE-1K**: a curated set of 1000 prompts constructed from cultural artifacts in CUBE-CSpace, that enable evaluation of cultural awareness. For example,
* Cuisine: A high resolution image of sushi from Japanese cuisine.
* Landmarks: A panoramic view of Eiffel Tower in France.
* Art: Clothing Image of a person in kurta from India.


## Citation

If you find the code or datset useful, please cite our paper:

```
@misc{kannen2024aestheticsculturalcompetencetexttoimage,
      title={Beyond Aesthetics: Cultural Competence in Text-to-Image Models},
      author={Nithish Kannen and Arif Ahmad and Marco Andreetto and Vinodkumar Prabhakaran and Utsav Prabhu and Adji Bousso Dieng and Pushpak Bhattacharyya and Shachi Dave},
      year={2024},
      eprint={2407.06863},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2407.06863},
}
```

## License

Copyright 2025 DeepMind Technologies Limited

### Software


All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

### Dataset

We distribute CUBE dataset under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en) license 

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.

## Contact

Please direct your questions to nitkan@google.com / shachi@google.com
