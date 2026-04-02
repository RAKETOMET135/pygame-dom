from __future__ import annotations
from typing import Any
from enum import Enum, auto
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.ui_event import UIEvent
from pygame_dom.cache.registry import exec_function
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

        self.display = Display.BLOCK
        self.position = "static"
        self.rendered_x = 0
        self.rendered_y = 0
        self.rendered_size_x = 0
        self.rendered_size_y = 0
        self.actual_size_x = 0
        self.actual_size_y = 0
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

    def __get_padding(self, style: dict, screen: pygame.Surface) -> tuple[int, int, int, int]:
        pad_left: int | str = style.get("padding-left", 0)
        pad_right: int | str = style.get("padding-right", 0)
        pad_top: int | str = style.get("padding-top", 0)
        pad_bottom: int | str = style.get("padding-bottom", 0)

        width: int = 0
        height: int = 0

        if self.parent:
            width = self.parent.get_rendered_size_x()
            height = self.parent.get_rendered_size_y()

        if width <= 0:
            width = screen.get_width()
        
        if height <= 0:
            height = screen.get_height()

        if isinstance(pad_left, str) and pad_left.endswith("%"):
            pad_left = (width / 100) * float(pad_left[:len(pad_left) - 1])
        
        if isinstance(pad_right, str) and pad_right.endswith("%"):
            pad_right = (width / 100) * float(pad_right[:len(pad_right) - 1])

        if isinstance(pad_top, str) and pad_top.endswith("%"):
            pad_top = (height / 100) * float(pad_top[:len(pad_top) - 1])
        
        if isinstance(pad_bottom, str) and pad_bottom.endswith("%"):
            pad_bottom = (height / 100) * float(pad_bottom[:len(pad_bottom) - 1])

        return (pad_top, pad_right, pad_bottom, pad_left)

    def __get_margin(self, style: dict) -> tuple[int, int, int, int]:
        return (style.get("margin-top", 0), style.get("margin-right", 0), style.get("margin-bottom", 0), style.get("margin-left", 0))

    def __get_border_radius(self, style: dict) -> tuple[int, int, int, int]:
        return (style.get("border-top-left-radius", 0), style.get("border-top-right-radius", 0), style.get("border-bottom-left-radius", 0), style.get("border-bottom-right-radius", 0))

    def __get_offset(self, style: dict, position: str, scale: float) -> tuple[int, int, int, int]:
        if position == "static":
            return (-1, -1, -1, -1)

        return (style.get("left", -1), style.get("top", -1), style.get("right", -1), style.get("bottom", -1))

    def __get_size(self, style: dict) -> tuple[int, int]:
        return (style.get("width", 0), style.get("height", 0))

    def __calc_x_position(
        self, ui_render_object: UIRenderObject, margin: tuple[int, int, int, int], padding: tuple[int, int, int, int], offset: tuple[int, int, int, int],
        screen_rect: pygame.Rect, element_width: int
    ) -> int:
        x_position: int = ui_render_object.render_x + margin[3]

        width: int = ui_render_object.width
        left: int | str = offset[0]
        right: int | str = offset[2]

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

        if left >= 0 and left >= margin[3]:
            x_position += left - margin[3]
        elif right >= 0:
            if right < margin[1]:
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
        top: int | str = offset[1]
        bottom: int | str = offset[3]

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

        if top >= 0 and top >= margin[0]:
            y_position += top - margin[0]
        elif bottom >= 0:
            if bottom < margin[2]:
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

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, children_data: dict = {}) -> dict:
        if not self.element:
            return {}

        # Reset one frame variables
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
        style: dict = self.element.set_style(ui_render_object, self.classes, self.id, self.type, { "hover": self.is_hover, "active": self.is_active })
        padding: tuple[int, int, int, int] = self.__get_padding(style, screen)
        margin: tuple[int, int, int, int] = self.__get_margin(style)
        border_radius: tuple[int, int, int, int] = self.__get_border_radius(style)
        self.position = style.get("position", "static")

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
        if (self.display == Display.BLOCK or self.display == Display.FLEX):
            ui_render_object.render_line += 1
            ui_render_object.render_x = 0
            ui_render_object.render_y += ui_render_object.render_line_height
            ui_render_object.render_line_height = 0

            if self.parent:
                ui_render_object.render_x = self.parent.get_rendered_x()

        # Get element size
        element_width: int = self.element.get_width()
        element_height: int = self.element.get_height()

        # Width
        if isinstance(size[0], str) and size[0].endswith("%"):
            size_x: int = 0

            if self.parent:
                size_x = self.parent.get_rendered_size_x()

            if size_x <= 0:
                size_x = screen.get_width()
            
            size_x = (size_x / 100) * float(size[0][:len(size[0]) - 1])

            element_width = int(size_x)
        else:
            if size[0] > 0:
                element_width = size[0]
        
        # Height
        if isinstance(size[1], str) and size[1].endswith("%"):
            size_y: int = 0

            if self.parent:
                size_y = self.parent.get_rendered_size_y()
            
            if size_y <= 0:
                size_y = screen.get_height()
            
            size_y = (size_y / 100) * float(size[1][:len(size[1]) - 1])

            element_height = int(size_y)
        else:
            if size[1] > 0:
                element_height = size[1]

        # Update elements using flex data
        flex_vertical_stretch: bool = children_data.get("vertical_stretch", False)

        if flex_vertical_stretch:
            element_height = children_data.get("vertical_stretch_size", 0)

        flex_position_x: int = children_data.get("render_x", -1)
        
        # Setup padding groups
        pad_horizontal: int = padding[1] + padding[3]
        pad_vertical: int = padding[0] + padding[2]

        # Get element position
        translate_x: int | str = translate[0]

        if isinstance(translate_x, str):
            if translate_x.endswith("%"):
                translate_x = ((element_width + pad_horizontal) / 100) * float(translate_x[:len(translate_x) - 1])
            else:
                translate_x = 0
        
        translate_y: int | str = translate[1]

        if isinstance(translate_y, str):
            if translate_y.endswith("%"):
                translate_y = ((element_height + pad_vertical) / 100) * float(translate_y[:len(translate_y) - 1])
            else:
                translate_y = 0

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
        self.rendered_x = position_x
        self.rendered_y = position_y
        self.rendered_size_x = element_width
        self.rendered_size_y = element_height
        self.actual_size_x = int((element_width) * scale) + int(pad_horizontal * scale)
        self.actual_size_y = int((element_height) * scale) + int(pad_vertical * scale)

        self.ui_render_object_stamp.render_x = position_x
        self.ui_render_object_stamp.render_y = position_y
        self.ui_render_object_stamp.width = self.actual_size_x
        self.ui_render_object_stamp.height = self.actual_size_y
        self.ui_render_object_stamp.pad_horizontal = pad_horizontal
        self.ui_render_object_stamp.pad_vertical = pad_vertical

        # Render background for element
        if style["background-color"]:
            rect: tuple[int, int, int, int] = (
                int(position_x),
                int(position_y),
                self.actual_size_x,
                self.actual_size_y
            )

            color: tuple = tuple(int(c) for c in style.get("background-color", (0, 0, 0, 0)))

            pygame.draw.rect(
                screen, 
                color, 
                rect, 
                border_top_left_radius=int(border_radius[0]), 
                border_top_right_radius=int(border_radius[1]),
                border_bottom_left_radius=int(border_radius[2]),
                border_bottom_right_radius=int(border_radius[3])
            )

            #pygame.draw.rect(
            #    screen,
            #    (0, 0, 0, 0),
            #    rect,
            #    border_top_left_radius=border_radius[0], 
            #    border_top_right_radius=border_radius[1],
            #    border_bottom_left_radius=border_radius[2],
            #    border_bottom_right_radius=border_radius[3],
            #    width=0
            #)

        self.element.draw(screen, ui_render_object, padding, margin, offset, (position_x, position_y, self.actual_size_x, self.actual_size_y))

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
        for child in self.children:
            child.draw(screen, self.ui_render_object_stamp, children_data)

        ui_render_object.render_zindex += self.ui_render_object_stamp.render_zindex

        if self.position == "absolute":
            return { "hover": self.is_mouse_in }

        # Update data for displays
        match self.display:
            case Display.BLOCK | Display.FLEX:
                ui_render_object.render_line += 1
                ui_render_object.render_x = 0
                ui_render_object.render_y += ui_render_object.render_line_height + element_height + padding[0] + padding[2] + margin[0] + margin[2]
                ui_render_object.render_line_height = 0
            case Display.INLINE:
                ui_render_object.render_x += element_width + padding[1] + padding[3] + margin[1] + margin[3]

                if element_height + padding[0] + padding[2] + margin[0] + margin[2] > ui_render_object.render_line_height:
                    ui_render_object.render_line_height = element_height + padding[0] + padding[2] + margin[0] + margin[2]
        
        return { "hover": self.is_mouse_in }