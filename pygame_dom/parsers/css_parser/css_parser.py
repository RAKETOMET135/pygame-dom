from pygame_dom.parsers.css_parser.css_ast import ASTValue, ASTProperty, ASTRule, ASTStyleSheet, ASTValueType, ASTValueInstance
from pygame_dom.parsers.css_parser.css_tokenizer import CSSToken, CSSTokenType
from pygame_dom.parsers.css_parser.css_ast_value_parser import get_parsed_ast_value
from pygame_dom.parsers.css_parser.css_parser_errors import CSSParserError

def parse_css_tokens(tokens: tuple[CSSToken]) -> ASTStyleSheet:
    selector_groups: list[dict] = create_selector_groups(tokens)
    selector_groups = create_properties(selector_groups)

    ast: ASTStyleSheet = create_ast(selector_groups)

    return ast

def create_ast_value(value: str) -> ASTValue:
    ast_value_type: ASTValueType
    ast_value_instance: ASTValueInstance

    ast_value_type, ast_value_instance = get_parsed_ast_value(value)

    return ASTValue(ast_value_type, ast_value_instance)

def create_ast_property(property: str, value: str) -> ASTProperty:
    ast_value: ASTValue = create_ast_value(value)

    return ASTProperty(property, ast_value)

def create_ast_rule(group: dict) -> ASTRule:
    selector: str = group["selector"]
    properties: dict = group["properties"]
    
    ast_properties: list = []

    for property_name, property_value in properties.items():
        ast_property: ASTProperty = create_ast_property(property_name, property_value)

        ast_properties.append(ast_property)

    return ASTRule(selector, ast_properties)

def create_ast(selector_groups: list[dict]) -> ASTStyleSheet:
    rules: list[ASTRule] = []

    for group in selector_groups:
        rule: ASTRule = create_ast_rule(group)

        rules.append(rule)

    return ASTStyleSheet(rules)

def parse_group_properties(group: dict) -> dict:
    parsed_properties: dict = {}
    current_property: str | None = None

    is_keyframes: bool = False

    if group["selector"].startswith("@"):
        is_keyframes = True

    def create_property(property_name: str) -> None:
        nonlocal parsed_properties, current_property

        if not property_name in parsed_properties:
            if is_keyframes:
                parsed_properties[property_name] = []
            else:
                parsed_properties[property_name] = None
        
        current_property = property_name

    for property_token in group["properties"]:
        token_type: CSSTokenType = property_token.token_type

        if is_keyframes:
            match token_type:
                case CSSTokenType.KEYFRAME:
                    if current_property:
                        raise CSSParserError(f"Expected '}}' before animation keyframe '{property_token.token_value}'.")

                    create_property(property_token.token_value)
                case CSSTokenType.LBRACE:
                    if not current_property:
                        raise CSSParserError(f"Unexpected token: {{")
                case CSSTokenType.PROPERTY:
                    if not current_property:
                        raise CSSParserError(f"Expected property type before ':'.")
                    
                    parsed_properties[current_property].append(property_token.token_value)
                    parsed_properties[current_property].append(":")
                case CSSTokenType.COLON:
                    if not current_property:
                        raise CSSParserError(f"Expected property type before ':'.")
                case CSSTokenType.VALUE:
                    if not current_property:
                        raise CSSParserError(f"Expected property type before property value '{property_token.token_value}'.")

                    parsed_properties[current_property].append(property_token.token_value)
                case CSSTokenType.SEMICOLON:
                    if not current_property:
                        raise CSSParserError(f"Unexpected token: ';'")

                    parsed_properties[current_property].append(";")
                case CSSTokenType.RBRACE:
                    current_property = None
                
            continue

        match token_type:
            case CSSTokenType.PROPERTY:
                if current_property:
                    raise CSSParserError(f"Expected ';' before property '{property_token.token_value}' value.")
                
                create_property(property_token.token_value)
            case CSSTokenType.COLON:
                if not current_property:
                    raise CSSParserError(f"Expected property type before ':'.")
            case CSSTokenType.VALUE:
                if not current_property:
                    raise CSSParserError(f"Expected property type before property value '{property_token.token_value}'.")
                
                parsed_properties[current_property] = property_token.token_value
            case CSSTokenType.SEMICOLON:
                if not current_property:
                    raise CSSParserError(f"Unexpected token: ';'")
                
                current_property = None
    
    return parsed_properties

def create_properties(selector_groups: list[dict]) -> list[dict]:
    parsed_selector_groups: list[dict] = []

    for group in selector_groups:
        group["properties"] = parse_group_properties(group)

        parsed_selector_groups.append(group)
    
    return parsed_selector_groups

def create_selector_groups(tokens: tuple[CSSToken]) -> list[dict]:
    selector_groups: list[dict] = []
    current_selector_group: dict | None = None

    indent: int = 0

    def create_selector_group(selector: str) -> dict:
        nonlocal selector_groups, current_selector_group

        group: dict = {
            "selector": selector,
            "properties": []
        }

        selector_groups.append(group)

        return group

    def get_selector_group(selector: str) -> dict | None:
        nonlocal selector_groups

        for group in selector_groups:
            if not group["selector"] == selector:
                continue

            return group
        
        return None

    def new_selector_group(selector: str) -> None:
        nonlocal current_selector_group

        group: dict | None = get_selector_group(selector)

        if not group:
            group = create_selector_group(selector)
        
        current_selector_group = group

    for token in tokens:
        token_type: CSSTokenType = token.token_type

        match token_type:
            case CSSTokenType.NAME:
                if current_selector_group:
                    selector: str = current_selector_group["selector"]

                    raise CSSParserError(f"Missing '}}' for selector '{selector}'.")

                new_selector_group(token.token_value)
            case CSSTokenType.LBRACE:
                if not current_selector_group:
                    raise CSSParserError(f"Expected selector before '{{'.")
                
                if indent > 0:
                    current_selector_group["properties"].append(token)

                indent += 1
            case CSSTokenType.RBRACE:
                if not current_selector_group:
                    raise CSSParserError(f"Unexpected token: '}}'")

                indent -= 1

                if indent == 0:
                    current_selector_group = None
                else:
                    current_selector_group["properties"].append(token)
            case CSSTokenType.ANIMATION_NAME:
                if current_selector_group:
                    selector: str = current_selector_group["selector"]

                    raise CSSParserError(f"Missing '}}' for selector '{selector}'.")

                new_selector_group(token.token_value)
            case _:
                if not current_selector_group:
                    raise CSSParserError(f"Can not write property '{token.token_value}' outside of a selector.")
                
                current_selector_group["properties"].append(token)
    
    return selector_groups