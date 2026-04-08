from typing import Any
import pygame
import copy

cache_fonts: dict = {}
cache_images: dict = {}
cache_styles: dict = {}

def get_font(name: str, size: int, bold: bool, italic: bool) -> pygame.font.Font:
    key: tuple[str, int, bool, bool] = (name, size, bold, italic)

    if not key in cache_fonts:
        if name.startswith("*"):
            cache_fonts[key] = pygame.font.Font(name[1:], size)
        else:
            cache_fonts[key] = pygame.font.SysFont(name, size, bold, italic)
    
    return cache_fonts[key]

def get_image(path: str, width: int, height: int) -> pygame.Surface | None:
    key: tuple[str, int, int] = (path, width, height)

    if not key in cache_images:
        try:
            image: pygame.Surface = pygame.image.load(path).convert_alpha()

            image = pygame.transform.smoothscale(image, (width, height))

            cache_images[key] = image
        except:
            return None
    
    return cache_images[key]

def get_style(_type: str, classes: list[str], _id: str, modifiers: dict, page: Any) -> dict | None:
    style_key: tuple[str, str, str, str] = (_type, str(classes), _id, str(modifiers))
    page_key: str = str(page.page_id)

    if not page_key in cache_styles:
        cache_styles[page_key] = {}

        return None

    page_styles: dict = cache_styles[page_key]

    if not style_key in page_styles:
        return None
    
    return copy.deepcopy(page_styles[style_key])

def add_style(_type: str, classes: list[str], _id: str, modifiers: dict, style: dict, page: Any) -> None:
    style_key: tuple[str, str, str, str] = (_type, str(classes), _id, str(modifiers))
    page_key: str = str(page.page_id)

    if not page_key in cache_styles:
        cache_styles[page_key] = {}

    page_styles: dict = cache_styles[page_key]

    page_styles[style_key] = style