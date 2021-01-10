import collections
import enum
import re
import typing


class BnfSyntaxViolation(Exception):
	pass


@enum.unique
class BnfTokenType(enum.Enum):
	NAME = enum.auto()
	LITERAL = enum.auto()
	SEPARATOR = enum.auto()
	COMMENT = enum.auto()
	BUILTIN = enum.auto()


@enum.unique
class BnfBulitinTokens(enum.Enum):
	DIGIT = "digit"
	LETTER = "letter"
	UPPER_LETTER = "uppercase-letter"
	LOWER_LETTER = "lowercase-letter"
	END_OF_LINE = "EOL"
	WORD = "word"
	WHITESPACE = "whitespace"
	SYMBOL = "symbol"


@enum.unique
class BnfSpecialChar(enum.Enum):
	OPEN_BRACKET = '<'
	CLOSE_BRACKET = '>'
	SINGLE_QUOTE = "'"
	DOUBLE_QUOTE = '"'
	SEPARATOR = '|'
	HYPHEN = '-'
	COMMENT = ';'
	ASSIGNMENT = "::="


class BnfToken(collections.namedtuple("BnfToken", "token_type token_value")):
	pass


class _BootstrapBnfParserGenerator:
	def __init__(self, name: str, specification: typing.Union[str, typing.Iterable[str]]):
		self.name = name
		if hasattr(specification, "splitlines"):
			specification = typing.cast(str, specification).splitlines()
		self.spec = list(specification)

	def lex(self):
		tokens = []
		for i, line in enumerate(self.spec):
			line = line.strip()
			if line.startswith(BnfSpecialChar.COMMENT.value):
				self._lex_comment(line, tokens)
			elif line.startswith(BnfSpecialChar.OPEN_BRACKET.value):
				self._lex_rule_assignment(line, i, tokens)
			elif line:
				self._error(line, "no rule", line)
		return tokens

	def _lex_comment(self, line: str, tokens: typing.List[str]):
		# do nothing
		pass

	def _lex_rule_assignment(self, line: str, linenum: int, tokens: typing.List[str]):
		rule_name = self._lex_rule_name(line, linenum)
		rem_line = line[len(rule_name) + 2:].strip()  # jump ahead to the rule assignment
		if not rem_line.startswith(BnfSpecialChar.ASSIGNMENT.value):
			self._error(linenum, "no rule assignment", rem_line)
		rem_line = rem_line[len(BnfSpecialChar.ASSIGNMENT.value):].strip()  # get the actual assignment

		self._lex_assignment_options(rem_line, linenum, tokens)

	def _lex_assignment_options(self, line: str, linenum: int, tokens: typing.List[str]):
		in_literal = False
		quote_type = (BnfSpecialChar.DOUBLE_QUOTE.value, BnfSpecialChar.SINGLE_QUOTE.value)
		running_literal = ""
		for char in line:
			if self._is_quote_char(char, quote_type):
				if in_literal:
					tokens.append(BnfToken(BnfTokenType.LITERAL, running_literal))
					in_literal = False
					quote_type = (BnfSpecialChar.DOUBLE_QUOTE.value, BnfSpecialChar.SINGLE_QUOTE.value)
					running_literal = ""
				else:
					in_literal = True
					quote_type = tuple(char)
					running_literal = ""
			# TODO - parse out a rule
			# TODO - parse out a pipe
			# TODO - parse out internal characters



		pass

	@staticmethod
	def _is_quote_char(char: str, 
					   desired_quote_chars: typing.Iterable[str]
					  ) -> bool:
		return char in desired_quote_chars

	def _lex_rule_name(self, line: str, linenum: int):
		try:
			end_rule_name = line.index(BnfSpecialChar.CLOSE_BRACKET.value)
		except ValueError:
			self._error(linenum, "no closing bracket", line)

		rule_name_pattern = re.compile(r"[a-zA-Z]\w*", re.VERBOSE)
		rule_name = line[1:end_rule_name]
		if not rule_name_pattern.match(rule_name):
			self._error(linenum, "invalid rule name", rule_name)

		return rule_name

	def _error(self, linenum: int, reason: str, value: str):
		raise BnfSyntaxViolation(
			f"Specification [{self.name}] has invalid syntax on line {linenum} <{reason}>: {value}"
		)
