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

from dataclasses import dataclass
from typing import Dict, List

from osrsbox.quests_api.quest_item_requirement import QuestItemRequirement
from osrsbox.quests_api.quest_skill_requirement import QuestSkillRequirement


@dataclass
class QuestRequirements:
    """This class defines the object structure and properties
    for an OSRS quest's requirements."""
    quest_points: int = None
    skills: List[QuestSkillRequirement] = None
    items: List[QuestItemRequirement] = None
    quests: List[str] = None
    misc: List[str] = None

    @classmethod
    def from_json(cls, json_dict: Dict) -> "QuestRequirements":
        """Convert the dictionary under the 'requirements' key into actual :class:`QuestRequirements`"""
        if json_dict.get("skills"):
            skills = json_dict.pop("skills")
            skills_list = []
            for skill in skills:
                skills_list.append(QuestSkillRequirement(**skill))
            json_dict["skills"] = skills_list

        if json_dict.get("items"):
            items = json_dict.pop("items")
            items_list = []
            for item in items:
                items_list.append(QuestItemRequirement(**item))
            json_dict["items"] = items_list

        return cls(**json_dict)

