from __future__ import annotations
from typing import Callable
from pygame_dom.page import UIPage
from pygame_dom.cache.registry import exec_function, add_function
from pygame_dom.ui_event import UIEvent
from pygame_dom.ui_state import UIState
import pygame

FUNCTION_REGISTRY: dict = {}

class RUI:
    def __init__(self) -> RUI:
        pass
    
    @staticmethod
    def exec_function(function_name: str) -> None:
        exec_function(function_name)

    @staticmethod
    def register(name: str | None = None) -> Callable:
        """
        Register a function as an event handler

        Args:
            name (str | None): Optional custom event handler name

        Returns:
            function: A decorator that registers the function as an event handler

        Example:
            >>> @RUI.register()
            >>> def button_1() -> None:
            >>>     print("button 1 was clicked")
            >>>
            >>> # In HTML file:
            >>> # <button onclick="button_1">Click</button>
        """

        def decorator(func: Callable) -> Callable:
            add_function(func, name)

            return func
        
        return decorator

    @staticmethod
    def create_ui_page(html_file_path: str) -> UIPage:
        """
        Creates an UIPage element that can be drawn to the screen

        Args:
            html_file_path (str): Path to HTML file that will be used as UIPage
        
        Returns:
            UIPage: UIPage that can be drawn to the screen using UIPage.draw()
        """

        return UIPage(html_file_path)
    
    @staticmethod
    def get_system_available_fonts() -> list[str]:
        """
        Returns a list of all available font names in pygame on this computer

        Returns:
            list[str]: List of all available fonts
        """

        return pygame.sysfont.get_fonts()