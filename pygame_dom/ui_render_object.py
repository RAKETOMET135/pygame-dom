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
        self.pad_horizontal = 0
        self.pad_vertical = 0
        self.def_render_x = 0
        self.overflow_surface = None
        self.overflow_surface_x = 0
        self.overflow_surface_y = 0
    
    def copy(self) -> UIRenderObject:
        copy: UIRenderObject = UIRenderObject(self.font, self.style_sheet)

        copy.render_line = self.render_line
        copy.render_line_height = self.render_line_height
        copy.render_x = self.render_x
        copy.render_y = self.render_y
        copy.width = self.width
        copy.height = self.height
        copy.render_zindex = self.render_zindex
        copy.pad_horizontal = self.pad_horizontal
        copy.pad_vertical = self.pad_vertical
        copy.def_render_x = self.def_render_x
        copy.overflow_surface = self.overflow_surface
        copy.overflow_surface_x = self.overflow_surface_x
        copy.overflow_surface_y = self.overflow_surface_y

        return copy

    def create_stamp(self) -> UIRenderObject:
        stamp: UIRenderObject = UIRenderObject(self.font, self.style_sheet)

        return stamp