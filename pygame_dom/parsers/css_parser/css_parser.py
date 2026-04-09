from pygame_dom.parsers.css_parser.css_ast import ASTValue, ASTProperty, ASTRule, ASTStyleSheet, ASTValueType
from pygame_dom.parsers.css_parser.css_tokenizer import CSSToken, CSSTokenType
from typing import Any

class ParserError(Exception):
    pass

def parse_css_tokens(tokens: tuple[CSSToken]) -> ASTStyleSheet:
    selector_groups: list[dict] = create_selector_groups(tokens)
    selector_groups = create_properties(selector_groups)

    print(selector_groups)

def create_ast_value(value: str) -> ASTValue:
    pass

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

    def create_property(property_name: str) -> None:
        nonlocal parsed_properties, current_property

        if not property_name in parsed_properties:
            parsed_properties[property_name] = None
        
        current_property = property_name

    for property_token in group["properties"]:
        token_type: CSSTokenType = property_token.token_type

        match token_type:
            case CSSTokenType.PROPERTY:
                if current_property:
                    raise ParserError(f"Expected ';' after property '{property_token.token_value}' value.")
                
                create_property(property_token.token_value)
            case CSSTokenType.COLON:
                if not current_property:
                    raise ParserError(f"Expected property type before ':'.")
            case CSSTokenType.VALUE:
                if not current_property:
                    raise ParserError(f"Expected property type before property value '{property_token.token_value}'.")
                
                parsed_properties[current_property] = property_token.token_value
            case CSSTokenType.SEMICOLON:
                if not current_property:
                    raise ParserError(f"Unexpected token: ';'")
                
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

                    raise ParserError(f"Missing '}}' for selector '{selector}'.")

                new_selector_group(token.token_value)
            case CSSTokenType.LBRACE:
                if not current_selector_group:
                    raise ParserError(f"Expected selector before '{{'.")
            case CSSTokenType.RBRACE:
                if not current_selector_group:
                    raise ParserError(f"Unexpected token: '}}'")

                current_selector_group = None
            case _:
                if not current_selector_group:
                    raise ParserError(f"Can not write property '{token.token_value}' outside of a selector.")
                
                current_selector_group["properties"].append(token)
    
    return selector_groups