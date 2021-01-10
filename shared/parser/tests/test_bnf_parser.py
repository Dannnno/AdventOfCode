import pytest

from shared.parser import _BootstrapBnfParserGenerator, BnfSyntaxViolation


def test_lex_skips_comments():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples"""
	pg = _BootstrapBnfParserGenerator("test_lex_skips_comments", spec)
	tokens = pg.lex()
	assert len(tokens) == 0

def test_lex_errors_on_incomplete_rulename():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_incomplete_rulename", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()

def test_lex_errors_on_invalid_rulename():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax!>"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_invalid_rulename", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()

def test_lex_errors_on_no_assignment():
	spec = """; BNF adapted from https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form#Further_examples
<syntax>            asdf"""
	pg = _BootstrapBnfParserGenerator("test_lex_errors_on_no_assignment", spec)
	with pytest.raises(BnfSyntaxViolation):
		tokens = pg.lex()




