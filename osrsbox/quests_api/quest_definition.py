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

from dataclasses import dataclass, asdict
from typing import Dict, List
from pathlib import Path

from osrsbox.quests_api.quest_requirements import QuestRequirements


@dataclass
class QuestDefinition:
    """This class defines the object structure and properties for an OSRS quest.

    The QuestDefinition class is the object that retains all properties for one
    specific quest. Every quest has the properties defined in this class.
    """
    id: int = None
    name: str = None
    members: bool = True
    type: str = None
    difficulty: str = None
    length: str = None
    series: str = None
    description: str = None
    start_point: str = None
    image: str = None
    wiki_url: str = None
    wiki_quick_guide_url: str = None
    developer: str = None
    release_date: str = None  # TODO ISO8601?
    required_for_completing: List[int] = None
    requirements: QuestRequirements = None
    recommended_requirements: QuestRequirements = None
    rewards: str = None

    @classmethod
    def from_json(cls, json_dict: Dict) -> "QuestDefinition":
        """Convert the dictionary under the 'requirements' key into actual :class:`QuestRequirements`"""
        if json_dict.get("requirements"):
            requirements = json_dict.pop("requirements")
            json_dict["requirements"] = QuestRequirements.from_json(requirements)

        if json_dict.get("recommended_requirements"):
            recommended_requirements = json_dict.pop("recommended_requirements")
            json_dict["recommended_requirements"] = QuestRequirements.from_json(recommended_requirements)

        return cls(**json_dict)

    def construct_json(self) -> Dict:
        """Construct dictionary/JSON for exporting or printing.

        :return json_out: All class attributes stored in a dictionary.
        """
        return asdict(self)

    def export_json(self, pretty: bool, export_path: str):
        """Output Monster to JSON file.
        :param pretty: Toggles pretty (indented) JSON output.
        :param export_path: The folder location to save the JSON output to.
        """
        json_out = self.construct_json()
        out_file_name = str(self.id) + ".json"
        out_file_path = Path(export_path / out_file_name)
        with open(out_file_path, "w", newline="\n") as out_file:
            if pretty:
                json.dump(json_out, out_file, indent=4)
            else:
                json.dump(json_out, out_file)
