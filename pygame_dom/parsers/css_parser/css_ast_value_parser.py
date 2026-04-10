from pygame_dom.parsers.css_parser.css_ast_value_types import *
from pygame_dom.parsers.css_parser.css_ast import ASTValueType, ASTValueInstance, ASTValue, ASTProperty
from pygame_dom.parsers.css_parser.css_data import *
from pygame_dom.parsers.css_parser.css_parser_errors import CSSParserError

def get_parsed_ast_value(value: str | list[str]) -> tuple[ASTValueType, ASTValueInstance]:
    if isinstance(value, list):
        return get_parsed_list_value(value)

    return get_parsed_string_value(value)

def get_parsed_list_value(value: list[str]) -> tuple[ASTValueType, ASTValueInstance]:
    if len(value) == 0:
        raise CSSParserError(f"Can not create empty animation.")
    
    if not value[0] == "@":
        return ASTValueType.NAME, Name("empty")

    value.pop(0)

    ast_properties: list[ASTProperty] = []

    for i in range(len(value)):
        if i % 2 == 1 and not i == 0:
            continue

        property_name: str = value[i]

        if i + 1 >= len(value):
            raise CSSParserError(f"Animation can not have an empty property: {property_name}")
        
        property_value: str = value[i + 1]

        ast_value_type: ASTValueType
        ast_value_instance: ASTValueInstance

        ast_value_type, ast_value_instance = get_parsed_string_value(property_value)

        ast_value: ASTValue = ASTValue(ast_value_type, ast_value_instance)

        ast_property: ASTProperty = ASTProperty(property_name, ast_value)

        ast_properties.append(ast_property)

    ast_keyframe: AnimationKeyframe = AnimationKeyframe(ast_properties)

    return ASTValueType.KEYFRAME, ast_keyframe

def get_parsed_string_value(value: str) -> tuple[ASTValueType, ASTValueInstance]:
    separated_values: list[str] = separate_values(value)

    parsed_values: list[tuple[ASTValueType, ASTValueInstance]] = []

    for val in separated_values:
        ast_value: tuple[ASTValueType, ASTValueInstance] = parse_ast_value(val)

        parsed_values.append(ast_value)
    
    parsed_values_length: int = len(parsed_values)

    if parsed_values_length <= 0:
        raise CSSParserError(f"Invalid property value: ")
    
    if parsed_values_length == 1:
        return ast_value
    
    ast_values: list[ASTValue] = []

    for parsed_val_type, parsed_val_value in parsed_values:
        ast_values.append(ASTValue(parsed_val_type, parsed_val_value))

    group: Group = Group(ast_values, False)

    return ASTValueType.GROUP, group

def parse_ast_value(value: str) -> tuple[ASTValueType, ASTValueInstance]:
    ast_value_type: ASTValueType
    ast_value_instance: ASTValueInstance | None = None

    if value.startswith("{") and value.endswith("}"):
        ast_value_type = ASTValueType.EXPR
        ast_value_instance = Expr(value[1:len(value) - 1])

        return ast_value_type, ast_value_instance

    if value.startswith("#"):
        ast_value_type = ASTValueType.COLOR
        ast_value_instance = create_color_from_hex(value[1:], value)

        if not ast_value_instance:
            raise CSSParserError(f"Invalid hex color: {value}")
        
        return ast_value_type, ast_value_instance

    if value.startswith("rgb("):
        ast_value_type = ASTValueType.COLOR
        ast_value_instance = create_color_from_rgb(value[4:len(value) - 1], value)

        if not ast_value_instance:
            raise CSSParserError(f"Invalid rgb color: {value}")

        return ast_value_type, ast_value_instance

    if value.startswith("rgba("):
        ast_value_type = ASTValueType.COLOR
        ast_value_instance = create_color_from_rgba(value[5:len(value) - 1], value)

        if not ast_value_instance:
            raise CSSParserError(f"Invalid rgba color: {value}")
        
        return ast_value_type, ast_value_instance
    
    if value.startswith("url("):
        ast_value_type = ASTValueType.URL
        
        if not value.endswith("\")"):
            raise CSSParserError(f"Invalid url: {value}")
        
        if not value.startswith("url(\""):
            raise CSSParserError(f"Invalid url: {value}")

        ast_value_instance = Url(value[5:len(value) - 2])

        return ast_value_type, ast_value_instance

    if value.startswith("var("):
        ast_value_type = ASTValueType.VAR

        if not value.endswith(")"):
            raise CSSParserError(f"Invalid variable: {value}")
        
        ast_value_instance = Var(value[4:len(value) - 1])

        return ast_value_type, ast_value_instance

    if value.startswith("\"") and value.endswith("\""):
        if len(value) == 1:
            raise CSSParserError(f"Invalid string: {value}")
        
        ast_value_type = ASTValueType.NAME_STRING
        ast_value_instance = NameString(value[1:len(value) - 1])

        return ast_value_type, ast_value_instance

    if value[0].isdigit() or value[0] == "-":
        ast_value_type = ASTValueType.UNIT
        ast_value_instance = create_unit(value)

        if not ast_value_instance:
            raise CSSParserError(f"Invalid unit: {value}")
        
        return ast_value_type, ast_value_instance

    if value in CSS_NAMED_COLORS:
        ast_value_type = ASTValueType.COLOR
        ast_value_instance = create_color_from_name(value)

        return ast_value_type, ast_value_instance

    return ASTValueType.NAME, Name(value)

def separate_values(value: str) -> list[str]:
    values: list[str] = []

    current_value: str = ""
    indent: int = 0

    def create_value() -> None:
        nonlocal current_value, values

        if len(current_value) <= 0:
            return

        values.append(current_value)

        current_value = ""

    def handle_space() -> None:
        nonlocal indent, current_value

        if indent == 0:
            create_value()
        else:
            current_value += " "

    def handle_lparen() -> None:
        nonlocal indent

        indent += 1

    def handle_rparen() -> None:
        nonlocal indent

        indent -= 1

    for char in value:
        match char:
            case " ":
                handle_space()
            case "(" | "[" | "{":
                handle_lparen()

                current_value += char
            case ")" | "]" | "}":
                handle_rparen()

                current_value += char
            case _:
                current_value += char
    
    create_value()

    return values

def create_color_from_name(color_name: str) -> Color:
    color_data: tuple[int, int, int] = CSS_NAMED_COLORS[color_name]

    return Color(float(color_data[0]), float(color_data[1]), float(color_data[2]))

def validate_color_rgb(r: float, g: float, b: float, value: str, color_type: str) -> None:
    if r < 0.0 or r > 255.0:
        raise CSSParserError(f"Invalid r channel for {color_type} color: {value}")

    if g < 0.0 or g > 255.0:
        raise CSSParserError(f"Invalid g channel for {color_type} color: {value}")

    if b < 0.0 or b > 255.0:
        raise CSSParserError(f"Invalid b channel for {color_type} color: {value}")

def validate_color_a(a: float, value: str, color_type: str) -> None:
    if a < 0.0 or a > 1.0:
        raise CSSParserError(f"Invalid a channel for {color_type} color: {value}")

def create_color_from_rgb(rgb_string: str, value: str) -> Color | None:
    rgb_string = rgb_string.replace(" ", "")

    rgb: list[str] = rgb_string.split(",")
    rgb_length: int = len(rgb)

    if rgb_length < 2 or rgb_length > 3:
        return None

    try:
        r: float = float(rgb[0])
        g: float = float(rgb[1])
        b: float = float(rgb[2])

        validate_color_rgb(r, g, b, value, "rgb")

        color: Color = Color(r, g, b)

        return color
    except ValueError:
        raise CSSParserError(f"Invalid rgb color: {value}")

def create_color_from_rgba(rgba_string: str, value: str) -> Color | None:
    rgba_string = rgba_string.replace(" ", "")

    rgba: list[str] = rgba_string.split(",")
    rgba_length: int = len(rgba)

    if rgba_length < 2 or rgba_length > 4:
        return None
    
    if rgba_length == 3:
        try:
            r: float = float(rgba[0])
            g: float = float(rgba[1])
            b: float = float(rgba[2])

            validate_color_rgb(r, g, b, value, "rgba")

            color: Color = Color(r, g, b)

            return color
        except ValueError:
            raise CSSParserError(f"Invalid rgba color: {value}")
    
    try:
        r: float = float(rgba[0])
        g: float = float(rgba[1])
        b: float = float(rgba[2])
        a: float = float(rgba[3])

        validate_color_rgb(r, g, b, value, "rgba")
        validate_color_a(a, value, "rgba")
        
        color: Color = Color(r, g, b, a * 255.0)

        return color
    except ValueError:
        raise CSSParserError(f"Invalid rgba color: {value}")

def create_color_from_hex(hex_string: str, value: str) -> Color | None:
    hex_length: int = len(hex_string)

    if hex_length == 3:
        try:
            r: float = float(int(hex_string[0] * 2, 16))
            g: float = float(int(hex_string[1] * 2, 16))
            b: float = float(int(hex_string[2] * 2, 16))

            validate_color_rgb(r, g, b, value, "hex")

            color: Color = Color(r, g, b)

            return color
        except ValueError:
            raise CSSParserError(f"Invalid hex color: {value}")

    if hex_length == 4:
        try:
            r: float = float(int(hex_string[0] * 2, 16))
            g: float = float(int(hex_string[1] * 2, 16))
            b: float = float(int(hex_string[2] * 2, 16))
            a: float = float(int(hex_string[3] * 2, 16))

            validate_color_rgb(r, g, b, value, "hex")
            validate_color_a(a, value, "hex")

            color: Color = Color(r, g, b, a * 255.0)

            return color
        except ValueError:
            raise CSSParserError(f"Invalid hex color: {value}")

    if hex_length == 6:
        try:
            r: float = float(int(hex_string[0:2], 16))
            g: float = float(int(hex_string[2:4], 16))
            b: float = float(int(hex_string[4:6], 16))

            validate_color_rgb(r, g, b, value, "hex")
            
            color: Color = Color(r, g, b)

            return color
        except ValueError:
            raise CSSParserError(f"Invalid hex color: {value}")

    if hex_length == 8:
        try:
            r: float = float(int(hex_string[0:2], 16))
            g: float = float(int(hex_string[2:4], 16))
            b: float = float(int(hex_string[4:6], 16))
            a: float = float(int(hex_string[6:8], 16))

            validate_color_rgb(r, g, b, value, "hex")
            validate_color_a(a / 255.0, value, "hex")

            color: Color = Color(r, g, b, a)

            return color
        except ValueError:
            raise CSSParserError(f"Invalid hex color: {value}")

def create_unit(unit_string: str) -> Unit | None:
    number_string: str = ""
    unit: str = ""

    is_unit: bool = False

    for char in unit_string:
        if not char.isdigit() and not char in [".", "-"]:
            is_unit = True
        
        if is_unit:
            unit += char
        else:
            number_string += char
    
    if len(number_string) == 0:
        raise CSSParserError(f"Invalid number: {unit_string}")

    number: float = 0.0

    try:
        number = float(number_string)
    except ValueError:
        raise CSSParserError(f"Invalid number: {unit_string}")
    
    if not unit in CSS_UNITS and not unit == "":
        raise CSSParserError(f"Invalid unit: {unit_string}")
    
    return Unit(number, unit)