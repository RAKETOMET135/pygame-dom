from __future__ import annotations
from bs4 import BeautifulSoup, Tag
from typing import Any
from pygame_dom.elements import *
from pygame_dom.ui_element import UIElement
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.style_sheet import StyleSheet
from pygame_dom.ui_event import UIEvent
from pygame_dom.ui_state import UIState, UIStateParser
from pygame_dom.cache.registry import add_page
from pygame_dom.cache.cache import get_image
import pygame

class UIPage:
    def __init__(self, html_file_path: str) -> UIPage:
        is_file_loaded: bool = False
        file_html: str = ""

        try:
            with open(html_file_path, "r") as file:
                file_html = file.read()
                is_file_loaded = True
        except:
            print(f"Could not open html file on path: {html_file_path}")
        
        if not is_file_loaded:
            return

        soup: BeautifulSoup = BeautifulSoup(file_html, "html.parser")

        self.soup = soup

        elements: list[Tag] = soup.find_all(recursive=False)

        self.elements = elements
        self.instances = []

        self.state_parser = UIStateParser()

        for element in elements:
            self.__build_element(element)

        self.__build_base_data()

        add_page(self)

    def __build_base_data(self) -> None:
        self.font = pygame.font.SysFont(None, 24)

        self.ui_render_object = UIRenderObject(self.font, None)
        self.style_sheet = None
        self.custom_cursor = None

    def style(self, css_file_path: str) -> None:
        """
        Loads CSS file that will be used to style this page

        Args:
            css_file_path (str): Path to CSS file
        """

        self.style_sheet = StyleSheet(css_file_path)
        self.ui_render_object.style_sheet = self.style_sheet

    def rebuild(self) -> None:
        """
        Clears all elements and creates them again using the loaded HTML file
        """

        self.instances = []

        for element in self.elements:
            self.__build_element(element)

    def __build_element(self, element: Tag, parent: UIElement | None = None) -> None:
        element_type: str = element.name
        element_text: str = self.__get_element_text(element)
        element_instance: Any = None

        match element_type:
            case "h1":
                element_instance = H1(element_text)
            case "h2":
                element_instance = H2(element_text)
            case "h3":
                element_instance = H3(element_text)
            case "h4":
                element_instance = H4(element_text)
            case "h5":
                element_instance = H5(element_text)
            case "h6":
                element_instance = H6(element_text)
            case "p":
                element_instance = P(element_text)
            case "div":
                element_instance = DIV(element_text)
            case "button":
                element_instance = BUTTON(element_text)
            case "img":
                element_instance = IMG(element.get("src", ""))
        
        ui_element: UIElement = UIElement(element_instance, element_type, parent)
        ui_element.set_classes(element.get("class") or [])
        ui_element.set_id(element.get("id") or "")
        ui_element.attrs = element.attrs

        for attr, value in ui_element.attrs.items():
            self.state_parser.parse_attr(value, ui_element, attr)

        self.state_parser.parse_text(element_text, ui_element)

        if parent:
            parent.add_child(ui_element)
        else:
            self.instances.append(ui_element)

        children: list[Tag] = element.find_all(recursive=False)

        for child in children:
            self.__build_element(child, ui_element)

    def __get_element_text(self, element: Tag) -> str:
        return "".join(
            child.strip()
            for child in element.contents
            if isinstance(child, str)
        )
    
    def __is_point_in_element(self, point: tuple[int, int], element: UIElement) -> bool:
        return (
            point[0] >= element.rendered_x and point[0] <= element.rendered_x + element.actual_size_x
            and
            point[1] >= element.rendered_y and point[1] <= element.rendered_y + element.actual_size_y
        )
    
    def __get_top_element(self, elements: list[UIElement]) -> UIElement | None:
        zindex: int = 0
        element: UIElement | None = None

        for el in elements:
            if not element:
                element = el
                zindex = el.latest_render_zindex

                continue

            if el.latest_render_zindex > zindex:
                element = el
                zindex = el.latest_render_zindex
        
        return element

    def __check_sub_elements(self, point: tuple[int, int], element: UIElement, affected_elements: list[UIElement], btn_down: bool, btn_up: bool, btn: int) -> None:
        for child in element.children:
            if self.__is_point_in_element(point, child):
                affected_elements.append(child)

                if not child.is_mouse_in:
                    child.is_mouse_enter = True
                    child.is_mouse_in = True
                
                if btn_down:
                    child.is_click_held = True

                    if btn == 1:
                        child.is_left_click_held = True
                    elif btn == 3:
                        child.is_right_click_held = True

                if btn_up:
                    child.is_click_turn = True

                    if btn == 1:
                        child.is_left_click_turn = True
                    elif btn == 3:
                        child.is_right_click_turn = True
            else:
                if child.is_mouse_in:
                    child.is_mouse_exit = True
                    child.is_mouse_in = False
                    child.is_click_held = False
                    child.is_left_click_held = False
                    child.is_right_click_held = False

                    affected_elements.append(child)

            self.__check_sub_elements(point, child, affected_elements, btn_down, btn_up, btn)  

    def render(self, screen: pygame.Surface, events: list[pygame.event.Event]) -> None:
        """
        Draws the page content onto surface and handles events

        Args:
            screen (pygame.Surface): Surface that is drawn on, can be screen
            events (list[pygame.event.Event]): List of events from pygame ("pygame.event.get()")
        """

        self.ui_render_object.reset()

        mouse_position: tuple[int, int] = pygame.mouse.get_pos()

        created_events: list[str] = []
        created_event_attrs: list = []
        handled_events: list[UIEvent] = []

        affected_elements: list[UIElement] = []

        btn_down: bool = False
        btn_up: bool = False
        btn: int = -1

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:    
                created_events.append("pointerdown")    
                created_event_attrs.append({"button": event.button})

                created_events.append("mousedown")
                created_event_attrs.append({"button": event.button})

                btn_down = True
                btn = event.button

                if btn == 1:
                    created_events.append("leftmousedown")
                    created_event_attrs.append({"button": 1})
                elif btn == 3:
                    created_events.append("rightmousedown")
                    created_event_attrs.append({"button": 3})
            
            elif event.type == pygame.MOUSEMOTION:
                created_events.append("mouseenter")
                created_event_attrs.append(None)

                created_events.append("mouseleave")
                created_event_attrs.append(None)

                created_events.append("pointerenter")
                created_event_attrs.append(None)

                created_events.append("pointerleave")
                created_event_attrs.append(None)

                created_events.append("mousemove")
                created_event_attrs.append(None)

                created_events.append("pointermove")
                created_event_attrs.append(None)
            elif event.type == pygame.MOUSEBUTTONUP:
                created_events.append("pointerup")
                created_event_attrs.append({"button": event.button})

                created_events.append("mouseup")
                created_event_attrs.append({"button": event.button})

                if not event.button in [2, 4, 5, 6, 7]:
                    created_events.append("click")
                    created_event_attrs.append({"button": event.button})

                created_events.append("dblclick")
                created_event_attrs.append({"button": event.button})

                btn_up = True
                btn = event.button

                if btn == 1:
                    created_events.append("leftclick")
                    created_event_attrs.append({"button": 1})

                    created_events.append("leftmouseup")
                    created_event_attrs.append({"button": 1})
                elif btn == 3:
                    created_events.append("rightclick")
                    created_event_attrs.append({"button": 3})

                    created_events.append("rightmouseup")
                    created_event_attrs.append({"button": 3})
            elif event.type == pygame.KEYDOWN:
                created_events.append("keydown")
                created_event_attrs.append({"key": event.key})
            elif event.type == pygame.KEYUP:
                created_events.append("keyup")
                created_event_attrs.append({"key": event.key})
            elif event.type == pygame.MOUSEWHEEL:
                created_events.append("mousewheel")
                created_event_attrs.append({"delta_x": event.x, "delta_y": event.y})

        element_hovered: bool = False

        for instance in self.instances:
            instance.latest_render_zindex = -1

            data: dict = instance.draw(screen, self.ui_render_object)

            if data["hover"]:
                element_hovered = True

            if self.__is_point_in_element(mouse_position, instance):
                affected_elements.append(instance)

                if not instance.is_mouse_in:
                    instance.is_mouse_enter = True
                    instance.is_mouse_in = True
                
                if btn_down:
                    instance.is_click_held = True

                    if btn == 1:
                        instance.is_left_click_held = True
                    elif btn == 3:
                        instance.is_right_click_held = True

                if btn_up:
                    instance.is_click_turn = True

                    if btn == 1:
                        instance.is_left_click_turn = True
                    elif btn == 3:
                        instance.is_right_click_turn = True
            else:
                if instance.is_mouse_in:
                    instance.is_mouse_exit = True
                    instance.is_mouse_in = False
                    instance.is_click_held = False
                    instance.is_left_click_held = False
                    instance.is_right_click_held = False

                    affected_elements.append(instance)
            
            self.__check_sub_elements(mouse_position, instance, affected_elements, btn_down, btn_up, btn)

        root_event_element: UIElement = self.__get_top_element(affected_elements)

        if not element_hovered and not pygame.mouse.get_cursor().type == pygame.SYSTEM_CURSOR_ARROW:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            pygame.mouse.set_visible(True)

            self.custom_cursor = None
        else:
            if root_event_element.custom_cursor:
                pygame.mouse.set_visible(False)

                self.custom_cursor = get_image(root_event_element.custom_cursor, 24, 24)
            elif not pygame.mouse.get_cursor().type == root_event_element.cursor:
                pygame.mouse.set_cursor(root_event_element.cursor)
                pygame.mouse.set_visible(True)

                self.custom_cursor = None

        if self.custom_cursor:
            screen.blit(self.custom_cursor, mouse_position)

        current_event: UIEvent | None = None

        if root_event_element:
            click_delay: int = pygame.time.get_ticks() - root_event_element.last_click_time

            i: int = -1

            for created_event in created_events:
                i += 1

                if (created_event == "mouseenter" or created_event == "pointerenter") and not root_event_element.is_mouse_enter:
                    continue

                if (created_event == "mouseleave" or created_event == "pointerleave") and not root_event_element.is_mouse_exit:
                    continue

                if created_event == "click" and not root_event_element.is_click_held:
                    continue

                if created_event == "dblclick" and (click_delay > 400 or click_delay < 10):
                    continue

                if created_event == "leftclick" and not root_event_element.is_left_click_held:
                    continue

                if created_event == "rightclick" and not root_event_element.is_right_click_held:
                    continue

                current_event = UIEvent(created_event, root_event_element)

                event_attrs: dict | None = created_event_attrs[i]

                if event_attrs:
                    current_event.key = event_attrs.get("key")
                    current_event.button = event_attrs.get("button")
                    current_event.delta_x = event_attrs.get("delta_x")
                    current_event.delta_y = event_attrs.get("delta_y")

                handled_events.append(current_event)

                root_event_element.on_event(current_event)