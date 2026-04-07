from __future__ import annotations
from typing import Any
from enum import Enum, auto
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.ui_event import UIEvent
from pygame_dom.cache.registry import exec_function, add_ui_element
import pygame

class Display(Enum):
    BLOCK = auto()
    INLINE = auto()
    FLEX = auto()

class UIElement:
    def __init__(self, element: Any, el_type: str, parent: UIElement | None) -> UIElement:
        self.element = element
        self.type = el_type
        self.parent = parent
        self.children = []

        self.binds = {}

        self.display = Display.BLOCK
        self.display_string = "block"
        self.position = "static"
        self.border_width = 0
        self.rendered_x = 0
        self.rendered_y = 0
        self.rendered_size_x = 0
        self.rendered_size_y = 0
        self.actual_size_x = 0
        self.actual_size_y = 0
        self.margin_size_x = 0
        self.margin_size_y = 0
        self.overflow_size_x = 0
        self.overflow_size_y = 0
        self.overflow_x = 0
        self.overflow_y = 0
        self.cursor = pygame.SYSTEM_CURSOR_ARROW
        self.custom_cursor = None

        self.classes = []
        self.id = ""
        self.attrs = {}

        self.ui_render_object_stamp = None

        self.latest_render_zindex = -1

        self.is_mouse_enter = False
        self.is_mouse_exit = False
        self.is_mouse_in = False
        self.is_click_held = False
        self.is_click_turn = False
        self.last_click_time = 0
        self.is_left_click_held = False
        self.is_right_click_held = False
        self.is_left_click_turn = False
        self.is_right_click_turn = False
        
        self.is_hover = False
        self.is_active = False

        self.scale = 1
        self.parent_scale = 1

        self.wants_focus = False
        self.wants_unfocus = False

        self.element.root = self

        add_ui_element(self)

    def on_bind_set(self, bind: Any, bind_type: str) -> None:
        if bind_type == "bind:checked":
            value: Any = bind.value

            if isinstance(value, bool) and hasattr(self.element, "active"):
                self.element.active = value
        elif bind_type == "bind:value":
            value: Any = bind.value

            if isinstance(value, str) and hasattr(self.element, "caret_position"):
                self.element.text = value
                self.element.caret_position = len(value)
                self.element.selection_start = self.element.caret_position
                self.element.selection_end = self.element.caret_position
        elif bind_type == "bind:focus":
            value: Any = bind.value

            if isinstance(value, bool) and hasattr(self.element, "focus"):
                if value:
                    self.wants_focus = True
                else:
                    self.wants_unfocus = True

    def on_event(self, event: UIEvent) -> None:
        for attr, value in self.attrs.items():
            if attr == f"on{event.event_type}":
                exec_function(value, event)
        
        if not event.propagation:
            return

        if self.parent:
            self.parent.on_event(event)
    
    def set_text(self, new_text: str) -> None:
        if not self.element:
            return

        if not hasattr(self.element, "text"):
            return

        self.element.text = new_text

    def set_classes(self, classes: list[str]) -> None:
        self.classes = classes
    
    def set_id(self, id: str) -> None:
        self.id = id

    def add_child(self, child: UIElement) -> None:
        self.children.append(child)

    def get_rendered_x(self) -> int:
        if self.parent and self.position == "static":
            return self.parent.get_rendered_x()
        
        if not self.parent and self.position == "static":
            return 0

        return self.rendered_x

    def get_rendered_size_x(self) -> int:
        if self.parent and self.position == "static":
            return self.parent.get_rendered_size_x()
        
        if not self.parent and self.position == "static":
            return 0
        
        return self.rendered_size_x

    def get_rendered_y(self) -> int:
        if self.parent and self.position == "static":
            return self.parent.get_rendered_y()
        
        if not self.parent and self.position == "static":
            return 0

        return self.rendered_y
    
    def get_rendered_size_y(self) -> int:
        if self.parent and self.position == "static":
            return self.parent.get_rendered_size_y()
        
        if not self.parent and self.position == "static":
            return 0
        
        return self.rendered_size_y

    def __get_relative_width(self, screen: pygame.Surface) -> int:
        if not self.parent:
            return screen.get_width()

        width: int = self.parent.get_rendered_size_x()

        if width <= 0:
            return screen.get_width()

        return width

    def __get_relative_height(self, screen: pygame.Surface) -> int:
        if not self.parent:
            return screen.get_height()
        
        height: int = self.parent.get_rendered_size_y()

        if height <= 0:
            return screen.get_height()
        
        return height

    def __get_percent(self, percenter: Any, full: int | float) -> int | float:
        if not isinstance(percenter, str):
            return percenter
        
        if not percenter.endswith("%"):
            return percenter
        
        return (full / 100) * float(percenter[:len(percenter) - 1])

    def __get_padding(self, style: dict, screen: pygame.Surface) -> tuple[int, int, int, int]:
        pad_left: int | str = style.get("padding-left", 0)
        pad_right: int | str = style.get("padding-right", 0)
        pad_top: int | str = style.get("padding-top", 0)
        pad_bottom: int | str = style.get("padding-bottom", 0)

        width: int = self.__get_relative_width(screen)
        height: int = self.__get_relative_height(screen)

        pad_left = self.__get_percent(pad_left, width) + self.border_width
        pad_right = self.__get_percent(pad_right, width) + self.border_width
        pad_top = self.__get_percent(pad_top, height) + self.border_width
        pad_bottom = self.__get_percent(pad_bottom, height) + self.border_width

        return (pad_top, pad_right, pad_bottom, pad_left)

    def __get_margin(self, style: dict, screen: pygame.Surface, position: str) -> tuple[int, int, int, int]:
        if position == "absolute":
            return (0, 0, 0, 0)

        mar_left: int | str = style.get("margin-left", 0)
        mar_right: int | str = style.get("margin-right", 0)
        mar_top: int | str = style.get("margin-top", 0)
        mar_bottom: int | str = style.get("margin-bottom", 0)

        width: int = self.__get_relative_width(screen)
        height: int = self.__get_relative_height(screen)

        mar_left = self.__get_percent(mar_left, width)
        mar_right = self.__get_percent(mar_right, width)
        mar_top = self.__get_percent(mar_top, height)
        mar_bottom = self.__get_percent(mar_bottom, height)

        return (mar_top, mar_right, mar_bottom, mar_left)

    def __get_border_radius(self, style: dict, screen: pygame.Surface) -> tuple[int, int, int, int]:
        br_top_left: int | str = style.get("border-top-left-radius", 0)
        br_top_right: int | str = style.get("border-top-right-radius", 0)
        br_bottom_left: int | str = style.get("border-bottom-left-radius", 0)
        br_bottom_right: int | str = style.get("border-bottom-right-radius", 0)

        width: int = self.__get_relative_width(screen)
        height: int = self.__get_relative_height(screen)

        br_top_left = self.__get_percent(br_top_left, (width + height) / 2)
        br_top_right = self.__get_percent(br_top_right, (width + height) / 2)
        br_bottom_left = self.__get_percent(br_bottom_left, (width + height) / 2)
        br_bottom_right = self.__get_percent(br_bottom_right, (width + height) / 2)
        
        return (br_top_left, br_top_right, br_bottom_left, br_bottom_right)

    def __get_offset(self, style: dict, position: str, scale: float) -> tuple[int, int, int, int]:
        if position == "static":
            return (None, None, None, None)

        return (style.get("left", None), style.get("top", None), style.get("right", None), style.get("bottom", None))

    def __get_size(self, style: dict) -> tuple[int, int]:
        return (style.get("width", 0), style.get("height", 0))

    def __calc_x_position(
        self, ui_render_object: UIRenderObject, margin: tuple[int, int, int, int], padding: tuple[int, int, int, int], offset: tuple[int, int, int, int],
        screen_rect: pygame.Rect, element_width: int
    ) -> int:
        x_position: int = ui_render_object.render_x + margin[3]

        width: int = ui_render_object.width
        left: int | str | None = offset[0]
        right: int | str | None = offset[2]

        if width <= 0:
            width = screen_rect.width
        else:
            width += ui_render_object.render_x

        if self.position == "absolute":
            if self.parent:
                x_position = self.parent.get_rendered_x()
                width = self.parent.get_rendered_size_x()

                if width <= 0:
                    width = screen_rect.width
                else:
                    width += x_position
            else:
                x_position = 0
                width = screen_rect.width

        if isinstance(left, str) and left.endswith("%"):
            left = float(left[:len(left) - 1])

            width -= x_position
            left = (width / 100) * left
            width += x_position

        if isinstance(right, str) and right.endswith("%"):
            right = float(right[:len(right) - 1])

            width -= x_position
            right = (width / 100) * right
            width += x_position

        if (left or left == 0) and left < 0:
            x_position += left
        elif (left or left == 0) and left >= margin[3]:
            x_position += left - margin[3]
        elif (right or right == 0):
            if right < 0:
                x_position = width - (element_width + padding[1] + right + padding[3])
            elif right < margin[1]:
                x_position = width - (element_width + margin[1] + padding[1] + padding[3])
            else:
                x_position = width - (element_width + padding[1] + right + padding[3])
        
        return x_position

    def __calc_y_position(
        self, ui_render_object: UIRenderObject, margin: tuple[int, int, int, int], padding: tuple[int, int, int, int], offset: tuple[int, int, int, int],
        screen_rect: pygame.Rect, element_height: int
    ) -> int:
        y_position: int = ui_render_object.render_y + margin[0]

        height: int = ui_render_object.height
        top: int | str | None = offset[1]
        bottom: int | str | None = offset[3]

        if height <= 0:
            height = screen_rect.height
        else:
            height += ui_render_object.render_y

        if self.position == "absolute":
            if self.parent:
                y_position = self.parent.get_rendered_y()
                height = self.parent.get_rendered_size_y()

                if height <= 0:
                    height = screen_rect.height
                else:
                    height += y_position
            else:
                y_position = 0
                height = screen_rect.height

        if isinstance(top, str) and top.endswith("%"):
            top = float(top[:len(top) - 1])

            height -= y_position
            top = (height / 100) * top
            height += y_position

        if isinstance(bottom, str) and bottom.endswith("%"):
            bottom = float(bottom[:len(bottom) - 1])

            height -= y_position
            bottom = (height / 100) * bottom
            height += y_position

        if (top or top == 0) and top < 0:
            y_position += top
        elif (top or top == 0) and top >= margin[0]:
            y_position += top - margin[0]
        elif (bottom or bottom == 0):
            if bottom < 0:
                y_position = height - (element_height + padding[2] + bottom + padding[0])
            elif bottom < margin[2]:
                y_position = height - (element_height + margin[2] + padding[2] + padding[0])
            else:
                y_position = height - (element_height + padding[2] + bottom + padding[0])

        return y_position

    def __parse_cursor(self, cursor: str) -> None:
        system_cursor_id: int | None = None

        match cursor:
            case "default":
                system_cursor_id = pygame.SYSTEM_CURSOR_ARROW
            case "pointer":
                system_cursor_id = pygame.SYSTEM_CURSOR_HAND
            case "text":
                system_cursor_id = pygame.SYSTEM_CURSOR_IBEAM
            case "wait":
                system_cursor_id = pygame.SYSTEM_CURSOR_WAIT
            case "crosshair":
                system_cursor_id = pygame.SYSTEM_CURSOR_CROSSHAIR
            case "move":
                system_cursor_id = pygame.SYSTEM_CURSOR_SIZEALL
        
        if not system_cursor_id and not system_cursor_id == 0:
            self.custom_cursor = cursor[5:len(cursor) - 2]

            return
        
        self.cursor = system_cursor_id

    def __calc_modern_text_dynamic_size(self, element_width: int, element_height: int, setted_width: int, setted_height: int) -> tuple[int, int]:
        calced_list: list = []
        line_m_text_widths: list = []
        current_line: int = 0

        _i: int = 0
        for i in range(len(self.element.modern_text) + len(self.children)):
            m_text: tuple[int, str] | None = self.element.get_modern_text(i)

            if m_text:
                calced_list.append(m_text)

                _i += 1
            else:
                child: UIElement = self.children[i - _i]

                if child.position == "absolute":
                    continue

                calced_list.append(child)

        if setted_width <= 0:
            element_width = 0
            
        if setted_height <= 0:
            element_height = 0

        for i, el in enumerate(calced_list):
            if not isinstance(el, tuple):
                if el.position == "absolute":
                    continue

                if el.display_string == "block":
                    if i == 0:
                        line_m_text_widths.append(0)

                        current_line += 1

                        continue

                    line_m_text_widths.append(0)
                    line_m_text_widths.append(0)

                    current_line += 2
                elif el.display_string == "inline":
                    if current_line >= len(line_m_text_widths):
                        line_m_text_widths.append(0)

                continue

            m_size: tuple[int, int] = self.element.get_modern_size(el[1])

            if i <= 0:
                if setted_width <= 0:
                    element_width = m_size[0]
                    
                if setted_height <= 0:
                    element_height = m_size[1]
                
                line_m_text_widths.append(element_width)

                continue

            prev_m_text: tuple[int, str] | None = calced_list[i - 1]

            if isinstance(prev_m_text, tuple):
                if setted_width <= 0:
                    element_width += m_size[0]
                    
                if setted_height <= 0 and element_height < m_size[1]:
                    element_height += m_size[1]
            else:
                child: UIElement = calced_list[i - 1]

                if child.display_string == "block":
                    if setted_width <= 0 and m_size[0] > element_width:
                        element_width = m_size[0]
                        
                    if setted_height <= 0:
                        special_case: bool = False

                        if not (i + 1 > len(calced_list) -1):
                            next_element: tuple[int, str] | UIElement = calced_list[i + 1]

                            if isinstance(next_element, UIElement) and next_element.display_string == "inline":
                                special_case = True

                        if not special_case:
                            element_height += m_size[1]
                elif child.display_string == "inline":
                    if setted_height <= 0 and m_size[1] > element_height:
                        element_height = m_size[1]
                        
                    if setted_width <= 0:
                        element_width += m_size[0]
            
            if current_line >= len(line_m_text_widths):
                line_m_text_widths.append(0)

            line_m_text_widths[current_line] += m_size[0]

        return element_width, element_height, line_m_text_widths

    def __calc_dynamic_size(self, element_width: int, element_height: int, setted_width: int, setted_height: int) -> tuple[int, int]:
        line_m_text_widths: list = []

        if hasattr(self.element, "modern_text") and len(self.element.modern_text) > 0:
            element_width, element_height, line_m_text_widths = self.__calc_modern_text_dynamic_size(element_width, element_height, setted_width, setted_height)

        inline_width: int = 0
        max_inline_width: int = 0

        inline_height_used: bool = False

        current_line: int = 0

        for i, child in enumerate(self.children):
            if child.position == "absolute":
                continue

            if setted_width <= 0:
                if child.display_string == "block":
                    if element_width < child.margin_size_x:
                        element_width = child.margin_size_x
                    
                    current_line += 1

                    if i > 0:
                        current_line += 1

                    if len(line_m_text_widths) > 0:
                        inline_width = line_m_text_widths[current_line]
                    else:
                        inline_width = 0
                elif child.display_string == "inline":
                    inline_width += child.margin_size_x

                    if inline_width > max_inline_width:
                        max_inline_width = inline_width

            if setted_height <= 0:
                if child.display_string == "block":
                    element_height += child.margin_size_y

                    inline_height_used = True
                elif child.display_string == "inline":
                    if inline_height_used:
                        inline_height_used = False

                        element_height += child.margin_size_y
        
        if setted_width <= 0 and max_inline_width > element_width:
            element_width = max_inline_width
        
        return element_width, element_height

    def __calc_width(self, screen: pygame.Surface, size: tuple, setted_width: int, element_width: int) -> tuple[int, int]:
        if isinstance(size[0], str) and size[0].endswith("%"):
            size_x: int = 0

            if self.parent:
                size_x = self.parent.get_rendered_size_x()

            if size_x <= 0:
                size_x = screen.get_width()

            size_x = (size_x / 100) * float(size[0][:len(size[0]) - 1])

            element_width = int(size_x)

            setted_width = size_x
        else:
            if size[0] > 0:
                element_width = size[0]

                setted_width = size[0]
        
        return element_width, setted_width

    def __calc_height(self, screen: pygame.Surface, size: tuple, setted_height: int, element_height: int) -> tuple[int, int]:
        if isinstance(size[1], str) and size[1].endswith("%"):
            size_y: int = 0

            if self.parent:
                size_y = self.parent.get_rendered_size_y()

            if size_y <= 0:
                size_y = screen.get_height()
            
            size_y = (size_y / 100) * float(size[1][:len(size[1]) - 1])

            setted_height = size_y

            element_height = int(size_y)
        else:
            if size[1] > 0:
                element_height = size[1]

                setted_height = size[1]
        
        return element_height, setted_height

    def __calc_element_size(self, screen: pygame.Surface, size: tuple[int, int]) -> tuple[int, int]:
        element_width: int = self.element.get_width()
        element_height: int = self.element.get_height()

        setted_width: int = 0
        setted_height: int = 0

        element_width, setted_width = self.__calc_width(screen, size, setted_width, element_width)
        element_height, setted_height = self.__calc_height(screen, size, setted_height, element_height)
        
        element_width, element_height = self.__calc_dynamic_size(element_width, element_height, setted_width, setted_height)

        return element_width, element_height

    def __calc_translate(self, translate: tuple, element_width: int, element_height: int, pad_horizontal: int, pad_vertical: int) -> tuple[int, int]:
        translate_x: int | str = 0

        if translate:
            translate_x = translate[0]

        if isinstance(translate_x, str):
            if translate_x.endswith("%"):
                translate_x = ((element_width + pad_horizontal) / 100) * float(translate_x[:len(translate_x) - 1])
            else:
                translate_x = 0
        
        translate_y: int | str = 0

        if translate:
            translate_y = translate[1]

        if isinstance(translate_y, str):
            if translate_y.endswith("%"):
                translate_y = ((element_height + pad_vertical) / 100) * float(translate_y[:len(translate_y) - 1])
            else:
                translate_y = 0
        
        return translate_x, translate_y

    def __handle_element_event_parameters(self) -> None:
        self.is_mouse_enter = False
        self.is_mouse_exit = False

        if self.is_click_turn:
            self.is_click_turn = False
            self.is_click_held = False
            self.last_click_time = pygame.time.get_ticks()
        
        if self.is_left_click_turn:
            self.is_left_click_turn = False
            self.is_left_click_held = False
        
        if self.is_right_click_turn:
            self.is_right_click_turn = False
            self.is_right_click_held = False

    def __render_sub_elements(self, screen: pygame.Surface, children_data: dict, text_align: str, ui_render_object: UIRenderObject) -> None:
        def_render_x: int = self.ui_render_object_stamp.def_render_x
        render_x: int = self.ui_render_object_stamp.render_x

        def align_text(render_line_index: int) -> None:
            if text_align == "right":
                self.ui_render_object_stamp.def_render_x = def_render_x + self.rendered_size_x - line_widths[render_line_index]
                self.ui_render_object_stamp.render_x = render_x + self.rendered_size_x - line_widths[render_line_index]
            elif text_align == "center":
                self.ui_render_object_stamp.def_render_x = def_render_x + (self.rendered_size_x - line_widths[render_line_index]) / 2
                self.ui_render_object_stamp.render_x = render_x + (self.rendered_size_x - line_widths[render_line_index]) / 2

        child_elements: int = len(self.children)
        line_widths: list[int] = []

        if hasattr(self.element, "modern_text") and len(self.element.modern_text) > 0:
            child_elements += len(self.element.modern_text)

            # Calculate the children width on lines
            current_line_width: int = 0
            modern_text_nodes_passed: int = 0

            for i in range(child_elements):
                m_text: tuple[int, str] | None = self.element.get_modern_text(i)

                if m_text:
                    modern_text_nodes_passed += 1

                    current_line_width += self.element.get_modern_size(m_text[1])[0]
                else:
                    child: UIElement = self.children[i - modern_text_nodes_passed]

                    if child.position == "absolute":
                        continue

                    if child.display_string == "inline":
                        current_line_width += child.margin_size_x
                    elif child.display_string == "block":
                        if current_line_width > 0:
                            line_widths.append(current_line_width)

                        current_line_width = child.margin_size_x

                        line_widths.append(current_line_width)

                        current_line_width = 0
            
            if current_line_width > 0:
                line_widths.append(current_line_width)

        modern_text_nodes: list = []
        modern_text_nodes_rendered: int = 0

        prev_line_render: int = -1
        prev_is_block: bool = False

        for i in range(child_elements):
            if len(line_widths) > 0 and not prev_line_render == self.ui_render_object_stamp.render_line:
                prev_line_render = self.ui_render_object_stamp.render_line

                align_text(self.ui_render_object_stamp.render_line)

            if hasattr(self.element, "get_modern_text"):
                m_text: tuple[int, str] | None = self.element.get_modern_text(i)

                if m_text:
                    if prev_is_block:
                        prev_is_block = False

                        if len(line_widths) > 0 and not prev_line_render == self.ui_render_object_stamp.render_line + 1:
                            prev_line_render = self.ui_render_object_stamp.render_line + 1
                
                        align_text(self.ui_render_object_stamp.render_line + 1)

                    modern_text_nodes_rendered += 1

                    m_text_size: tuple[int, int] = self.element.get_modern_size(m_text[1])

                    modern_text_nodes.append((i, (self.ui_render_object_stamp.render_x, self.ui_render_object_stamp.render_y, m_text_size[0], m_text_size[1])))

                    self.ui_render_object_stamp.render_x += m_text_size[0]

                    if self.ui_render_object_stamp.render_line_height < m_text_size[1]:
                        self.ui_render_object_stamp.render_line_height = m_text_size[1]

                    continue

            child_index: int = i - modern_text_nodes_rendered

            child_node: UIElement = self.children[child_index]

            if child_node.display_string == "block" and not child_node.position == "absolute":
                prev_is_block = True

                if len(line_widths) > 0 and not prev_line_render == self.ui_render_object_stamp.render_line + 1:
                    prev_line_render = self.ui_render_object_stamp.render_line + 1

                align_text(self.ui_render_object_stamp.render_line + 1)
            elif prev_is_block and child_node.display_string == "inline" and not child_node.position == "absolute":
                prev_is_block = False

                if len(line_widths) > 0 and not prev_line_render == self.ui_render_object_stamp.render_line + 1:
                    prev_line_render = self.ui_render_object_stamp.render_line
                
                align_text(self.ui_render_object_stamp.render_line + 1)

            child_node.draw(screen, self.ui_render_object_stamp, children_data)
        
        # Render modern text
        for modern_text_node in modern_text_nodes:
            self.element.draw_modern_text(screen, modern_text_node[0], modern_text_node[1], ui_render_object)

    def __calc_overflow_size(self, position_x: int, position_y: int, ui_render_object: UIRenderObject) -> None:
        if not ui_render_object.overflow_surface or not self.parent:
            self.overflow_size_x = self.actual_size_x
            self.overflow_size_y = self.actual_size_y
            self.overflow_x = self.rendered_x
            self.overflow_y = self.rendered_y

            return

        new_width: int = 0
        new_height: int = 0
        new_x: int = 0
        new_y: int = 0

        point_1: tuple[int, int] = (ui_render_object.overflow_surface_x, ui_render_object.overflow_surface_y)
        point_2: tuple[int, int] = (ui_render_object.overflow_surface_x + ui_render_object.overflow_surface[0], ui_render_object.overflow_surface_y + ui_render_object.overflow_surface[1])

        point_3: tuple[int, int] = (position_x, position_y)
        point_4: tuple[int, int] = (position_x + self.actual_size_x, position_y + self.actual_size_y)

        condition_1: tuple[bool, bool] = (point_3[0] >= point_1[0] and point_3[0] <= point_2[0], point_3[1] >= point_1[1] and point_3[1] <= point_2[1])
        condition_2: tuple[bool, bool] = (point_4[0] >= point_1[0] and point_4[0] <= point_2[0], point_4[1] >= point_1[1] and point_4[1] <= point_2[1])

        if condition_1[0] and condition_2[0]:
            new_width = self.actual_size_x
            new_x = position_x
        elif condition_1[0]:
            new_width = abs(point_2[0] - point_3[0])
            new_x = position_x
        elif condition_2[0]:
            new_width = abs(point_1[0] - point_4[0])
            new_x = position_x + abs(point_1[0] - point_3[0])
        elif point_3[0] < point_1[0] and point_4[0] > point_2[0]:
            new_width = abs(point_1[0] - point_2[0])
            new_x = position_x + abs(point_1[0] - point_3[0])

        if condition_1[1] and condition_2[1]:
            new_height = self.actual_size_y
            new_y = position_y
        elif condition_1[1]:
            new_height = abs(point_2[1] - point_3[1])
            new_y = position_y
        elif condition_2[1]:
            new_height = abs(point_1[1] - point_4[1])
            new_y = position_y + abs(point_1[1] - point_3[1])
        elif point_3[1] < point_1[1] and point_4[1] > point_2[1]:
            new_height = abs(point_1[1] - point_2[1])
            new_y = position_y + abs(point_1[1] - point_3[1])
        
        self.overflow_size_x = new_width
        self.overflow_size_y = new_height
        self.overflow_x = new_x
        self.overflow_y = new_y

    def __merge_overflows(
            self, point_1: tuple[int, int], point_2: tuple[int, int], point_3: tuple[int, int], point_4: tuple[int, int], position_x: int, position_y: int
        ) -> tuple[int, int, int, int]:
        new_width: int = 0
        new_height: int = 0
        new_x: int = 0
        new_y: int = 0

        condition_1: tuple[bool, bool] = (point_3[0] >= point_1[0] and point_3[0] <= point_2[0], point_3[1] >= point_1[1] and point_3[1] <= point_2[1])
        condition_2: tuple[bool, bool] = (point_4[0] >= point_1[0] and point_4[0] <= point_2[0], point_4[1] >= point_1[1] and point_4[1] <= point_2[1])

        if condition_1[0] and condition_2[0]:
            new_width = self.actual_size_x
            new_x = position_x
        elif condition_1[0]:
            new_width = abs(point_2[0] - point_3[0])
            new_x = position_x
        elif condition_2[0]:
            new_width = abs(point_1[0] - point_4[0])
            new_x = position_x + abs(point_1[0] - point_3[0])
        elif point_3[0] < point_1[0] and point_4[0] > point_2[0]:
            new_width = abs(point_1[0] - point_2[0])
            new_x = position_x + abs(point_1[0] - point_3[0])

        if condition_1[1] and condition_2[1]:
            new_height = self.actual_size_y
            new_y = position_y
        elif condition_1[1]:
            new_height = abs(point_2[1] - point_3[1])
            new_y = position_y
        elif condition_2[1]:
            new_height = abs(point_1[1] - point_4[1])
            new_y = position_y + abs(point_1[1] - point_3[1])
        elif point_3[1] < point_1[1] and point_4[1] > point_2[1]:
            new_height = abs(point_1[1] - point_2[1])
            new_y = position_y + abs(point_1[1] - point_3[1]) - 1
        
        self.ui_render_object_stamp.overflow_surface = (new_width, new_height)
        self.ui_render_object_stamp.overflow_surface_x = new_x
        self.ui_render_object_stamp.overflow_surface_y = new_y

    def __calc_overflows(self, screen: pygame.Surface, position_x: int, position_y: int, ui_render_object: UIRenderObject, overflow_x: str, overflow_y: str) -> None:
        if ui_render_object.overflow_surface:
            self.ui_render_object_stamp.overflow_surface = ui_render_object.overflow_surface
            self.ui_render_object_stamp.overflow_surface_x = ui_render_object.overflow_surface_x
            self.ui_render_object_stamp.overflow_surface_y = ui_render_object.overflow_surface_y

        if overflow_x == "visible" and overflow_y == "visible":
            return

        point_1: tuple[int, int] = (0, 0)
        point_2: tuple[int, int] = (0, 0)

        if ui_render_object.overflow_surface:
            point_1 = (ui_render_object.overflow_surface_x, ui_render_object.overflow_surface_y)
            point_2 = (ui_render_object.overflow_surface_x + ui_render_object.overflow_surface[0], ui_render_object.overflow_surface_y + ui_render_object.overflow_surface[1])

        if overflow_x == "hidden" and overflow_y == "hidden":
            if ui_render_object.overflow_surface:
                point_3: tuple[int, int] = (position_x, position_y)
                point_4: tuple[int, int] = (position_x + self.actual_size_x, position_y + self.actual_size_y)
                
                self.__merge_overflows(point_1, point_2, point_3, point_4, position_x, position_y)
            else:
                self.ui_render_object_stamp.overflow_surface = (self.actual_size_x, self.actual_size_y)
                self.ui_render_object_stamp.overflow_surface_x = position_x
                self.ui_render_object_stamp.overflow_surface_y = position_y
        elif overflow_x == "hidden":
            if ui_render_object.overflow_surface:
                point_3: tuple[int, int] = (position_x, -1)
                point_4: tuple[int, int] = (position_x + self.actual_size_x, screen.get_height() + 1)

                self.__merge_overflows(point_1, point_2, point_3, point_4, position_x, position_y)
            else:
                self.ui_render_object_stamp.overflow_surface = (self.actual_size_x, screen.get_height() + 2)
                self.ui_render_object_stamp.overflow_surface_x = position_x
                self.ui_render_object_stamp.overflow_surface_y = -1
        elif overflow_y == "hidden":
            if ui_render_object.overflow_surface:
                point_3: tuple[int, int] = (-1, position_y)
                point_4: tuple[int, int] = (screen.get_width() + 1, position_y + self.actual_size_y)

                self.__merge_overflows(point_1, point_2, point_3, point_4, position_x, position_y)
            else:
                self.ui_render_object_stamp.overflow_surface = (screen.get_width() + 2, self.actual_size_y)
                self.ui_render_object_stamp.overflow_surface_x = -1
                self.ui_render_object_stamp.overflow_surface_y = position_y

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, children_data: dict = {}) -> dict:
        if not self.element:
            return {}

        # Reset one frame variables
        self.__handle_element_event_parameters()

        # Create data for sub elements
        if self.ui_render_object_stamp:
            self.ui_render_object_stamp.reset()
        else:
            self.ui_render_object_stamp = ui_render_object.create_stamp()

        self.ui_render_object_stamp.render_zindex = ui_render_object.render_zindex + 1

        screen_rect: pygame.Rect = screen.get_rect()

        # Handle zindex like event interaction
        self.latest_render_zindex = ui_render_object.render_zindex

        ui_render_object.render_zindex += 1

        # Get style
        is_focused: bool = False

        if hasattr(self.element, "focus"):
            is_focused = self.element.focus

        style: dict = self.element.set_style(ui_render_object, self.classes, self.id, self.type, { "hover": self.is_hover, "active": self.is_active, "focus": is_focused })
        self.position = style.get("position", "static")
        self.border_width = style.get("border-width", 0)
        border_color: tuple = style.get("border-color", None)
        outline_width: int = style.get("outline-width", 0)
        outline_color: tuple = style.get("outline-color", (0, 0, 0, 0))

        text_align: str = style.get("text-align", "left")

        padding: tuple[int, int, int, int] = self.__get_padding(style, screen)
        margin: tuple[int, int, int, int] = self.__get_margin(style, screen, self.position)
        border_radius: tuple[int, int, int, int] = self.__get_border_radius(style, screen)

        parent_scale: float = children_data.get("scale", 1)
        scale: float = style.get("scale", 1) * parent_scale

        self.scale = scale
        self.parent_scale = parent_scale

        offset: tuple[int, int, int, int] = self.__get_offset(style, self.position, scale)
        size: tuple[int, int] = self.__get_size(style)
        display: str = style.get("display", "block")
        visibility: str = style.get("visibility", "visible")
        translate: tuple[int | str, int | str] = style.get("translate")

        if hasattr(self.element, "pre_render_font"):
            self.element.pre_render_font(ui_render_object, parent_scale)
        
        if hasattr(self.element, "pre_render_image"):
            self.element.pre_render_image(parent_scale)

        self.display_string = display

        if display == "none" or visibility == "hidden":
            return {}

        if self.is_mouse_in:
            self.__parse_cursor(style.get("cursor", "default"))

        if display == "block":
            self.display = Display.BLOCK
        elif display == "inline":
            self.display = Display.INLINE
        elif display == "flex":
            self.display = Display.FLEX
        
        # Set element to new line
        if (self.display == Display.BLOCK or self.display == Display.FLEX) and not self.position == "absolute":
            ui_render_object.render_line += 1
            ui_render_object.render_x = ui_render_object.def_render_x
            ui_render_object.render_y += ui_render_object.render_line_height
            ui_render_object.render_line_height = 0

            if self.parent:
                #ui_render_object.render_x = self.parent.get_rendered_x()
                pass

        # Get element size
        element_width, element_height = self.__calc_element_size(screen, size)

        # Check if render background (checkbox and radio dont have bakground)
        render_background: bool = True

        bg: tuple[int, int, int, int] | None = style.get("background-color", None)

        if hasattr(self.element, "input_type") and self.element.input_type in ["radio", "checkbox"]:
            render_background = False

            # Make default height for the inputs
            if element_width < 20:
                element_width = 20
            
            if element_height < 20:
                element_height = 20

        # Update elements using flex data
        flex_vertical_stretch: bool = children_data.get("vertical_stretch", False)

        if flex_vertical_stretch:
            element_height = children_data.get("vertical_stretch_size", 0)

        flex_position_x: int = children_data.get("render_x", -1)
        
        # Setup padding groups
        pad_horizontal: int = padding[1] + padding[3]
        pad_vertical: int = padding[0] + padding[2]

        # Setup margin groups
        mar_horizontal: int = margin[1] + margin[3]
        mar_vertical: int = margin[0] + margin[2]

        # Get element position
        translate_x, translate_y = self.__calc_translate(translate, element_width, element_height, pad_horizontal, pad_vertical)

        position_x: int = self.__calc_x_position(ui_render_object, margin, padding, offset, screen_rect, element_width) + translate_x
        position_y: int = self.__calc_y_position(ui_render_object, margin, padding, offset, screen_rect, element_height) + translate_y

        # Change element position to make scale center
        position_x -= int((element_width * (scale / parent_scale) - element_width) / 2) + int((pad_horizontal * (scale / parent_scale) - pad_horizontal) / 2)
        position_y -= int((element_height * (scale / parent_scale) - element_height) / 2) + int((pad_vertical * (scale / parent_scale) - pad_vertical) / 2)

        # Update position for flex elements
        if flex_position_x >= 0:
            position_x = flex_position_x
            
            children_data["render_x"] += element_width

        # Update data for sub element rendering
        outer_position: tuple[int, int, int, int] = (
            position_x,
            position_y,
            self.actual_size_x,
            self.actual_size_y
        )

        self.rendered_x = position_x
        self.rendered_y = position_y
        self.rendered_size_x = element_width
        self.rendered_size_y = element_height
        self.actual_size_x = int((element_width) * scale) + int(pad_horizontal * scale)
        self.actual_size_y = int((element_height) * scale) + int(pad_vertical * scale)
        self.margin_size_x = self.actual_size_x + int(mar_horizontal * scale)
        self.margin_size_y = self.actual_size_y + int(mar_vertical * scale)

        self.ui_render_object_stamp.render_x = position_x + padding[3] * (scale / parent_scale)
        self.ui_render_object_stamp.render_y = position_y + padding[0] * (scale / parent_scale)
        self.ui_render_object_stamp.width = self.actual_size_x
        self.ui_render_object_stamp.height = self.actual_size_y
        self.ui_render_object_stamp.pad_horizontal = pad_horizontal
        self.ui_render_object_stamp.pad_vertical = pad_vertical
        self.ui_render_object_stamp.def_render_x = self.ui_render_object_stamp.render_x

        # Create an overflow surface if overflow: hidden
        overflow_x: str = style.get("overflow-x", "visible")
        overflow_y: str = style.get("overflow-y", "visible")

        self.__calc_overflow_size(position_x, position_y, ui_render_object)
        self.__calc_overflows(screen, position_x, position_y, ui_render_object, overflow_x, overflow_y)

        if hasattr(self.element, "text") and hasattr(self.element, "get_text_position") and len(self.element.modern_text) <= 0:
            text_position: tuple[int, int] = self.element.get_text_position(outer_position, padding)

            self.ui_render_object_stamp.render_x = text_position[0] + self.element.get_width()
            self.ui_render_object_stamp.render_line_height = self.element.get_height()

        # Create rect for rendering background, border and outline
        rect: tuple[int, int, int, int] = (
            int(position_x),
            int(position_y),
            self.actual_size_x,
            self.actual_size_y
        )

        # Prepare local overflow surface for rendering if needed
        local_overflow_surface: pygame.Surface | None = None

        # Render background for element
        if bg and render_background:
            color: tuple = tuple(int(c) for c in style.get("background-color", (0, 0, 0, 0)))

            if ui_render_object.overflow_surface:
                if ui_render_object.overflow_surface[0] <= 0 or ui_render_object.overflow_surface[1] <= 0:
                    pass

                local_overflow_surface = pygame.Surface(ui_render_object.overflow_surface, pygame.SRCALPHA)

                pygame.draw.rect(
                    local_overflow_surface, 
                    color, 
                    (rect[0] - ui_render_object.overflow_surface_x, rect[1] - ui_render_object.overflow_surface_y, rect[2], rect[3]), 
                    border_top_left_radius=int(border_radius[0]), 
                    border_top_right_radius=int(border_radius[1]),
                    border_bottom_left_radius=int(border_radius[2]),
                    border_bottom_right_radius=int(border_radius[3])
                )
            else:
                pygame.draw.rect(
                    screen, 
                    color, 
                    rect, 
                    border_top_left_radius=int(border_radius[0]), 
                    border_top_right_radius=int(border_radius[1]),
                    border_bottom_left_radius=int(border_radius[2]),
                    border_bottom_right_radius=int(border_radius[3])
                )

        # Render border and outline
        if ui_render_object.overflow_surface and render_background:
            if ui_render_object.overflow_surface[0] <= 0 or ui_render_object.overflow_surface[1] <= 0:
                if self.border_width > 0 and border_color:
                    pygame.draw.rect(
                        local_overflow_surface,
                        border_color,
                        (
                            rect[0] - ui_render_object.overflow_surface_x,
                            rect[1] - ui_render_object.overflow_surface_y,
                            rect[2],
                            rect[3]
                        ),
                        border_top_left_radius=border_radius[0], 
                        border_top_right_radius=border_radius[1],
                        border_bottom_left_radius=border_radius[2],
                        border_bottom_right_radius=border_radius[3],
                        width=self.border_width
                    )
                
                if outline_width > 0 and outline_color:
                    radius_1: int = outline_width if border_radius[0] > 0 else 0
                    radius_2: int = outline_width if border_radius[1] > 0 else 0
                    radius_3: int = outline_width if border_radius[2] > 0 else 0
                    radius_4: int = outline_width if border_radius[3] > 0 else 0

                    pygame.draw.rect(
                        local_overflow_surface,
                        outline_color,
                        (
                            rect[0] - outline_width - ui_render_object.overflow_surface_x,
                            rect[1] - outline_width - ui_render_object.overflow_surface_y,
                            rect[2] + 2 * outline_width,
                            rect[3] + 2 * outline_width
                        ),
                        border_top_left_radius=border_radius[0] + radius_1, 
                        border_top_right_radius=border_radius[1] + radius_2,
                        border_bottom_left_radius=border_radius[2] + radius_3,
                        border_bottom_right_radius=border_radius[3] + radius_4,
                        width=outline_width
                    )
                
                screen.blit(local_overflow_surface, (ui_render_object.overflow_surface_x, ui_render_object.overflow_surface_y))
        elif render_background:
            if self.border_width > 0 and border_color:
                pygame.draw.rect(
                    screen,
                    border_color,
                    (
                        rect[0],
                        rect[1],
                        rect[2],
                        rect[3]
                    ),
                    border_top_left_radius=border_radius[0], 
                    border_top_right_radius=border_radius[1],
                    border_bottom_left_radius=border_radius[2],
                    border_bottom_right_radius=border_radius[3],
                    width=self.border_width
                )
                
            if outline_width > 0 and outline_color:
                radius_1: int = outline_width if border_radius[0] > 0 else 0
                radius_2: int = outline_width if border_radius[1] > 0 else 0
                radius_3: int = outline_width if border_radius[2] > 0 else 0
                radius_4: int = outline_width if border_radius[3] > 0 else 0

                pygame.draw.rect(
                    screen,
                    outline_color,
                    (
                        rect[0] - outline_width,
                        rect[1] - outline_width,
                        rect[2] + 2 * outline_width,
                        rect[3] + 2 * outline_width
                    ),
                    border_top_left_radius=border_radius[0] + radius_1, 
                    border_top_right_radius=border_radius[1] + radius_2,
                    border_bottom_left_radius=border_radius[2] + radius_3,
                    border_bottom_right_radius=border_radius[3] + radius_4,
                    width=outline_width
                )

        if hasattr(self.element, "modern_text") and len(self.element.modern_text) > 0:
            pass
        else:
            if self.ui_render_object_stamp.overflow_surface:
                element_ui_render_object: UIRenderObject = ui_render_object.copy()

                element_ui_render_object.overflow_surface = self.ui_render_object_stamp.overflow_surface
                element_ui_render_object.overflow_surface_x = self.ui_render_object_stamp.overflow_surface_x
                element_ui_render_object.overflow_surface_y = self.ui_render_object_stamp.overflow_surface_y

                self.element.draw(screen, element_ui_render_object, padding, margin, offset, outer_position)
            else:
                self.element.draw(screen, ui_render_object, padding, margin, offset, outer_position)

        # Set data for flex children
        children_data: dict = {
            "vertical_stretch": False,
            "vertical_stretch_size": 0,
            "render_x": -1
        }

        if self.display == Display.FLEX:
            align_items: str = style.get("align-items", "stretch")

            if align_items == "stretch":
                children_data["vertical_stretch"] = True
                children_data["vertical_stretch_size"] = element_height
            
            children_data["render_x"] = position_x

        children_data["scale"] = scale

        # Render sub elements
        self.__render_sub_elements(screen, children_data, text_align, ui_render_object)

        # Add zindex from child elements
        ui_render_object.render_zindex += self.ui_render_object_stamp.render_zindex

        if self.position == "absolute":
            return { "hover": self.is_mouse_in }

        # Update data for displays
        match self.display:
            case Display.BLOCK | Display.FLEX:
                #ui_render_object.render_line += 1
                ui_render_object.render_x = ui_render_object.def_render_x
                ui_render_object.render_y += ui_render_object.render_line_height + element_height + padding[0] + padding[2] + margin[0] + margin[2]
                ui_render_object.render_line_height = 0
            case Display.INLINE:
                ui_render_object.render_x += element_width + padding[1] + padding[3] + margin[1] + margin[3]

                if element_height + padding[0] + padding[2] + margin[0] + margin[2] > ui_render_object.render_line_height:
                    ui_render_object.render_line_height = element_height + padding[0] + padding[2] + margin[0] + margin[2]
        
        return { "hover": self.is_mouse_in }