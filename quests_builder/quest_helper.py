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

import re
from typing import List, Dict

import mwparserfromhell

# Map to convert integer difficulties from the OSRS Wiki to a human readable string
from common_builder_tools import builder_utils

DIFFICULTY_CONVERSION = {
    "1": "Novice",
    "2": "Intermediate",
    "3": "Experienced"
}

RFD_QUESTS = [
    "Freeing the Mountain Dwarf",
    "Freeing the Goblin generals",
    "Freeing Pirate Pete",
    "Freeing the Lumbridge Guide",
    "Freeing Evil Dave",
    "Freeing King Awowogei",
    "Freeing Sir Amik Varze"
    "Freeing Skrach Uglogwee",
    "Defeating the Culinaromancer"
]


def clean_display_string(string: str) -> str:
    """Remove common markup from wiki text"""
    return re.sub('[*[\]]', '', string).strip()


def get_url_string(name: str) -> str:
    """Ready the given string for use in a URL"""
    return clean_display_string(name) \
        .replace(" ", "_") \
        .replace("'", "%27") \
        .replace("&", "%26") \
        .replace("+", "%2B")


def extract_sanitized_value(template: mwparserfromhell.nodes.template.Template, key: str) -> str:
    """Wrapper for extracting a value from a template and sanitizing it"""
    value = builder_utils.extract_template_value(template, key)

    if not value:
        return None

    return clean_display_string(value)


def get_template_params(template: mwparserfromhell.nodes.template.Template) -> List[str]:
    """Get the list of keys contained in the given template"""
    return [param.name.strip() for param in template.params]


def get_difficulty(template: mwparserfromhell.nodes.template.Template) -> str:
    """Extract the difficulty of a quest from the given template"""
    difficulty = builder_utils.extract_template_value(template, "difficulty")

    if not difficulty:
        return "Unknown Difficulty"

    if difficulty.isdigit():
        if difficulty in DIFFICULTY_CONVERSION:
            # Some quests have their difficulty set as an integer that maps to a readable string
            # We have to convert this value here
            return DIFFICULTY_CONVERSION[difficulty]
        else:
            return f"Unable to convert difficulty {difficulty}"

    return difficulty


def get_quest_length(template: mwparserfromhell.nodes.template.Template) -> str:
    """Extract the length of a quest from the given template"""
    length = builder_utils.extract_template_value(template, "length")

    if not length:
        return "Unknown Length"

    if "-" in length:
        length = length[:length.index('-')].strip()

    return clean_display_string(length)


def get_image(template: mwparserfromhell.nodes.template.Template) -> str:
    """Extract the url to a quest's image on the OSRS Wiki from the given template"""
    image = builder_utils.extract_template_value(template, "image")

    if not image:
        return None

    image = get_url_string(image)

    if "|" in image:
        image = image.split("|")[0]

    return builder_utils.construct_wiki_url(image)


def get_skill_requirement(template: mwparserfromhell.nodes.template.Template, raw_text: str) -> Dict:
    """Extract a skill requirement for a quest from the given template"""
    skill_req_params = template.params

    skill_name = str(skill_req_params[0])

    if len(skill_req_params) < 2:
        # Some skill requirements are malformed
        # We have to handle several special cases here
        # E.g. Level 30 {{SkillReq|Mining}} vs {{SkillReq|Mining}} vs {{SkillReq|Mining|30}}
        raw_text = raw_text.replace("*", "")
        start_idx = len("Level ") if "Level " in raw_text and raw_text.index("Level ") == 0 else 0
        skill_level = raw_text[start_idx:raw_text.index("{")].strip()
    else:
        # Some skill requirements are written as a range, such as "43+ Prayer"
        skill_level = str(skill_req_params[1].replace("+", ""))

    if not skill_level.isdigit():
        return None

    return {
        "name": skill_name,
        "level": int(skill_level)
    }


def clean_quest_name(quest_name: str) -> str:
    """Helper method to clean up quest names and handle special cases"""
    if "[[" in quest_name and "level" not in quest_name:
        quest_name = quest_name[quest_name.index("[["):quest_name.index("]]")]

    quest_name = clean_display_string(quest_name)

    if "#" in quest_name:
        quest_name = quest_name.split("#")[1]

    quest_name = quest_name.split("|")[0].strip()

    for rfd_quest in RFD_QUESTS:
        if quest_name.lower() in rfd_quest.lower():
            return f"Recipe for Disaster/{rfd_quest}"

    return quest_name
