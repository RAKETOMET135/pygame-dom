from typing import Final
from pygame_dom.parsers.css_parser.css_tokenizer import CSSToken, get_tokens_from_file
from pygame_dom.parsers.css_parser.css_parser import ASTStyleSheet, parse_css_tokens

def get_parsed_css(file_path: str) -> None:
    tokens: tuple[CSSToken] = get_tokens_from_file(file_path)

    ast: ASTStyleSheet = parse_css_tokens(tokens)

# TESTS
if __name__ == "__main__":
    __TEST_FILE_PATH: Final[str] = "test.css"

    get_parsed_css(__TEST_FILE_PATH)