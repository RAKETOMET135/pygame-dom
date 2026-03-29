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
        
        if not self.element.text:
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

    def __get_padding(self, style: dict) -> tuple[int, int, int, int]:
        return (style.get("padding-top", 0), style.get("padding-right", 0), style.get("padding-bottom", 0), style.get("padding-left", 0))

    def __get_margin(self, style: dict) -> tuple[int, int, int, int]:
        return (style.get("margin-top", 0), style.get("margin-right", 0), style.get("margin-bottom", 0), style.get("margin-left", 0))

    def __get_border_radius(self, style: dict) -> tuple[int, int, int, int]:
        return (style.get("border-top-left-radius", 0), style.get("border-top-right-radius", 0), style.get("border-bottom-left-radius", 0), style.get("border-bottom-right-radius", 0))

    def __get_offset(self, style: dict, position: str) -> tuple[int, int, int, int]:
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

        if offset[0] >= 0 and offset[0] >= margin[3]:
            x_position += offset[0] - margin[3]
        elif offset[2] >= 0:
            if offset[2] < margin[1]:
                x_position = width - (element_width + margin[1] + padding[1] + padding[3])
            else:
                x_position = width - (element_width + padding[1] + offset[2] + padding[3])
        
        return x_position

    def __calc_y_position(
        self, ui_render_object: UIRenderObject, margin: tuple[int, int, int, int], padding: tuple[int, int, int, int], offset: tuple[int, int, int, int],
        screen_rect: pygame.Rect, element_height: int
    ) -> int:
        y_position: int = ui_render_object.render_y + margin[0]

        height: int = ui_render_object.height

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

        if offset[1] >= 0 and offset[1] >= margin[0]:
            y_position += offset[1] - margin[0]
        elif offset[3] >= 0:
            if offset[3] < margin[2]:
                y_position = height - (element_height + margin[2] + padding[2] + padding[0])
            else:
                y_position = height - (element_height + padding[2] + offset[3] + padding[0])

        return y_position

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, children_data: dict = {}) -> None:
        if not self.element:
            return

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

        self.ui_render_object_stamp.render_zindex = ui_render_object.render_zindex

        screen_rect: pygame.Rect = screen.get_rect()

        # Handle zindex like event interaction
        self.latest_render_zindex = ui_render_object.render_zindex

        ui_render_object.render_zindex += 1

        # Get style
        style: dict = self.element.set_style(ui_render_object, self.classes, self.id, self.type)
        padding: tuple[int, int, int, int] = self.__get_padding(style)
        margin: tuple[int, int, int, int] = self.__get_margin(style)
        border_radius: tuple[int, int, int, int] = self.__get_border_radius(style)
        self.position = style.get("position", "static")
        offset: tuple[int, int, int, int] = self.__get_offset(style, self.position)
        size: tuple[int, int] = self.__get_size(style)
        display: str = style.get("display", "block")

        if display == "block":
            self.display = Display.BLOCK
        elif display == "inline":
            self.display = Display.INLINE
        elif display == "flex":
            self.display = Display.FLEX
        
        # Set element to new line
        if self.display == Display.BLOCK or self.display == Display.FLEX:
            ui_render_object.render_line += 1
            ui_render_object.render_x = 0
            ui_render_object.render_y += ui_render_object.render_line_height
            ui_render_object.render_line_height = 0

        # Get element size
        element_width: int = self.element.get_width()
        element_height: int = self.element.get_height()

        if size[0] > 0:
            element_width = size[0]
        
        if size[1] > 0:
            element_height = size[1]

        # Update elements using flex data
        flex_vertical_stretch: bool = children_data.get("vertical_stretch", False)

        if flex_vertical_stretch:
            element_height = children_data.get("vertical_stretch_size", 0)

        flex_position_x: int = children_data.get("render_x", -1)
        
        # Get element position
        position_x: int = self.__calc_x_position(ui_render_object, margin, padding, offset, screen_rect, element_width)
        position_y: int = self.__calc_y_position(ui_render_object, margin, padding, offset, screen_rect, element_height)

        # Update position for flex elements
        if flex_position_x >= 0:
            position_x = flex_position_x
            
            children_data["render_x"] += element_width

        # Update data for sub element rendering
        self.rendered_x = position_x
        self.rendered_y = position_y
        self.rendered_size_x = element_width
        self.rendered_size_y = element_height
        self.actual_size_x = element_width + padding[1] + padding[3]
        self.actual_size_y = element_height + padding[0] + padding[2]

        self.ui_render_object_stamp.render_x = position_x
        self.ui_render_object_stamp.render_y = position_y
        self.ui_render_object_stamp.width = element_width
        self.ui_render_object_stamp.height = element_height

        # Render background for element
        if style["background-color"]:
            rect: tuple[int, int, int, int] = (
                position_x,
                position_y,
                element_width + padding[1] + padding[3],
                element_height + padding[0] + padding[2]
            )

            pygame.draw.rect(
                screen, 
                style["background-color"], 
                rect, 
                border_top_left_radius=border_radius[0], 
                border_top_right_radius=border_radius[1],
                border_bottom_left_radius=border_radius[2],
                border_bottom_right_radius=border_radius[3]
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

        self.element.draw(screen, ui_render_object, padding, margin, offset, (position_x, position_y))

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

        # Render sub elements
        for child in self.children:
            child.draw(screen, self.ui_render_object_stamp, children_data)

        ui_render_object.render_zindex += self.ui_render_object_stamp.render_zindex

        if self.position == "absolute":
            return

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