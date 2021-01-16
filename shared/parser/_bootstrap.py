import re

from collections import namedtuple
from enum import Enum, unique, auto
from pathlib import Path
from typing import List, TextIO


class BnfSyntaxViolationError(Exception):
	"""Represents invalid syntax within a BNF grammar."""


	def __init__(self, line_number: int, grammar_name: str, reason: str, invalid_value: str):
		self.line_number = line_number
		self.grammar_name = grammar_name
		self.reason = reason
		self.invalid_value = invalid_value

	def __str__(self):
		return f"""Specification [{self.grammar_name}] has invalid syntax on line {
				   	   self.line_number} <{self.reason}>: {self.invalid_value}"""

	def __repr__(self):
		return str(self)


@unique
class BnfTokenType(Enum):
	"""A type of token within a BNF grammar"""
	
	NAME = auto()
	LITERAL = auto()
	SEPARATOR = auto()
	COMMENT = auto()
	BUILTIN = auto()


@unique
class BnfBuiltinTokens(Enum):
	"""Builtin tokens that have an established meaning in the EBNF grammar"""

	DIGIT = "digit"
	LETTER = "letter"
	UPPER_LETTER = "uppercase-letter"
	LOWER_LETTER = "lowercase-letter"
	END_OF_LINE = "EOL"
	WORD = "word"
	WHITESPACE = "whitespace"
	SYMBOL = "symbol"

	@property
	def as_rule_name(self) -> str:
		"""
		The builtin token as a valid BNF rule name.
		"""

		return f"<{self.value}>"
	
	@classmethod
	def lookup(cls, value: str) -> BnfBuiltinTokens:
		"""
		Given a value, find the Enum member

		Parameters
		==========
		value: str
			The value to lookup

		Returns
		=======
		BnfBuiltinTokens
			The token that was found

		Raises
		======
		KeyError
			If the value is not found
		"""

		for member in cls.__members__:
			if cls[member].value == value:
				return cls[member]

		raise KeyError(value)

@unique
class BnfSpecialChar(Enum):
	"""Special character(s) in the EBNF grammar."""

	OPEN_BRACKET = '<'
	CLOSE_BRACKET = '>'
	SINGLE_QUOTE = "'"
	DOUBLE_QUOTE = '"'
	SEPARATOR = '|'
	HYPHEN = '-'
	COMMENT = ';'
	ASSIGNMENT = "::="
	EOL = "\r\n"


class BnfToken(namedtuple("BnfToken", "token_type token_value")):
	"""A particular token in an EBNF grammar"""

	pass


def read_grammar_from_file(file: Path) -> List[str]:
	"""
	Read the grammar from a file

	Parameters
	==========
	file: Path
		The file to read from

	Returns
	=======
	List[str]
		The lines of the grammar
	"""

	with open(file) as f:
		return read_grammar(f)


def read_grammar(grammar_stream: TextIO) -> List[str]:
	"""
	Read the grammar and split line-by-line.

	Parameters
	==========
	grammar_stream: TextIO
		The stream to read from

	Returns
	=======
	List[str]
		The lines of the grammar
	"""

	return [line.strip() for line in grammar_stream]


def _lex_grammar(grammar: List[str]) -> List[BnfToken]:
	"""
	Lex a given EBNF grammar into tokens

	Parameters
	==========
	grammar: List[str]
		The lines of the grammar

	Returns
	=======
	tokens: List[BnfToken]
		The tokens in the grammar
	"""

	tokens = []
	for i, line in enumerate(grammar):
		line = line.strip()

		if line.startswith(BnfSpecialChar.COMMENT.value):
			# comments aren't tokens, just strip them
			continue  
		elif line.startswith(BnfSpecialChar.OPEN_BRACKET.value):
			# We have a rule definition
			tokens.extend(_lex_line(i, line))
		elif line:
			# Something unknown happend
			raise BnfSyntaxViolationError(i, "Extended BNF", "Unknown Value", line)
		else:
			# the line was whitespace only
			tokens.append(BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL))
	return tokens


def _lex_line(line_number: int, line: str) -> List[BnfToken]:
	tokens = []

	# Only called in contexts where we've already identified it as having a leading "<"
	mod_line = line.strip()[1:]  # cut off the leading "<""

	# grab the rule name
	try:
		index = mod_line.index(BnfSpecialChar.CLOSE_BRACKET.value)
	except ValueError as e:
		raise BnfSyntaxViolationError(line_number, "Extended BNF", "Missing close-bracket in rule name", line)
	
	rule_name = mod_line[:index]
	if not _validate_rule_name(rule_name):
		raise BnfSyntaxViolationError(line_number, "Extended BNF", "Rule name contains illegal characters", rule_name)
	tokens.append(BnfToken(BnfTokenType.NAME, rule_name))	

	# grab the rule evaluation
	mod_line = mod_line.strip()
	if not mod_line.startswith(BnfSpecialChar.ASSIGNMENT.value):
		raise BnfSyntaxViolationError(line_number, "Extended BNF", f"Rule <{rule_name}> expression is missing an assignment", line)

	mod_line = mod_line[len(BnfSpecialChar.ASSIGNMENT.value):].strip()

	in_quotes = False
	quote_type = None
	running_value = ""
	quote_pairs = {
		# Key = open quote, value = close quote
		BnfSpecialChar.OPEN_BRACKET.value: BnfSpecialChar.CLOSE_BRACKET.value,
		BnfSpecialChar.SINGLE_QUOTE.value: BnfSpecialChar.SINGLE_QUOTE.value
		BnfSpecialChar.DOUBLE_QUOTE.value: BnfSpecialChar.DOUBLE_QUOTE.value
	}
	ws_pattern = re.compile(r"\s")
	for i, char in enumerate(mod_line):
		if in_quotes:
			if char == quote_type:
				token_type = BnfTokenType.LITERAL
				if quote_type == BnfSpecialChar.CLOSE_BRACKET.value:
					if not _validate_rule_name(running_value):
						raise BnfSyntaxViolationError(
							line_number, "Extended BNF",
							f"Rule <{rule_name}> expression had invalid sub-rule", running_value
						)
					token_type = BnfTokenType.NAME
				
				tokens.append(BnfToken(token_type, running_value))
				in_quotes = False
				quote_type = None
				running_value = ""
			else:
				running_value += char
		else:
			if char in quote_pairs:
				if running_value:
					raise BnfSyntaxViolationError(
						line_number, "Extended BNF", 
						f"Rule <{rule_name}> expression had unexpected character", char
					)
				in_quotes = True
				quote_type = quote_pairs[char]
			elif ws_pattern.match(char):
				# skip whitespace outside of quotes
				pass
			elif char == BnfSpecialChar.SEPARATOR.value:
				if running_value:
					raise BnfSyntaxViolationError(
						line_number, "Extended BNF", 
						f"Rule <{rule_name}> expression had unexpected character", char
					)
				tokens.append(BnfToken(BnfTokenType.SEPARATOR, char))
			else:
				raise BnfSyntaxViolationError(
					line_number, "Extended BNF", 
					f"Rule <{rule_name}> expression had unexpected character", char
				)
	tokens.append(BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL))

	# now handle builtins
	for i, (token_type, token_value) in enumerate(tokens):
		if token_type is BnfTokenType.NAME:
			try:
				member = BnfBuiltinTokens.lookup(token_value)
			except KeyError:
				continue
			else:
				tokens[i] = BnfToken(BnfTokenType.BUILTIN, member)

	return tokens


def _validate_rule_name(rule_name: str) -> bool:
	"""
	Check if a given rule name is syntactically valid in our EBNF.

	Parameters
	==========
	rule_name: str
		The prospective name of the rule

	Returns
	=======
	bool
		Whether or not the value is a valid rule name
	"""

	pattern = re.compile(r"""
		[a-zA-Z]  # must have a leading letter
		\w*		  # then 0 or more valid identifier characters
	""", re.VERBOSE)

	return pattern.match(rule_name) is not None

