from pathlib import Path
import sys

import pytest

# Ensure repository root is on the path so the parser module can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from djvu2pdf_toc_parser import parse_sexp, next_quote


def test_next_quote_replaces_escaped_quotes():
    input_str = ' "He said \\"Hi\\"" trailing'
    index, result = next_quote(input_str, 0)

    assert result == '"He said \'Hi\'"'
    # index should point right after the closing quote
    assert input_str[index - 1] == '"'


def test_parse_sexp_bookmarks_structure():
    toc_input = (
        '(bookmarks ("Intro" "#1") '
        '("Chapter 1" "#5" ("Section" "#7")))))'
    )
    toc_output = []

    parse_sexp(toc_input[1:], toc_output, '', 0)

    assert toc_output == ['"Intro" "1"', '"Chapter 1" "5"', '\t"Section" "7"']
