from __future__ import annotations
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.cache.cache import get_image
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
    
    def set_image_path(self, path: str) -> None:
        if self.path == path:
            return
        
        self.path = path
        self.width = -1
        self.height = -1

    def get_height(self) -> int:
        if not self.rect:
            return 0
        
        return self.rect.height
    
    def get_width(self) -> int:
        if not self.rect:
            return 0
        
        return self.rect.width
    
    def set_style(self, ui_render_object: UIRenderObject, classes: list[str], _id: str, type: str) -> dict:
        if not ui_render_object:
            return {}

        if not ui_render_object.style_sheet:
            return {}

        self.style = ui_render_object.style_sheet.get_style(type, classes, _id)

        width: int = self.style.get("width")
        height: int = self.style.get("height")

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

        return self.style
    
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

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, padding: tuple[int, int, int, int], margin: tuple[int, int, int, int], offset: tuple[int, int, int, int], outerPosition: tuple[int, int]) -> None:
        if self.width < 0 or self.height < 0:
            self.__get_init_size()
        
        self.surface = get_image(self.path, self.width, self.height)

        if not self.surface:
            return
        
        self.rect = self.surface.get_rect()

        self.rect.x = outerPosition[0] + padding[3]
        self.rect.y = outerPosition[1] + padding[0]

        screen.blit(self.surface, self.rect)

class IMG(ImageElement):
    def __init__(self, path: str) -> IMG:
        super().__init__(path)