from shared.parser._bootstrap import BnfSyntaxViolationError, BnfToken, BnfTokenType, BnfBuiltinTokens, BnfSpecialChar, _lex_grammar, read_grammar, _parse_bnf_grammar

import pytest


def test_lex_skips_comments():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples"""
	tokens = _lex_grammar(read_grammar(spec))
	assert len(tokens) == 0

def test_lex_errors_on_incomplete_rulename():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax"""
	with pytest.raises(BnfSyntaxViolationError):
		tokens = _lex_grammar(read_grammar(spec))

def test_lex_errors_on_invalid_rulename():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax!>"""
	with pytest.raises(BnfSyntaxViolationError):
		tokens = _lex_grammar(read_grammar(spec))

def test_lex_errors_on_no_assignment():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax>            asdf"""
	with pytest.raises(BnfSyntaxViolationError):
		tokens = _lex_grammar(read_grammar(spec))

def test_lex_errors_on_internal_incomplete_rulename():
	spec = """<syntax> ::= <rule"""
	with pytest.raises(BnfSyntaxViolationError):
		tokens = _lex_grammar(read_grammar(spec))

def test_lex_errors_on_internal_invalid_rulename():
	spec = """<syntax> ::= <rule!>"""
	with pytest.raises(BnfSyntaxViolationError):
		tokens = _lex_grammar(read_grammar(spec))

def test_lex_simple_grammar():
	spec = """
; comment
<rule> ::= "whatever"
   <indent-rule>::=<other-rule> | "or me"
<other-rule>                 ::=                   "a" | "b" | "c" | <digit>
"""
	tokens = _lex_grammar(read_grammar(spec))

	expected = [
		BnfToken(BnfTokenType.NAME, "rule"), 
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, "whatever"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
		BnfToken(BnfTokenType.NAME, "indent-rule"), 
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "other-rule"), 
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "or me"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
		BnfToken(BnfTokenType.NAME, "other-rule"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, "a"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "b"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "c"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.DIGIT),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL)
	]

	assert tokens == expected

def test_lex_full_grammar():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
              <syntax>            ::= <rule> | <rule> <syntax>
              <rule>              ::= <opt-whitespace> "<" <rule-name> ">" <opt-whitespace> "::=" <opt-whitespace> <expression> <line-end> | <comment>
              ; The addition of comments is an extension to "traditional" BNF
              <comment>           ::= <opt-whitespace> ";" <comment-text> <line-end>
              <comment-text>      ::= <text1> | <text2>
              <opt-whitespace>    ::= " " <opt-whitespace> | ""
              <expression>        ::= <list> | <list> <opt-whitespace> "|" <opt-whitespace> <expression>
              <line-end>          ::= <opt-whitespace> <EOL> | <line-end> <line-end>
              <list>              ::= <term> | <term> <opt-whitespace> <list>
              <term>              ::= <literal> | "<" <rule-name> ">"
              <literal>           ::= '"' <text1> '"' | "'" <text2> "'"
              <text1>             ::= "" | <character1> <text1>
              <text2>             ::= '' | <character2> <text2>
              <character>         ::= <letter> | <digit> | <symbol>
              <character1>        ::= <character> | "'"
              <character2>        ::= <character> | '"'
              <rule-name>         ::= <letter> | <rule-name> <rule-char>
              <rule-char>         ::= <letter> | <digit> | "-" | "_"
              ; Split into two sections for clarity
              <letter>            ::= <uppercase-letter> | <lowercase-letter>
              <uppercase-letter>  ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" 
              <lowercase-letter>  ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
              <digit>             ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
              <symbol>            ::=  "|" | " " | "!" | "#" | "$" | "%" | "&" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" | ">" | "=" | "<" | "?" | "@" | "[" | "\" | "]" | "^" | "_" | "`" | "{" | "}" | "~"
              ; Providing built-ins that can be assumed
              <built-in-rule>     ::= "<digit>" | "<letter>" | "<lowercase-letter>" | "<uppercase-letter>" | "<EOL>" | "<word>" | "<whitespace>" | "<symbol>"
           """

	expected = [
		# ; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
		# <syntax>            ::= <rule> | <rule> <syntax>
		BnfToken(BnfTokenType.NAME, "syntax"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "rule"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "rule"),
		BnfToken(BnfTokenType.NAME, "syntax"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <rule>              ::= <opt-whitespace> "<" <rule-name> ">" <opt-whitespace> "::=" <opt-whitespace> <expression> <line-end> | <comment>
		BnfToken(BnfTokenType.NAME, "rule"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.LITERAL, "<"),
		BnfToken(BnfTokenType.NAME, "rule-name"),
		BnfToken(BnfTokenType.LITERAL, ">"),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.LITERAL, "::="),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.NAME, "expression"),
		BnfToken(BnfTokenType.NAME, "line-end"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "comment"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # ; The addition of comments is an extension to "traditional" BNF
        # <comment>           ::= <opt-whitespace> ";" <comment-text> <line-end>
		BnfToken(BnfTokenType.NAME, "comment"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.LITERAL, ";"),
		BnfToken(BnfTokenType.NAME, "comment-text"),
		BnfToken(BnfTokenType.NAME, "line-end"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <comment-text>      ::= <text1> | <text2>
		BnfToken(BnfTokenType.NAME, "comment-text"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "text1"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "text2"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <opt-whitespace>    ::= " " <opt-whitespace> | ""
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, " "),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, ""),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <expression>        ::= <list> | <list> <opt-whitespace> "|" <opt-whitespace> <expression>
		BnfToken(BnfTokenType.NAME, "expression"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "list"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "list"),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.LITERAL, "|"),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.NAME, "expression"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <line-end>          ::= <opt-whitespace> <EOL> | <line-end> <line-end>
		BnfToken(BnfTokenType.NAME, "line-end"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.END_OF_LINE),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "line-end"),
		BnfToken(BnfTokenType.NAME, "line-end"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <list>              ::= <term> | <term> <opt-whitespace> <list>
		BnfToken(BnfTokenType.NAME, "list"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "term"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "term"),
		BnfToken(BnfTokenType.NAME, "opt-whitespace"),
		BnfToken(BnfTokenType.NAME, "list"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <term>              ::= <literal> | "<" <rule-name> ">"
		BnfToken(BnfTokenType.NAME, "term"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "literal"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<"),
		BnfToken(BnfTokenType.NAME, "rule-name"),
		BnfToken(BnfTokenType.LITERAL, ">"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <literal>           ::= '"' <text1> '"' | "'" <text2> "'"
		BnfToken(BnfTokenType.NAME, "literal"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, '"'),
		BnfToken(BnfTokenType.NAME, "text1"),
		BnfToken(BnfTokenType.LITERAL, '"'),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "'"),
		BnfToken(BnfTokenType.NAME, "text2"),
		BnfToken(BnfTokenType.LITERAL, "'"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <text1>             ::= "" | <character1> <text1>
		BnfToken(BnfTokenType.NAME, "text1"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, ""),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "character1"),
		BnfToken(BnfTokenType.NAME, "text1"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <text2>             ::= '' | <character2> <text2>
		BnfToken(BnfTokenType.NAME, "text2"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, ""),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "character2"),
		BnfToken(BnfTokenType.NAME, "text2"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <character>         ::= <letter> | <digit> | <symbol>
		BnfToken(BnfTokenType.NAME, "character"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.LETTER),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.DIGIT),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.SYMBOL),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <character1>        ::= <character> | "'"
		BnfToken(BnfTokenType.NAME, "character1"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "character"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "'"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <character2>        ::= <character> | '"'
		BnfToken(BnfTokenType.NAME, "character2"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.NAME, "character"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, '"'),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <rule-name>         ::= <letter> | <rule-name> <rule-char>
		BnfToken(BnfTokenType.NAME, "rule-name"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.LETTER),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.NAME, "rule-name"),
		BnfToken(BnfTokenType.NAME, "rule-char"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <rule-char>         ::= <letter> | <digit> | "-" | "_"
		BnfToken(BnfTokenType.NAME, "rule-char"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.LETTER),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.DIGIT),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "-"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "_"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # ; Split into two sections for clarity
        # <letter>            ::= <uppercase-letter> | <lowercase-letter>
		BnfToken(BnfTokenType.NAME, "letter"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.UPPER_LETTER),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.BUILTIN, BnfBuiltinTokens.LOWER_LETTER),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <uppercase-letter>  ::= "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" 
		BnfToken(BnfTokenType.NAME, "uppercase-letter"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, "A"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "B"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "C"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "D"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "E"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "F"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "G"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "H"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "I"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "J"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "K"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "L"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "M"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "N"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "O"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "P"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "Q"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "R"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "S"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "T"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "U"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "V"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "W"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "X"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "Y"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "Z"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <lowercase-letter>  ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
        BnfToken(BnfTokenType.NAME, "lowercase-letter"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, "a"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "b"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "c"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "d"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "e"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "f"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "g"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "h"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "i"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "j"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "k"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "l"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "m"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "n"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "o"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "p"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "q"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "r"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "s"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "t"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "u"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "v"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "w"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "x"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "y"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "z"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <digit>             ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
        BnfToken(BnfTokenType.NAME, "digit"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),	
		BnfToken(BnfTokenType.LITERAL, "0"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "1"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "2"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "3"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "4"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "5"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "6"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "7"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "8"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "9"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # <symbol>            ::=  "|" | " " | "!" | "#" | "$" | "%" | "&" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" | ">" | "=" | "<" | "?" | "@" | "[" | "\" | "]" | "^" | "_" | "`" | "{" | "}" | "~"
        BnfToken(BnfTokenType.NAME, "symbol"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),	
		BnfToken(BnfTokenType.LITERAL, "|"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, " "),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "!"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "#"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "$"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "%"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "&"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "("),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, ")"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "*"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "+"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, ","),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "-"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "."),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "/"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, ":"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, ";"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, ">"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "="),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "?"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "@"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "["),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, ""),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "]"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "^"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "_"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "`"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "{"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "}"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "~"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
        # ; Providing built-ins that can be assumed
        # <built-in-rule>     ::= "<digit>" | "<letter>" | "<lowercase-letter>" | "<uppercase-letter>" | "<EOL>" | "<word>" | "<whitespace>" | "<symbol>"
        BnfToken(BnfTokenType.NAME, "built-in-rule"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.ASSIGNMENT),
		BnfToken(BnfTokenType.LITERAL, "<digit>"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<letter>"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<lowercase-letter>"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<uppercase-letter>"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<EOL>"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<word>"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<whitespace>"),
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "<symbol>"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
	]

	tokens = _lex_grammar(read_grammar(spec))

	assert tokens == expected

def test_parse_simple():
	spec = """
; comment
<rule> ::= "whatever"
   <indent-rule>::=<other-rule> | "or me"
<other-rule>                 ::=                   "a" | "b" | "c" | <digit>
"""
	tokens = _lex_grammar(read_grammar(spec))
	rules = _parse_bnf_grammar(tokens)

	expected = {}

	assert rules == expected