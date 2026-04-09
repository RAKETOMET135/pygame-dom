from __future__ import annotations
from typing import Any

class Color:
    def __init__(self, r: float, g: float, b: float, a: float = 255) -> Color:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def get_value(self, use_float_format: bool = False) -> tuple[int, int, int, int] | tuple[float, float, float, float]:
        if use_float_format:
            return (self.r, self.g, self.b, self.a)
        
        return (int(self.r), int(self.g), int(self.b), int(self.a))

class Unit:
    def __init__(self, value: float, unit: str) -> Unit:
        self.value = value
        self.unit = unit

class Name:
    def __init__(self, name: str) -> Name:
        self.name = name

class Var:
    def __init__(self, link: str) -> Var:
        self.link = link

class Url:
    def __init__(self, link: str) -> Url:
        self.link = link

class Group:
    def __init__(self, content: list[Any], is_comma: bool) -> Group:
        self.content = content
        self.is_comma = is_comma