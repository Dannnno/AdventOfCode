import pathlib
import typing


def get_advent_of_code_path(year: int, day: int) -> pathlib.Path:
	"""
	Get the fully-qualified Path to the desired input file

	Parameters
	==========
	year: int
		The year of the input you want
	day: int
		The day of the input you want

	Returns
	=======
	pathlib.Path
		Location of the file on disk

	Raises
	======
	ValueError
		If given a year/day not in range, or for a challenge that hasn't be attempted
	"""
	if year not in range(2015, 2021):
		raise ValueError(f"AdventOfCode has only existed from 2015-2020")
	if day not in range(1, 26):
		raise ValueError(f"AdventOfCode only has challenges for Dec. 1-25")

	path = pathlib.Path(__file__).parent / str(year) / "inputs" / f"Day{day}Challenge.txt"

	if not path.exists():
		raise ValueError(
			f"AdventOfCode challenge for Day {day} of {year} has not yet been attempted [{path}]"
		)

	return path


def get_advent_of_code_input(year: int, day: int) -> typing.Iterable[str]:
	"""
	Get the challenge input for a given AOC problem.

	Parameters
	==========
	year: int
		The year of the input you want
	day: int
		The day of the input you want

	Yields
	=======
	Iterable[str]
		The lines from the file
	"""

	path = get_advent_of_code_path(year, day)

	with path.open() as f:
		for line in f:
			yield line.strip()
