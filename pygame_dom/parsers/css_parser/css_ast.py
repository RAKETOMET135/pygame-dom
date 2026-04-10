from __future__ import annotations
from enum import Enum, auto

class ASTValueType(Enum):
    COLOR = auto()
    UNIT = auto()
    NAME = auto()
    NAME_STRING = auto()
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
    
    def __str__(self) -> str:
        return f"ASTValue: {self.datatype.name}, {self.value}"

    def __repr__(self) -> str:
        return self.__str__()

class ASTProperty:
    def __init__(self, name: str, value: ASTValue) -> ASTProperty:
        self.name = name
        self.value = value
    
    def __str__(self) -> str:
        return f"ASTProperty: {self.name}, {self.value}"

    def __repr__(self) -> str:
        return self.__str__()

class ASTRule:
    def __init__(self, selector: str, properties: list[ASTProperty]) -> ASTRule:
        self.selector = selector
        self.properties = properties
    
    def __str__(self) -> str:
        return f"ASTRule: {self.selector}, {self.properties}"

    def __repr__(self) -> str:
        return self.__str__()

class ASTStyleSheet:
    def __init__(self, rules: list[ASTRule]) -> ASTStyleSheet:
        self.rules = rules
    
    def __str__(self) -> str:
        output: str = ""

        for rule in self.rules:
            output += "\033[1;32m" + rule.selector + "\033[0m\n"
        
            for _property in rule.properties:
                output += "\033[31m> " + _property.name + "\033[0m\n"
    
                output += "\033[3;35m  > " + _property.value.datatype.name + "\033[0m\n"
                output += "\033[3m  > " + str(_property.value.value) + "\033[0m\n"

        return output
    
    def __repr__(self) -> str:
        return self.__str__()