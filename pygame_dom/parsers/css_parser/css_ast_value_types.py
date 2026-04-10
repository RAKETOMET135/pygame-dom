from __future__ import annotations
from pygame_dom.parsers.css_parser.css_ast import ASTValueInstance
from typing import Any

class Color(ASTValueInstance):
    def __init__(self, r: float, g: float, b: float, a: float = 255.0) -> Color:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def get_value(self, use_float_format: bool = False) -> tuple[int, int, int, int] | tuple[float, float, float, float]:
        if use_float_format:
            return (self.r, self.g, self.b, self.a)
        
        return (int(self.r), int(self.g), int(self.b), int(self.a))
    
    def __str__(self) -> str:
        return f"Color: {self.r}, {self.g}, {self.b}, {self.a}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Unit(ASTValueInstance):
    def __init__(self, value: float, unit: str) -> Unit:
        self.value = value
        self.unit = unit

class Name(ASTValueInstance):
    def __init__(self, name: str) -> Name:
        self.name = name

class Var(ASTValueInstance):
    def __init__(self, link: str) -> Var:
        self.link = link

class Url(ASTValueInstance):
    def __init__(self, link: str) -> Url:
        self.link = link

class Expr(ASTValueInstance):
    def __init__(self, expr: str) -> Expr:
        self.expr = expr
    
    def __str__(self) -> str:
        return f"Expr: {self.expr}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Group(ASTValueInstance):
    def __init__(self, content: list[Any], is_comma: bool) -> Group:
        self.content = content
        self.is_comma = is_comma