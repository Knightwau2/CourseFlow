from typing import Tuple, List

from PyPDF2 import PdfReader, PageObject
import re
import os


unit_listings = "handbooks/DeakinUniversity2019_Units-v4-accessible.pdf"
unit_listings_text_cache = "handbooks/unit_listings_text_cache.txt"
course_listings = "handbooks/DeakinUniversity2019_Courses-v4-accessible.pdf"
unit_details_first_page = 27
unit_details_last_page = 1210
units = []




class Unit:
    id = 1

    def __init__(self):
        self.code = f"DEFAULT_CODE_{Unit.id}"
        self.title = f"DEFAULT_TITLE_{Unit.id}"
        self.raw_information = ""
        self.description = ""
        self.prerequisites = []
        self.corequisites = []
        self.incompatible_with = []
        self.constraints = {}
        Unit.id += 1

    def __repr__(self):
        return f"{self.code} - {self.title}"


# todo: write tests
# fixme: ACA711, ACR210 title capturing "Offering information"
# todo: write tests for second group's lookahead cases
def extract_unit_codes_and_titles(text: str) -> List[Unit]:
    # Comment partially generated by GPT-3.5 2023-04-06
    # Regex pattern to capture a unit code, title, and raw unit information from a handbook page.
    # 1. Matches three uppercase letters followed by three digits as the unit code,
    # 2. any text between a hyphen or em dash and the text " Enrolment modes:" or " Year:" as the title,
    # 3. and any text before the next unit code using a positive lookahead assertion.
    pattern = re.compile(r"([A-Z]{3}\d{3})"  # 1
                         r" [–-] "
                         r"(.+?)(?= Enrolment modes:| Year:| Offering information:)"  # 2
                         r"(.+?)(?=[A-Z]{3}\d{3} [–-])")  # 3

    units = []
    # Create a new Unit object for each unit extracted from the handbook
    for match in pattern.finditer(text):
        unit = Unit()
        unit.code = match.group(1)
        unit.title = match.group(2)
        unit.raw_information = match.group(3).strip()

        units.append(unit)

    return units

def read_unit_details(text: str) -> List[Unit]:
    # Replace newline characters with spaces
    text = text.replace("\n", " ")
    # Convert any double spaces to single spaces
    text = re.sub(r" {2,}", " ", text)

    # Split the text by unit information
    units = extract_unit_codes_and_titles(text)

    return units


if __name__ == "__main__":
    # Read the handbook text from the cache file if it exists, otherwise create the cache file
    if os.path.exists(unit_listings_text_cache):
        with open(unit_listings_text_cache, "r", encoding="utf-8") as file:
            text = " ".join(file.readlines())
    else:
        # Read all unit information text from the handbook PDF
        reader = PdfReader(unit_listings)
        text = []
        for page in reader.pages[unit_details_first_page - 1:]:
            text.append(page.extract_text(orientations=(0,)))
        text = " ".join(text)

        # Write the text to a cache which will be used in the future
        with open(unit_listings_text_cache, "w", encoding="utf-8") as file:
            file.write(text)
    units = read_unit_details(text)
    print()
