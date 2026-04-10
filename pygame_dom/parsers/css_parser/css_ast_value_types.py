from __future__ import annotations
from pygame_dom.parsers.css_parser.css_ast import ASTValueInstance, ASTValue, ASTProperty

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
    
    def __str__(self) -> str:
        return f"Unit: {self.value}, {self.unit}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Name(ASTValueInstance):
    def __init__(self, name: str) -> Name:
        self.name = name
    
    def __str__(self) -> str:
        return f"Name: {self.name}"
    
    def __repr__(self) -> str:
        return self.__str__()

class NameString(ASTValueInstance):
    def __init__(self, name: str) -> NameString:
        self.name = name
    
    def __str__(self) -> str:
        return f"NameString: {self.name}"

    def __repr__(self) -> str:
        return self.__str__()

class Var(ASTValueInstance):
    def __init__(self, link: str) -> Var:
        self.link = link
    
    def __str__(self) -> str:
        return f"Var: {self.link}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Url(ASTValueInstance):
    def __init__(self, link: str) -> Url:
        self.link = link
    
    def __str__(self) -> str:
        return f"Url: {self.link}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Expr(ASTValueInstance):
    def __init__(self, expr: str) -> Expr:
        self.expr = expr
    
    def __str__(self) -> str:
        return f"Expr: {self.expr}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Group(ASTValueInstance):
    def __init__(self, content: list[ASTValue], is_comma: bool) -> Group:
        self.content = content
        self.is_comma = is_comma
    
    def __str__(self) -> str:
        output: str = "Group: ["

        for i, child in enumerate(self.content):
            if i > 0:
                output += "; "
            
            output += str(child)

        return output + "]"
    
    def __repr__(self) -> str:
        return self.__str__()

class AnimationKeyframe(ASTValueInstance):
    def __init__(self, content: list[ASTProperty]) -> AnimationKeyframe:
        self.content = content
    
    def __str__(self) -> str:
        return f"AnimationKeyframe: {self.content}"

    def __repr__(self) -> str:
        return self.__str__()