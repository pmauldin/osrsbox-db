"""
Author:  PH01L
Email:   phoil@osrsbox.com
Website: https://www.osrsbox.com

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

import datetime
import dateparser

import mwparserfromhell


def construct_wiki_url(resource: str) -> str:
    """Construct a url to the given resource on the OSRS Wiki"""
    return f"https://oldschool.runescape.wiki/w/{resource}"


def extract_template_value(template: mwparserfromhell.nodes.template.Template, key: str) -> str:
    """Helper method to extract a value from a template using a specified key.

    This helper method is a simple solution to repeatedly try to fetch a specific
    entry from a wiki text template (a mwparserfromhell template object).

    :param template: A mediawiki wiki text template.
    :param key: The key to query in the template.
    :return value: The extracted template value based on supplied key.
    """
    value = None
    try:
        value = template.get(key).value
        value = value.strip()
        return value
    except ValueError:
        return value


def clean_release_date(value: str) -> str:
    """A helper method to convert the release date entry from an OSRS Wiki infobox.

    The returned value will be a specifically formatted string: dd Month YYYY.
    For example, 25 June 2017 or 01 November 2014.

    :param value: The extracted raw wiki text.
    :return release_date: A cleaned release date of an item.
    """
    if value is None:
        return None

    release_date = value
    release_date = release_date.strip()
    release_date = release_date.replace("[", "")
    release_date = release_date.replace("]", "")
    try:
        release_date = datetime.datetime.strptime(release_date, "%d %B %Y")
        return release_date.date().isoformat()
    except ValueError:
        pass

    try:
        release_date = dateparser.parse(release_date)
        release_date = release_date.date().isoformat()
    except (ValueError, TypeError, AttributeError):
        return None

    return release_date
