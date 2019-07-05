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

import json
import logging
import re

import mwparserfromhell

from osrsbox.quests_api.quest_definition import QuestDefinition
from common_builder_tools import builder_utils
from quests_builder import quest_helper


class BuildQuest:
    def __init__(self, quest_name, wiki_text, quest_titles):
        self.quest_name = quest_name
        self.wiki_text = wiki_text  # Dict of raw wiki text from OSRS Wiki
        self.quest_titles = quest_titles  # List of all quest titles

        # For this quest, create dictionary for property storage
        self.quest_dict = dict()

        # Setup logging
        logging.basicConfig(filename="builder.log",
                            filemode='a',
                            level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def populate(self):
        """The primary entry and quest object population function"""
        # Start section in logger
        self.logger.debug("============================================ START")
        self.logger.debug(f"Quest name: {self.quest_name}")

        # Set initial values not dependent on template parsing
        quest_id = quest_helper.get_url_string(self.quest_name.replace("/", "-"))
        self.quest_dict["id"] = quest_id
        self.quest_dict["name"] = self.quest_name
        self.quest_dict["wiki_url"] = builder_utils.construct_wiki_url(quest_id)

        # Parse the wiki templates
        wiki_code = mwparserfromhell.parse(self.wiki_text)
        templates = wiki_code.filter_templates()

        for template in templates:
            template_name = template.name.strip().lower()

            if "infobox quest" in template_name:
                self.logger.debug("Parsing Infobox...")
                self.parse_infobox(template)

            if "quest details" in template_name:
                self.logger.debug("Parsing Quest Details...")
                self.parse_details(template)

            if "quick guide" in template_name:
                self.quest_dict["wiki_quick_guide_url"] = builder_utils.construct_wiki_url(f"{quest_id}/Quick_guide")

            if "miniquests" in template_name:
                self.quest_dict["type"] = "Miniquest"

            if "minigames" in template_name:
                self.quest_dict["type"] = "Minigame"

            # TODO Required Items
            # TODO Rewards
            # TODO Enemies to defeat
            # TODO Required for completing
            # TODO Start Point

        # Here for debugging purposes, prints the raw properties dict
        self.logger.debug(json.dumps(self.quest_dict, indent=4))

        # Populate the dataclass
        quest_definition = QuestDefinition.from_json(self.quest_dict)

        self.logger.debug(json.dumps(quest_definition.construct_json(), indent=4, ensure_ascii=False))

        return quest_definition

    def parse_infobox(self, template):
        """Parse an Infobox template."""

        # Determine if the quest is members only or not
        members = template.get("members").value
        if members.strip().lower() in ["false", "no"]:
            self.quest_dict["members"] = False

        # Get the list of series this quest is a part of, if any
        series = template.get("series").value
        if series and "None" not in series:
            series_list = re.split(", |and", quest_helper.clean_display_string(str(series)))
            self.quest_dict["series"] = []
            for series_link in series_list:
                series_name = series_link
                if "|" in series_link:
                    series_name = series_link.split("|")[1]
                self.quest_dict["series"].append(series_name)

        # Parse the infobox for remaining metadata
        self.quest_dict["image"] = quest_helper.get_image(template)
        self.quest_dict["developer"] = quest_helper.extract_sanitized_value(template, "developer")
        self.quest_dict["release_date"] = builder_utils.clean_release_date(quest_helper.extract_sanitized_value(template, "release"))

    def parse_details(self, template):
        """Parse the details section of the quest wiki page"""

        # Retrieve various properties from the template
        self.quest_dict["difficulty"] = quest_helper.get_difficulty(template)
        self.quest_dict["length"] = quest_helper.get_quest_length(template)
        self.quest_dict["description"] = quest_helper.extract_sanitized_value(template, "description")

        # Retrieve the requirements for this quest
        self.set_requirements(template)

    def set_requirements(self, template):
        """Parse the requirements template in the details section"""

        # Extract the requirements for this quest
        requirements = builder_utils.extract_template_value(template, "requirements")

        if not requirements:
            return

        # Setup initial variables for requirements parsing
        required_quests = []
        recommended_quests = []

        required_skills = []
        recommended_skills = []

        misc_requirements = []

        tracking_quests = False
        recommended = False

        self.quest_dict["requirements"] = dict()
        requirements = requirements.splitlines()

        # Parse each line in the requirements section
        for req in requirements:
            req = req.strip()

            req_lower = req.lower()
            if req_lower in ["", "none"]:
                continue

            # if " or " in req_lower:
            #     # If this
            #     if "{{skill" in req_lower and "[[" in req_lower
            #     misc_requirements.append(quest_helper.clean_display_string(req))
            #     continue
            #
            # if " and " in req_lower:
            #     misc_requirements.append(quest_helper.clean_display_string(req))
            #     continue

            # Get any templates used in this requirement
            req_templates = mwparserfromhell.parse(req).filter_templates()

            if "quest points" in req_lower:
                if len(req_templates) == 0:
                    cleaned_req = quest_helper.clean_display_string(req)
                    quest_points = quest_points.lower().replace("quest points").strip()
                    if quest_points.isdigit():
                        self.quest_dict["requirements"]["quest_points"] = int(quest_points)
                    else:
                        misc_requirements.append(cleaned_req)
                    continue

                skill_template = req_templates[0]
                skill_req = quest_helper.get_skill_requirement(skill_template, req)

                if skill_req:
                    self.quest_dict["requirements"]["quest_points"] = skill_req["level"]
                    continue

            # Mark that we're entering a section with quest requirements
            if "quests:" in req_lower:
                tracking_quests = True
                continue

            cleaned_req = quest_helper.clean_quest_name(req)
            if cleaned_req in self.quest_titles:
                if recommended:
                    recommended_quests.append(cleaned_req)
                else:
                    required_quests.append(cleaned_req)
                continue

            # Handle special case for quest requirement listing
            quest_special_cases = ["Completion of", "Completed"]
            if any(case in req for case in quest_special_cases):
                req_quest = quest_helper.clean_quest_name(req[req.index("[["):req.index("]]")])
                if recommended:
                    recommended_quests.append(req_quest)
                else:
                    required_quests.append(req_quest)
                continue

            # Mark that requirements from this point on are recommended, not required
            if "recommended:" in req_lower:
                tracking_quests = False
                recommended = True

                continue

            if req_templates and len(req_templates) > 0 and not (tracking_quests and "**" in req_lower):
                skill_template_names = ["skill clickpic", "skillreq"]
                skill_template = req_templates[0]

                # Check if this is a skill requirement
                if any(name in skill_template.name.lower() for name in skill_template_names):
                    tracking_quests = False

                    skill_req = quest_helper.get_skill_requirement(skill_template, req)

                    if not skill_req:
                        continue

                    if recommended:
                        recommended_skills.append(skill_req)
                    else:
                        required_skills.append(skill_req)
                    continue

            if tracking_quests:
                # Quests under the "Required Quests" heading start with **
                # If the next line doesn't start with **, we've moved out of the quests section
                if "**" not in req_lower:
                    tracking_quests = False
                elif "kudos" not in req_lower:
                    req_quest = quest_helper.clean_quest_name(req)
                    if recommended:
                        recommended_quests.append(req_quest)
                    else:
                        required_quests.append(req_quest)
                    continue

            # Don't include lines that are just notes (e.g. 'No boosts allowed:')
            if ":" in req:
                continue

            # Have a "catch-all" section for any requirements we didn't explicitly handle above
            misc_requirements.append(quest_helper.clean_display_string(req))

        # Add all the parsed requirements to the properties dict
        if recommended_quests or recommended_skills:
            self.quest_dict["recommended_requirements"] = dict()

        if required_quests:
            self.quest_dict["requirements"]["quests"] = required_quests

        if recommended_quests:
            self.quest_dict["recommended_requirements"]["quests"] = required_quests

        if required_skills:
            self.quest_dict["requirements"]["skills"] = required_skills

        if recommended_skills:
            self.quest_dict["recommended_requirements"]["skills"] = recommended_skills

        if misc_requirements:
            self.quest_dict["requirements"]["misc"] = misc_requirements
