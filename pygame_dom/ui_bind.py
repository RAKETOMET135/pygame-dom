from __future__ import annotations
from typing import Any
from pygame_dom.cache.registry import add_bind, update_bind_elements
from pygame_dom.ui_element import UIElement

class UIBind:
    def __init__(self, name: str) -> UIBind:
        self._name = name
        self._value = None

        add_bind(self)
    
    def set(self, value: Any) -> None:
        self._value = value

        update_bind_elements(self)

    @property
    def value(self) -> Any | None:
        return self._value
    
    @property
    def name(self) -> str:
        return self._name