from __future__ import annotations
from enum import Enum, auto

class CSSTokenType(Enum):
    NAME = auto()
    PROPERTY = auto()
    VALUE = auto()
    LBRACE = auto()
    RBRACE = auto()
    COLON = auto()
    SEMICOLON = auto()

class CSSToken:
    def __init__(self, token_type: CSSTokenType, token_value: str) -> CSSToken:
        self.token_type = token_type
        self.token_value = token_value

        self._fix_value_spaces_left()
        self._fix_value_spaces_right()

    def _fix_value_spaces_left(self) -> None:
        index: int = 0

        while index < len(self.token_value):
            char: str = self.token_value[index]

            if char == " ":
                index += 1

                continue
            
            self.token_value = self.token_value[index:]

            break
    
    def _fix_value_spaces_right(self) -> None:
        index: int = len(self.token_value) - 1

        while index >= 0:
            char: str = self.token_value[index]

            if char == " ":
                index -= 1

                continue

            self.token_value = self.token_value[:index + 1]

            break
    
    def __str__(self) -> str:
        return f"CSSToken: type: {self.token_type}; value: {self.token_value}"
    
    def __repr__(self) -> str:
        return f"{self.token_type.name}"