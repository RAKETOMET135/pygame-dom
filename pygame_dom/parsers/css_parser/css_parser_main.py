from typing import Final
from pygame_dom.parsers.css_parser.css_tokenizer import CSSToken, get_tokens_from_file
from pygame_dom.parsers.css_parser.css_parser import ASTStyleSheet, parse_css_tokens

def get_parsed_css(file_path: str) -> None:
    tokens: tuple[CSSToken] = get_tokens_from_file(file_path)

    ast: ASTStyleSheet = parse_css_tokens(tokens)

    __test_print_ast(ast)
    

# TESTS
def __test_print_ast(ast: ASTStyleSheet) -> None:
    for rule in ast.rules:
        print(rule.selector)
        
        for _property in rule.properties:
            print("> " + _property.name)
    
            print("  > " + _property.value.datatype.name)
            print("  > " + str(_property.value.value))

if __name__ == "__main__":
    __TEST_FILE_PATH: Final[str] = "test.css"

    get_parsed_css(__TEST_FILE_PATH)