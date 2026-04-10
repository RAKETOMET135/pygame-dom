from pygame_dom.parsers.css_parser.css_ast_value_types import *
from pygame_dom.parsers.css_parser.css_ast import ASTValueType, ASTValueInstance
from pygame_dom.parsers.css_parser.css_data import *
from pygame_dom.parsers.css_parser.css_parser_errors import CSSParserError

def get_parsed_ast_value(value: str) -> tuple[ASTValueType, ASTValueInstance]:
    ast_value_type: ASTValueType
    ast_value_instance: ASTValueInstance | None = None

    if value.startswith("{") and value.endswith("}"):
        ast_value_type = ASTValueType.EXPR
        ast_value_instance = Expr(value[1:len(value) - 1])

        return ast_value_type, ast_value_instance

    if value.startswith("rgb("):
        ast_value_type = ASTValueType.COLOR
        ast_value_instance = create_color_from_rgb(value[4:len(value) - 1], value)

        if not ast_value_instance:
            raise CSSParserError(f"Invalid rgb color: {value}")

        return ast_value_type, ast_value_instance

    if value in CSS_NAMED_COLORS:
        ast_value_type = ASTValueType.COLOR
        ast_value_instance = create_color_from_name(value)

        return ast_value_type, ast_value_instance

    if not ast_value_instance:
        raise CSSParserError(f"Invalid property value: {value}")

def create_color_from_name(color_name: str) -> Color:
    color_data: tuple[int, int, int] = CSS_NAMED_COLORS[color_name]

    return Color(float(color_data[0]), float(color_data[1]), float(color_data[2]))

def create_color_from_rgb(rgb_string: str, value: str) -> Color | None:
    rgb_string = rgb_string.replace(" ", "")

    rgb: list[str] = rgb_string.split(",")

    if len(rgb) < 2 or len(rgb) > 3:
        return None

    try:
        color: Color = Color(float(rgb[0]), float(rgb[1]), float(rgb[2]))

        return color
    except ValueError:
        raise CSSParserError(f"Invalid rgb color: {value}")

def create_color_from_rgba(rgba_string: str) -> Color:
    pass

def create_color_from_hex(hex_string: str) -> Color:
    pass