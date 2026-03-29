import pygame

cache_fonts: dict = {}

def get_font(name: str, size: int, bold: bool, italic: bool) -> pygame.font.Font:
    key: tuple[str, int, bool, bool] = (name, size, bold, italic)

    if not key in cache_fonts:
        cache_fonts[key] = pygame.font.SysFont(name, size, bold, italic)
    
    return cache_fonts[key]