from __future__ import annotations
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.cache.cache import get_image
from pygame_dom.data.transitions import handle_transition
import pygame

class ImageElement:
    def __init__(self, path: str) -> ImageElement:
        self.path = path
        self.surface = None
        self.rect = None

        self.style = None
        self.width = -1
        self.height = -1
        self._width = -1
        self._height = -1
        self.scale = 1
        self.parent_scale = 1

        self.style_stamp = None
        self.time = 0
        self.delay_dict = {}
        self.start_dict = {}

        self.inline_style_raw = ""
        self.inline_style = {}
        self.inline_style_parsed = False
        self.reactive_inline_style = {}
    
    def set_image_path(self, path: str) -> None:
        if self.path == path:
            return
        
        self.path = path
        self.width = -1
        self.height = -1

    def get_height(self) -> int:
        if not self.rect:
            return 0
        
        return int(self.rect.height / (self.scale * self.parent_scale))
    
    def get_width(self) -> int:
        if not self.rect:
            return 0
        
        return int(self.rect.width / (self.scale * self.parent_scale))
    
    def set_style(self, ui_render_object: UIRenderObject, classes: list[str], _id: str, _type: str, modifiers: dict) -> dict:
        if not ui_render_object:
            return {}

        if not ui_render_object.style_sheet:
            return {}

        # Styles (main + inline)
        self.style = ui_render_object.style_sheet.get_style(_type, classes, _id, modifiers)

        if not self.inline_style_parsed:
            self.inline_style_parsed = True

            self.inline_style = ui_render_object.style_sheet.parse_inline_style(self.inline_style_raw, self.root)

        ui_render_object.style_sheet.parse_reactive_inline_style(self.reactive_inline_style, self.inline_style)

        ui_render_object.style_sheet.overwrite_main_style(self.style, self.inline_style)
        #

        self.transition = self.style.get("transition", {})

        if not self.style_stamp:
            self.style_stamp = self.style
        else:
            handle_transition(self.style, self.style_stamp, self.delay_dict, self.time, self.start_dict)

        width: int = self.style_stamp.get("width")
        height: int = self.style_stamp.get("height")

        self.scale = self.style_stamp.get("scale", 1)

        if width and height:
            self.width = width
            self.height = height
        elif width:
            ratio: float = width / self._width

            self.width = width
            self.height = self._height * ratio
        elif height:
            ratio: float = height / self._height

            self.height = height
            self.width = self._width * ratio
        else:
            self.width = self._width
            self.height = self._height

        self.rect = pygame.rect.Rect(0, 0, round(self.width * self.scale), round(self.height * self.scale))

        self.time = pygame.time.get_ticks()

        return self.style_stamp
    
    def __get_init_size(self) -> tuple[int, int]:
        init_image: pygame.Surface

        try:
            init_image = pygame.image.load(self.path)
        except:
            return

        self.rect = init_image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self._width = self.width
        self._height = self.height

    def pre_render_image(self, parent_scale: float) -> None:
        self.surface = get_image(self.path, int(self.width), int(self.height))

        if not self.surface:
            return

        self.parent_scale = parent_scale

        self.rect = self.surface.get_rect()

        self.surface = pygame.transform.smoothscale(self.surface, (round(self.rect.width * self.scale * parent_scale), round(self.rect.height * self.scale * parent_scale)))

        self.rect = self.surface.get_rect()

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, padding: tuple[int, int, int, int], margin: tuple[int, int, int, int], offset: tuple[int, int, int, int], outerPosition: tuple[int, int, int, int]) -> None:
        if self.width < 0 or self.height < 0:
            self.__get_init_size()

        if not self.surface:
            return

        self.rect = self.surface.get_rect()

        self.rect.x = outerPosition[0] + round((outerPosition[2] - self.rect.width) / 2)
        self.rect.y = outerPosition[1] + round((outerPosition[3] - self.rect.height) / 2)

        if ui_render_object.overflow_surface:
            local_overflow_surface: pygame.Surface = pygame.Surface(ui_render_object.overflow_surface, pygame.SRCALPHA)

            local_overflow_surface.blit(
                self.surface,
                (
                    self.rect[0] - ui_render_object.overflow_surface_x,
                    self.rect[1] - ui_render_object.overflow_surface_y,
                    self.rect[2],
                    self.rect[3]
                )
            )

            screen.blit(local_overflow_surface, (ui_render_object.overflow_surface_x, ui_render_object.overflow_surface_y))
        else:
            screen.blit(self.surface, self.rect)

class IMG(ImageElement):
    def __init__(self, path: str) -> IMG:
        super().__init__(path)