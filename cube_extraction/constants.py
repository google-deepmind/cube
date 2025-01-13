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

"""Constants used in CUBE extraction.

Includes WikiData root and edge nodes for the concepts considered.

Steps to add a new concept or country to CUBE:
1) Identify root nodes (such as {'food': 'Q2095'} ) and add them to this file
in a dictionary format.
2) If there are any concept specific edges or properties, identify them and
add them to the PROPERTY_2_ID dictionary.
3) If there are any new countries to add, identify them and add them to
the ID_2_COUNTRY dictionary.
4) Add a new 'if' statement in create_root_cache.py to create the root cache
for the new concept.
Wikidata IDs can be found here: https://www.wikidata.org/wiki/Wikidata:Main_Page
"""

# Add new concept root nodes here.

CUISINE_ROOT_NODES = {
    'Q2095': 'food',
    'Q746549': 'dish',
    'Q19861951': 'type of food or dish',
}


LANDMARK_ROOT_NODES = {
    'Q210272': 'Cultural Heritage',
    'Q41176': 'Building',
    'Q33506': 'Museum',
    'Q16560': 'Palace',
    'Q839954': 'archaeological site',
    'Q22698': 'park',
    'Q1107656': 'garden',
    'Q24398318': 'religious building',
    'Q4989906': 'monument',
    'Q2416723': 'theme park',
    'Q842858': 'National museum',
    'Q3152824': 'cultural institution',
    'Q1060829': 'concert hall',
    'Q153562': 'opera house',
    'Q1007870': 'art gallery',
    'Q3395377': 'ancient monument',
    'Q109607': 'ruins',
    'Q207694': 'art museum',
    'Q15243209': 'historic district',
    'Q9259': 'World Heritage Site',
    'Q7075': 'Library',
    'Q11635': 'theatre',
    'Q39614': 'cemetery',
    'Q16999091': 'landmarks',
    'Q1785071': 'fort',
    'Q143912': 'triumphal arch',
    'Q1329623': 'cultural center ',
    'Q28737012': 'museum of culture',
    'Q811979': 'architectural structure',
    'Q622425': 'nightclub',
    'Q12271': 'architecture',
    'Q11303': 'skyscraper',
    'Q12280': 'bridge',
    'Q39715': 'lighthouse',
    'Q23413': 'castle',
    'Q483110': 'stadium',
    'Q1200957': 'tourist destination',
    'Q167346': 'botanical garden',
    'Q2281788': 'public aquarium',
}


ART_ROOT_NODES = {
    'Q11460': 'clothing',
    'Q9053464': 'costume',
    'Q3172759': 'traditional costume',
    'Q107357104': 'type of dance',
    'Q45971958': 'performing art genre',
    'Q17399019': 'style of painting',
    'Q1153484': 'folk art',
}

# Edges of WikiData considered for the CUBE extraction process.
# New edges may be introduced for newer concepts.
# Refer here for IDs: https://www.wikidata.org/wiki/Property:P361.
PROPERTY_2_ID = {
    'instance of': 'P31',
    'subclass of': 'P279',
    'country of origin': 'P495',
    'country': 'P17',
    'cuisine': 'P2012',
    'part of': 'P361',
}
# Current list of countries considered for CUBE extraction.
# New countries can be added to the dictionary as CUBE is scaled.
# IDs can be found here: https://www.wikidata.org/wiki/Wikidata:Main_Page
ID_2_COUNTRY = {
    'Q155': 'Brazil',
    'Q668': 'India',
    'Q17': 'Japan',
    'Q1033': 'Nigeria',
    'Q45': 'Portugal',
    'Q43': 'Turkey',
    'Q30': 'United States',
    'Q38': 'Italy',
    'Q408': 'Australia',
    'Q142': 'France',
}

SLING_PATH = 'Downloads/data/e/wiki/en/mapping.sling'
KB_DUMP = 'Downloads/data/e/kb/kb.sling'
WIKI = '/wp/en/'
WIKI_QID = '/w/item/qid'

# This is a conversion from country to adjective so that it can be used in a
# prompt. For example, 'Indian cuisine' is more natural than 'India cuisine'
country_to_adjective = {
    'Brazil': 'Brazilian',
    'India': 'Indian',
    'Japan': 'Japanese',
    'Nigeria': 'Nigerian',
    'Portugal': 'Portuguese',
    'Turkey': 'Turkish',
    'United States': 'American',
    'Italy': 'Italian',
    'Australia': 'Australian',
    'France': 'French',
}

# Refer https://developers.google.com/custom-search/docs/json_api_reference#country-codes # pylint: disable=line-too-long
country_to_search_api_code = {
    'Brazil': 'br',
    'India': 'in',
    'Japan': 'jp',
    'Nigeria': 'ng',
    'Portugal': 'pt',
    'Turkey': 'tr',
    'United States': 'us',
    'Italy': 'it',
    'Australia': 'au',
    'France': 'fr',
}
