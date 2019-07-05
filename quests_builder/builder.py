"""
Author:  pmauldin
Email:   petermauldin1@gmail.com

Copyright (c) 2019, PH01L

###############################################################################
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
"""

import os
import json
from pathlib import Path

import config
from quests_builder import quest_builder

if __name__ == "__main__":
    # Delete old log file
    if os.path.exists("builder.log"):
        os.remove("builder.log")

    # Load the wiki text file
    wiki_text_file_path = Path(config.EXTRACTION_WIKI_PATH / "extract_page_text_quests.json")
    with open(wiki_text_file_path) as wiki_text_file:
        quests_wiki_text = json.load(wiki_text_file)

    # Filter out non-quest entities
    name_exclusion_list = ["Quests/", "Miniquests", "/Quick guide", "Category:", "User:", "Quest series"]

    # Start processing items
    for quest_name, wiki_text in quests_wiki_text.items():
        if any(exl.lower() in quest_name.lower() for exl in name_exclusion_list):
            continue

        # Initialize the BuildQuest class
        builder = quest_builder.BuildQuest(quest_name, wiki_text)

        # Start the build quest population method
        quest_definition = builder.populate()

        output_dir = Path(config.DOCS_PATH / "quests-json" / "")

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Actually output a JSON file, comment out for testing
        quest_definition.export_json(True, output_dir)
