from __future__ import annotations
from pygame_dom.style_sheet import StyleSheet
import pygame

class UIRenderObject:
    def __init__(self, font: pygame.font.Font, style_sheet: StyleSheet) -> UIRenderObject:
        self.font = font
        self.style_sheet = style_sheet

        self.reset()
    
    def reset(self) -> None:
        self.render_line = 0
        self.render_line_height = 0
        self.render_x = 0
        self.render_y = 0
        self.width = 0
        self.height = 0
        self.render_zindex = 0
    
    def create_stamp(self) -> UIRenderObject:
        stamp: UIRenderObject = UIRenderObject(self.font, self.style_sheet)

        return stamp