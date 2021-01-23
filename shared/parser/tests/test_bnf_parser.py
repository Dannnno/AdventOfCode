import pytest

from shared.parser.bnf_parser import _BootstrapBnfParserGenerator, BnfSyntaxViolation, BnfToken, BnfTokenType, BnfBuiltinTokens, BnfSpecialChar

@pytest.mark.skip()
def test_lex_skips_comments():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples"""
	pg = _BootstrapBnfParserGenerator("test_lex_skips_comments", spec)
	tokens = pg.lex()
	assert len(tokens) == 1

@pytest.mark.skip()
def test_lex_errors_on_incomplete_rulename():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_incomplete_rulename", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()

@pytest.mark.skip()
def test_lex_errors_on_invalid_rulename():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax!>"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_invalid_rulename", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()

@pytest.mark.skip()
def test_lex_errors_on_no_assignment():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax>            asdf"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_no_assignment", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()

@pytest.mark.skip()
def test_lex_errors_on_internal_incomplete_rulename():
	spec = """<syntax> ::= <rule"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_internal_incomplete_rulename", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()

@pytest.mark.skip()
def test_lex_errors_on_internal_invalid_rulename():
	spec = """<syntax> ::= <rule!>"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_internal_invalid_rulename", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()

@pytest.mark.skip()
def test_lex_simple_grammar():
	spec = """
; comment
<rule> ::= "whatever"
   <indent-rule>::=<other-rule> | "or me"
<other-rule>                 ::=                   "a" | "b" | "c" | <digit>
"""
	pg = _BootstrapBnfParserGenerator("test_lex_simple_grammar", spec)
	tokens = pg.lex()

	expected = [
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
		BnfToken(BnfTokenType.NAME, "rule"), 
		BnfToken(BnfTokenType.LITERAL, "whatever"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
		BnfToken(BnfTokenType.NAME, "indent-rule"), 
		BnfToken(BnfTokenType.NAME, "other-rule"), 
		BnfToken(BnfTokenType.SEPARATOR, "|"),
		BnfToken(BnfTokenType.LITERAL, "or me"),
		BnfToken(BnfTokenType.LITERAL, BnfSpecialChar.EOL),
		BnfToken(BnfTokenType.NAME, "other-rule"),
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
