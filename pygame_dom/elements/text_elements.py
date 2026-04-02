from __future__ import annotations
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.cache.cache import get_font
from pygame_dom.data.transitions import handle_transition
import pygame

class TextElement:
    def __init__(self, text: set) -> TextElement:
        self.text = text
        self.surface = None
        self.rect = None

        self.style = None
        self.color = (255, 255, 255, 255)
        self.font = None
        self.font_size = 0
        self.font_weight = 400
        self.font_style = "normal"
        self.scale = 1

        self.style_stamp = None
        self.time = 0
        self.delay_dict = {}
        self.start_dict = {}
    
    def get_height(self) -> int:
        if not self.rect:
            return 0
        
        return int(self.rect.height / self.scale)

    def get_width(self) -> int:
        if not self.rect:
            return 0
        
        return int(self.rect.width / self.scale)

    def __get_font_family(self, font_family: str) -> str:
        if font_family.startswith("url("):
            font_path: str = font_family[5:len(font_family) - 2]

            return "*" + font_path

        return font_family

    def set_style(self, ui_render_object: UIRenderObject, classes: list[str], _id: str, _type: str, modifiers: dict) -> dict:
        if not ui_render_object:
            return {}

        if not ui_render_object.style_sheet:
            return {}

        self.style = ui_render_object.style_sheet.get_style(_type, classes, _id, modifiers)
        self.transition = self.style.get("transition", {})

        if not self.style_stamp:
            self.style_stamp = self.style
        else:
            handle_transition(self.style, self.style_stamp, self.delay_dict, self.time, self.start_dict)

        self.scale = self.style_stamp.get("scale", 1)

        self.color = self.style_stamp["color"]
        self.font_size = self.style_stamp["font-size"]
        self.font_weight = self.style_stamp["font-weight"]
        self.font_style = self.style_stamp["font-style"]

        is_bold: bool = self.font_weight >= 600
        is_italic: bool = self.font_style == "italic"

        self.font = get_font(self.__get_font_family(self.style_stamp.get("font-family")), self.font_size, is_bold, is_italic)

        self.time = pygame.time.get_ticks()

        return self.style_stamp
    
    def pre_render_font(self, ui_render_object: UIRenderObject) -> None:
        if not self.font:
            self.font = ui_render_object.font

        color: tuple = tuple(int(c) for c in self.color)

        self.surface = self.font.render(self.text, True, color)

        if len(self.color) > 3:
            self.surface.set_alpha(self.color[3])
        
        self.rect = self.surface.get_rect()

        self.surface = pygame.transform.smoothscale(self.surface, (int(self.rect.width * self.scale), int(self.rect.height * self.scale)))

        self.rect = self.surface.get_rect()

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, padding: tuple[int, int, int, int], margin: tuple[int, int, int, int], offset: tuple[int, int, int, int], outerPosition: tuple[int, int, int, int]) -> None:
        if not self.surface:
            return

        self.rect.x = outerPosition[0] + int((outerPosition[2] - self.rect.width) / 2)
        self.rect.y = outerPosition[1] + int((outerPosition[3] - self.rect.height) / 2)

        #self.rect.x = outerPosition[0] + padding[3] * self.scale + int((self.rect.x * self.scale - self.rect.x) / 2)
        #self.rect.y = outerPosition[1] + padding[0] * self.scale + int((self.rect.y * self.scale - self.rect.y) / 2)

        screen.blit(self.surface, self.rect)

class H1(TextElement):
    def __init__(self, text: str) -> H1:
        super().__init__(text)

class H2(TextElement):
    def __init__(self, text: str) -> H2:
        super().__init__(text)

class H3(TextElement):
    def __init__(self, text: str) -> H3:
        super().__init__(text)

class H4(TextElement):
    def __init__(self, text: str) -> H4:
        super().__init__(text)

class H5(TextElement):
    def __init__(self, text: str) -> H5:
        super().__init__(text)

class H6(TextElement):
    def __init__(self, text: str) -> H6:
        super().__init__(text)

class P(TextElement):
    def __init__(self, text: str) -> P:
        super().__init__(text)

class DIV(TextElement):
    def __init__(self, text: str) -> DIV:
        super().__init__(text)

class BUTTON(TextElement):
    def __init__(self, text: str) -> BUTTON:
        super().__init__(text)