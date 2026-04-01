from __future__ import annotations
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.cache.cache import get_font
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
    
    def get_height(self) -> int:
        if not self.rect:
            return 0
        
        return self.rect.height

    def get_width(self) -> int:
        if not self.rect:
            return 0
        
        return self.rect.width

    def __get_font_family(self, font_family: str) -> str:
        if font_family.startswith("url("):
            font_path: str = font_family[5:len(font_family) - 2]

            return "*" + font_path

        return font_family

    def set_style(self, ui_render_object: UIRenderObject, classes: list[str], _id: str, type: str, modifiers: dict) -> dict:
        if not ui_render_object:
            return {}

        if not ui_render_object.style_sheet:
            return {}

        self.style = ui_render_object.style_sheet.get_style(type, classes, _id, modifiers)

        self.color = self.style["color"]
        self.font_size = self.style["font-size"]
        self.font_weight = self.style["font-weight"]
        self.font_style = self.style["font-style"]

        is_bold: bool = self.font_weight >= 600
        is_italic: bool = self.font_style == "italic"

        self.font = get_font(self.__get_font_family(self.style.get("font-family")), self.font_size, is_bold, is_italic)

        return self.style

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, padding: tuple[int, int, int, int], margin: tuple[int, int, int, int], offset: tuple[int, int, int, int], outerPosition: tuple[int, int]) -> None:
        if not self.font:
            self.font = ui_render_object.font

        self.surface = self.font.render(self.text, True, self.color)

        if len(self.color) > 3:
            self.surface.set_alpha(self.color[3])

        self.rect = self.surface.get_rect()

        self.rect.x = outerPosition[0] + padding[3]
        self.rect.y = outerPosition[1] + padding[0]

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