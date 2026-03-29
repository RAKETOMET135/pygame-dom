from __future__ import annotations
from typing import Any
from pygame_dom.cache.registry import add_state, get_state, state_update
from pygame_dom.ui_element import UIElement

class UIState:
    def __init__(self, name: str, value: Any) -> UIState:
        self._name = name
        self._value = value

        add_state(self)
    
    @property
    def value(self) -> Any:
        return self._value
    
    @value.setter
    def value(self, value: Any) -> None:
        self._value = value

        state_update(self.name)
    
    @property
    def name(self) -> str:
        return self._name

class UIStateInstance:
    def __init__(self, start: int, end: int, name: str) -> UIStateInstance:
        self.start = start
        self.end = end
        self.name = name

class UIStateParser:
    def __init__(self) -> UIStateParser:
        self.states = []

    def render_all_states(self) -> None:
        for state in self.states:
            self.render_state(state)

    def on_state_created_by_user(self, state_name: str) -> None:
        for state in self.states:
            has_state: bool = False

            for ui_state_instance in state[1]:
                if not ui_state_instance.name == state_name:
                    continue

                has_state = True

                break

            if has_state:
                self.render_state(state)

    def render_state(self, state: list) -> None:
        ui_element: UIElement = state[0]
        ui_state_instances: list[UIStateInstance] = state[1]
        ui_text: str = state[2]

        i: int = 0

        new_text: str = ""

        is_state: bool = False

        for letter in ui_text:
            if letter == "{":
                is_state = True

                ui_state_instance: UIStateInstance = ui_state_instances[i]

                state_value: Any = get_state(ui_state_instance.name)

                if state_value:
                    new_text += str(state_value.value)

                i += 1

                continue
            
            if letter == "}":
                is_state = False

                continue

            if is_state:
                continue
            
            new_text += letter

        ui_element.set_text(new_text)

    def parse_text(self, text: str, ui_element: UIElement) -> None:
        element_states: list[UIStateInstance] = []

        is_state: bool = False

        c_state_start: int = -1
        c_state_end: int = -1
        c_state_name: str = ""

        i: int = -1

        for letter in text:
            i += 1

            if letter == "{":
                is_state = True

                c_state_start = i

                continue
            
            if not is_state:
                continue

            if letter == "}":
                is_state = False

                c_state_end = i

                state: UIStateInstance = UIStateInstance(c_state_start, c_state_end, c_state_name)

                element_states.append(state)

                c_state_start = -1
                c_state_end = -1
                c_state_name = ""

                continue

            c_state_name += letter

        self.states.append((ui_element, element_states, text))