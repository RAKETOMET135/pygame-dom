from typing import Final
from pygame_dom.parsers.css_parser.css_token import CSSToken, CSSTokenType
from pygame_dom.parsers.css_parser.css_parser_errors import CSSTokenizerError

def get_tokens_from_file(file_path: str) -> tuple[CSSToken]:
    file_content: str = open_css_file(file_path)
    css_tokens: tuple[CSSToken] = tokenize_file_content(file_content)

    return css_tokens

def tokenize_file_content(file_content: str) -> tuple[CSSToken]:
    for to_remove_str in ["\n", "\r", "\t", "\b", "\f", "\f", "\v", "\\"]:
        file_content = file_content.replace(to_remove_str, "")

    tokens: list[CSSToken] = []

    current_token: str = ""
    indent: int = 0

    is_comment: bool = False

    def create_token(token_type: CSSTokenType = CSSTokenType.NAME) -> None:
        nonlocal current_token, tokens

        if len(current_token) <= 0 or current_token.isspace():
            return
        
        token: CSSToken = CSSToken(token_type, current_token)
        tokens.append(token)

        current_token = ""

    def handle_lbrace() -> None:
        nonlocal current_token, indent

        if indent == 0:
            create_token(CSSTokenType.NAME)
        
            current_token = "{"
            create_token(CSSTokenType.LBRACE)

        indent += 1

    def handle_colon() -> None:
        nonlocal current_token

        create_token(CSSTokenType.PROPERTY)

        current_token = ":"
        create_token(CSSTokenType.COLON)

    def handle_semicolon() -> None:
        nonlocal current_token

        create_token(CSSTokenType.VALUE)

        current_token = ";"
        create_token(CSSTokenType.SEMICOLON)

    def handle_rbrace() -> None:
        nonlocal current_token, indent

        indent -= 1

        if indent == 1:
            current_token = "{" + current_token[1:] + "}"

            create_token(CSSTokenType.VALUE)
        elif indent == 0:
            create_token(CSSTokenType.VALUE)

            current_token = "}"
            create_token(CSSTokenType.RBRACE)

    def handle_slash(char_index: int) -> None:
        nonlocal is_comment

        if char_index > 0 and file_content[char_index - 1] == "*":
            is_comment = False
        elif char_index < len(file_content) - 1 and file_content[char_index + 1] == "*":
            is_comment = True

    for i, char in enumerate(file_content):
        if is_comment and not char == "/":
            continue

        match char:
            case "{":
                handle_lbrace()
            case ":":
                handle_colon()
            case ";":
                handle_semicolon()
            case "}":
                handle_rbrace()
            case "/":
                handle_slash(i)
            case _:
                current_token += char
    
    return tuple(tokens)

def open_css_file(file_path: str) -> str:
    if not file_path.endswith(".css"):
        raise CSSTokenizerError(f"File on provided path {file_path} is not a CSS file.")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            file_content: str = file.read()

            return file_content
    except FileNotFoundError:
        raise CSSTokenizerError(f"File on path {file_path} does not exist.")
    except PermissionError:
        raise CSSTokenizerError(f"File on path {file_path} is not accessable.")
    except IsADirectoryError:
        raise CSSTokenizerError(f"File on path {file_path} is a directory.")
    except UnicodeDecodeError:
        raise CSSTokenizerError(f"File on path {file_path} does not have correct encoding, only UTF-8 is supported.")
    except OSError as e:
        raise CSSTokenizerError(f"OS error while reading file on path '{file_path}'.") from e

# TESTS
if __name__ == "__main__":
    __TEST_FILE_PATH: Final[str] = "test.css"

    print(get_tokens_from_file(__TEST_FILE_PATH))