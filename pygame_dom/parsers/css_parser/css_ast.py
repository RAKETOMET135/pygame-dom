from __future__ import annotations
from typing import Any
from enum import Enum, auto

class ASTValueType(Enum):
    COLOR = auto()
    UNIT = auto()
    NAME = auto()
    VAR = auto()
    URL = auto()
    EXPR = auto()
    
    GROUP = auto()

class ASTValueInstance:
    pass

class ASTValue:
    def __init__(self, datatype: ASTValueType, value: ASTValueInstance) -> ASTValue:
        self.datatype = datatype
        self.value = value

class ASTProperty:
    def __init__(self, name: str, value: ASTValue) -> ASTProperty:
        self.name = name
        self.value = value

class ASTRule:
    def __init__(self, selector: str, properties: list[ASTProperty]) -> ASTRule:
        self.selector = selector
        self.properties = properties

class ASTStyleSheet:
    def __init__(self, rules: list[ASTRule]) -> ASTStyleSheet:
        self.rules = rules