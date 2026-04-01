import pygame

cache_fonts: dict = {}
cache_images: dict = {}

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