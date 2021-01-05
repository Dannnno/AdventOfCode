from enum import Enum, auto

import requests

class AdventOfCodeUrlTypeEnum(Enum):

	CHALLENGE_FIRST_PART = auto()
	CHALLENGE_SECOND_PART = auto()
	INPUT = auto()


def get_advent_of_code_url(year, day, url_type=AdventOfCodeUrlTypeEnum.INPUT):
	if year not in range(2015, 2021):
		raise ValueError(f"AdventOfCode has only existed from 2015-2020")
	if day not in range(1, 26):
		raise ValueError(f"AdventOfCode only has challenges for Dec. 1-25")

	if url_type is AdventOfCodeUrlTypeEnum.CHALLENGE_FIRST_PART:
		return f"https://adventofcode.com/{year}/day/{day}"
	elif url_type is AdventOfCodeUrlTypeEnum.CHALLENGE_SECOND_PART:
		return f"https://adventofcode.com/{year}/day/{day}#part2"
	else:
		return f"https://adventofcode.com/{year}/day/{day}/input"

def get_advent_of_code_input(year, day):
	url = get_advent_of_code_url(year, day)

	return requests.get(url)	
