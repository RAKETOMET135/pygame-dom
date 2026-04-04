from __future__ import annotations
from typing import Any
from pygame_dom.cache.registry import add_state, get_state, state_update
from pygame_dom.ui_element import UIElement
from pygame_dom.logic.state_eval import safe_eval_wrapper, get_variables

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

class UIStateExpr:
    def __init__(self, expr: str, involved_states: list[str]) -> UIStateExpr:
        self.expr = expr
        self.involved_states = involved_states

        self.result = None
    
    def is_state_involved(self, state_name: str) -> bool:
        return state_name in self.involved_states

    def exec_expr(self) -> Any:
        self.result = safe_eval_wrapper(self.expr, self.involved_states)

        return self.result

class UIStateObject:
    def __init__(self, ui_element: UIElement, raw_text: str, object_type: str) -> UIStateObject:
        self.ui_element = ui_element
        self.raw_text = raw_text
        self.involved_states = []

        self.segments = []
        self.result = None

        self._on_helper = ""

        self.__check_type(object_type)
        self.__parse_raw_text()
    
    def apply_result(self) -> None:
        if not self.result:
            return

        match self.object_type:
            case "text":
                self.ui_element.set_text(self.result)
            case "attr.src":
                self.ui_element.attrs["src"] = self.result

                if self.ui_element.element and hasattr(self.ui_element.element, "set_image_path"):
                    self.ui_element.element.set_image_path(self.result)
            case "attr.on":
                self.ui_element.attrs[self._on_helper] = self.result

    def __check_type(self, object_type: str) -> None:
        if object_type.startswith("attr.on"):
            self._on_helper = object_type[5:]

            object_type = "attr.on"

        self.object_type = object_type

    def __insert_states(self, states: list[str]) -> None:
        for state in states:
            if state in self.involved_states:
                continue

            self.involved_states.append(state)

    def __parse_raw_text(self) -> None:
        self.segments = []

        segment_text: str = ""
        is_segment_expr: bool = False
        segment_indent: int = 0

        for char in self.raw_text:
            if char == "{":
                if is_segment_expr:
                    segment_indent += 1

                    continue

                if len(segment_text) > 0:
                    self.segments.append(segment_text)

                    segment_text = ""
                
                is_segment_expr = True

                continue
            elif char == "}" and is_segment_expr:
                if segment_indent > 0:
                    segment_indent -= 1

                    continue

                if len(segment_text) > 0:
                    used_states: list[str] = get_variables(segment_text)

                    self.segments.append(UIStateExpr(segment_text, used_states))

                    self.__insert_states(used_states)

                    segment_text = ""

                is_segment_expr = False

                continue

            segment_text += char
        
        if len(segment_text) > 0:
            self.segments.append(segment_text)

    def is_state_involved(self, state_name: str) -> bool:
        return state_name in self.involved_states

    def build(self, changed_state_name: str) -> None:
        final_text: str = ""

        for segment in self.segments:
            if isinstance(segment, str):
                final_text += segment

                continue
            
            if not segment.is_state_involved(changed_state_name):
                final_text += str(segment.result)

                continue

            final_text += str(segment.exec_expr())

        self.result = final_text

        self.apply_result()
    
    def init_build(self) -> None:
        final_text: str = ""

        for segment in self.segments:
            if isinstance(segment, str):
                final_text += segment

                continue

            final_text += str(segment.exec_expr())
        
        self.result = final_text

        self.apply_result()

class UIStateInstance:
    def __init__(self, start: int, end: int, name: str) -> UIStateInstance:
        self.start = start
        self.end = end
        self.name = name

class UIStateParser:
    def __init__(self) -> UIStateParser:
        self.modern_states = []

        self.states = []
        self.attr_states = []

    def detect_state(self, ui_element: UIElement, raw_text: str, state_type: str) -> None:
        if raw_text.count("{") < 1 or raw_text.count("}") < 1:
            return
        
        state: UIStateObject = UIStateObject(ui_element, raw_text, state_type)

        self.modern_states.append(state)


    def render_all_states(self) -> None:
        for state in self.modern_states:
            state.init_build()


        for state in self.states:
            self.render_state(state)
        
        for attr_state in self.attr_states:
            self.render_attr_state(attr_state)

    def on_state_created_by_user(self, state_name: str) -> None:
        for state in self.modern_states:
            if not state.is_state_involved(state_name):
                continue

            state.build(state_name)


        for state in self.states:
            has_state: bool = False

            for ui_state_instance in state[1]:
                if not ui_state_instance.name == state_name:
                    continue

                has_state = True

                break

            if has_state:
                self.render_state(state)
        
        for attr_state in self.attr_states:
            has_state: bool = False

            for ui_state_instance in attr_state[1]:
                if not ui_state_instance.name == state_name:
                    continue

                has_state = True

                break

            if has_state:
                self.render_attr_state(attr_state)

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
    
    def render_attr_state(self, state: list) -> None:
        ui_element: UIElement = state[0]
        ui_state_instances: list[UIStateInstance] = state[1]
        ui_text: str = state[2]
        ui_attr_name: str = state[3]

        i: int = 0

        new_text: str = ""

        is_state: bool = False

        for letter in ui_text:
            if letter == "{":
                is_state = True

                ui_state_instance: UIStateInstance = ui_state_instances[i]

                state_value: Any = get_state(ui_state_instance.name)  # <--- interaction with registry
                #state_value = ""

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

        ui_element.attrs[ui_attr_name] = new_text

        if ui_attr_name == "src" and ui_element.element and hasattr(ui_element.element, "set_image_path"):
            ui_element.element.set_image_path(new_text)

    def parse_text(self, text: str, ui_element: UIElement) -> None:
        if ui_element.type == "input":
            return

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
    
    def parse_attr(self, text: str, ui_element: UIElement, attr: str) -> None:
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

        self.attr_states.append((ui_element, element_states, text, attr))