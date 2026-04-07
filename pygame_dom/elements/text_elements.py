from __future__ import annotations
from pygame_dom.ui_render_object import UIRenderObject
from pygame_dom.cache.cache import get_font
from pygame_dom.cache.registry import add_radio_input, get_radio_inputs, get_framework_image, update_bind
from pygame_dom.data.transitions import handle_transition
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
        self.scale = 1
        self.parent_scale = 1
        self.text_align = "left"
        self.y_align = "top"
        self.text_decoration = "none"
        self.text_decoration_color = (255, 255, 255, 255)
        self.text_decoration_thickness = 2

        self.style_stamp = None
        self.time = 0
        self.delay_dict = {}
        self.start_dict = {}

        self.inline_style_raw = ""
        self.inline_style = {}
        self.inline_style_parsed = False
        self.reactive_inline_style = {}

        self.modern_text = []
    
    def get_height(self) -> int:
        if not self.rect:
            return 0
        
        return int(self.rect.height / (self.scale * self.parent_scale))

    def get_width(self) -> int:
        if not self.rect:
            return 0
        
        return int(self.rect.width / (self.scale * self.parent_scale))

    def __get_font_family(self, font_family: str) -> str:
        if font_family.startswith("url("):
            font_path: str = font_family[5:len(font_family) - 2]

            return "*" + font_path

        return font_family

    def set_style(self, ui_render_object: UIRenderObject, classes: list[str], _id: str, _type: str, modifiers: dict) -> dict:
        if not ui_render_object:
            return {}

        if not ui_render_object.style_sheet:
            return {}
        
        if hasattr(self, "input_type"):
            modifiers["input_type"] = self.input_type

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

        self.scale = self.style_stamp.get("scale", 1)
        self.text_align = self.style_stamp.get("text-align", "left")
        self.text_decoration = self.style_stamp.get("text-decoration-line", "none")
        self.text_decoration_thickness = self.style_stamp.get("text-decoration-thickness", 2)

        text_decoration_color: tuple | None = self.style_stamp.get("text-decoration-color")

        if not text_decoration_color:
            self.text_decoration_color = self.style_stamp.get("color", (255, 255, 255))
        else:
            self.text_decoration_color = text_decoration_color

        self.color = self.style_stamp["color"]
        self.font_size = self.style_stamp["font-size"]
        self.font_weight = self.style_stamp["font-weight"]
        self.font_style = self.style_stamp["font-style"]

        is_bold: bool = self.font_weight >= 600
        is_italic: bool = self.font_style == "italic"

        self.font = get_font(self.__get_font_family(self.style_stamp.get("font-family")), self.font_size, is_bold, is_italic)

        self.time = pygame.time.get_ticks()

        return self.style_stamp
    
    def pre_render_font(self, ui_render_object: UIRenderObject, parent_scale: float) -> None:
        if not self.font:
            self.font = ui_render_object.font

        self.parent_scale = parent_scale

        color: tuple = tuple(int(c) for c in self.color)

        if hasattr(self, "placeholder") and self.text == "":
            self.surface = self.font.render(self.placeholder, True, color)
        else:
            self.surface = self.font.render(self.text, True, color)

        if len(self.color) > 3:
            self.surface.set_alpha(self.color[3])
        
        self.rect = self.surface.get_rect()

        self.surface = pygame.transform.smoothscale(self.surface, (int(self.rect.width * self.scale * parent_scale), int(self.rect.height * self.scale * parent_scale)))

        self.rect = self.surface.get_rect()

    def get_text_position(self, outer_position: tuple[int, int, int, int], padding: tuple[int, int, int, int]) -> tuple[int, int]:
        x: int = 0
        y: int = 0

        if self.text_align == "center":
            x = outer_position[0] + int((outer_position[2] - self.rect.width) / 2)
        elif self.text_align == "left":
            x = outer_position[0] + padding[3] * self.scale * self.parent_scale
        elif self.text_align == "right":
            x = outer_position[0] + outer_position[2] - self.rect.width - padding[1] * self.scale * self.parent_scale

        if self.y_align == "center":
            y = outer_position[1] + int((outer_position[3] - self.rect.height) / 2)
        elif self.y_align == "top":
            y = outer_position[1] + padding[0] * self.scale * self.parent_scale
        elif self.y_align == "bottom":
            y = outer_position[1] + outer_position[3] - self.rect.height - padding[2] * self.scale * self.parent_scale

        return (x, y)

    def get_modern_size(self, text: str) -> tuple[int, int]:
        return self.font.size(text)

    def get_modern_text(self, index: int) -> tuple[int, str] | None:
        for t in self.modern_text:
            if not t[0] == index:
                continue

            return t
        
        return None

    def draw_modern_text(self, screen: pygame.display, modern_index: int, rect: tuple[int, int, int, int], ui_render_object: UIRenderObject) -> None:
        m_text: tuple[int, str] = self.get_modern_text(modern_index)

        if not m_text:
            return
        
        m_text_surface: pygame.Surface = self.font.render(m_text[1], True, self.color)

        if ui_render_object.overflow_surface:
            local_overflow_surface: pygame.Surface = pygame.Surface(ui_render_object.overflow_surface, pygame.SRCALPHA)

            local_overflow_surface.blit(
                m_text_surface, 
                (
                    int(rect[0] - ui_render_object.overflow_surface_x),
                    int(rect[1] - ui_render_object.overflow_surface_y),
                    int(rect[2]),
                    int(rect[3])
                )
            )

            if self.text_decoration == "underline":
                pygame.draw.rect(local_overflow_surface, self.text_decoration_color, (
                    int(rect[0] - ui_render_object.overflow_surface_x), int(rect[1] + rect[3] - ui_render_object.overflow_surface_y), int(rect[2]), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "overline":
                pygame.draw.rect(local_overflow_surface, self.text_decoration_color, (
                    int(rect[0] - ui_render_object.overflow_surface_x), int(rect[1] - self.text_decoration_thickness - ui_render_object.overflow_surface_y), int(rect[2]), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "line-through":
                pygame.draw.rect(local_overflow_surface, self.text_decoration_color, (
                    int(rect[0] - ui_render_object.overflow_surface_x), int(rect[1] + int(rect[3] / 2) - ui_render_object.overflow_surface_y), int(rect[2]), int(self.text_decoration_thickness)
            ))

            screen.blit(local_overflow_surface, (int(ui_render_object.overflow_surface_x), int(ui_render_object.overflow_surface_y)))
        else:
            screen.blit(m_text_surface, (int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])))
        
            if self.text_decoration == "underline":
                pygame.draw.rect(screen, self.text_decoration_color, (
                    int(rect[0]), int(rect[1] + rect[3]), int(rect[2]), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "overline":
                pygame.draw.rect(screen, self.text_decoration_color, (
                    int(rect[0]), int(rect[1] - self.text_decoration_thickness), int(rect[2]), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "line-through":
                pygame.draw.rect(screen, self.text_decoration_color, (
                    int(rect[0]), int(rect[1] + int(rect[3] / 2)), int(rect[2]), int(self.text_decoration_thickness)
            ))

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, padding: tuple[int, int, int, int], margin: tuple[int, int, int, int], offset: tuple[int, int, int, int], outer_position: tuple[int, int, int, int]) -> None:
        if not self.surface:
            return

        position: tuple[int, int] = self.get_text_position(outer_position, padding)

        self.rect.x = position[0]
        self.rect.y = position[1]

        if hasattr(self, "offset_x"):
            self.rect.x -= self.offset_x

        if ui_render_object.overflow_surface:
            local_overflow_surface: pygame.Surface = pygame.Surface((int(ui_render_object.overflow_surface[0]), int(ui_render_object.overflow_surface[1])), pygame.SRCALPHA)

            local_overflow_surface.blit(
                self.surface,
                (
                    int(self.rect[0] - ui_render_object.overflow_surface_x),
                    int(self.rect[1] - ui_render_object.overflow_surface_y),
                    int(self.rect[2]),
                    int(self.rect[3])
                )
            )

            if self.text_decoration == "underline":
                pygame.draw.rect(local_overflow_surface, self.text_decoration_color, (
                    int(self.rect.x - ui_render_object.overflow_surface_x), int(self.rect.y + self.rect.height - ui_render_object.overflow_surface_y), int(self.rect.width), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "overline":
                pygame.draw.rect(local_overflow_surface, self.text_decoration_color, (
                    int(self.rect.x - ui_render_object.overflow_surface_x), int(self.rect.y - self.text_decoration_thickness - ui_render_object.overflow_surface_y), int(self.rect.width), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "line-through":
                pygame.draw.rect(local_overflow_surface, self.text_decoration_color, (
                    int(self.rect.x - ui_render_object.overflow_surface_x), int(self.rect.y + int(self.rect.height / 2) - ui_render_object.overflow_surface_y), int(self.rect.width), int(self.text_decoration_thickness)
                ))

            screen.blit(local_overflow_surface, (int(ui_render_object.overflow_surface_x), int(ui_render_object.overflow_surface_y)))
        else:
            screen.blit(self.surface, (int(self.rect.x), int(self.rect.y), int(self.rect.width), int(self.rect.height)))

            if self.text_decoration == "underline":
                pygame.draw.rect(screen, self.text_decoration_color, (
                    int(self.rect.x), int(self.rect.y + self.rect.height), int(self.rect.width), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "overline":
                pygame.draw.rect(screen, self.text_decoration_color, (
                    int(self.rect.x), int(self.rect.y - self.text_decoration_thickness), int(self.rect.width), int(self.text_decoration_thickness)
                ))
            elif self.text_decoration == "line-through":
                pygame.draw.rect(screen, self.text_decoration_color, (
                    self.rect.x, self.rect.y + int(self.rect.height / 2), self.rect.width, self.text_decoration_thickness
                ))

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

class INPUT(TextElement):
    def __init__(self, text: str, input_type: str) -> INPUT:
        self.focus = False
        self.caret_position = 0
        self.caret = None
        self.caret_size_x = 2
        self.placeholder = text
        self.selection_start = -1
        self.selection_end = -1
        self.prev_input_active_time = 0
        self.padding = (0, 0, 0, 0)
        self.caret_timer = 0
        self.caret_visible = True
        self.input_type = input_type
        self.prev_text = ""
        self.secret = ""
        self.offset_x = 0
        self.prev_caret_x = 0
        self.calc_offset = False
        self.all_text_x = 0
        self.actual_input_text_max_width = 0

        self.select_mode = False

        super().__init__("")
    
    def __handle_bind_event(self) -> None:
        if self.input_type == "password":
            if "bind:value" in self.root.binds:
                update_bind(self.root.binds["bind:value"], self.secret)
        else:
            if "bind:value" in self.root.binds:
                update_bind(self.root.binds["bind:value"], self.text)

        if "bind:focus" in self.root.binds:
            update_bind(self.root.binds["bind:focus"], self.focus)

    def focus_element(self) -> None:
        self.__handle_bind_event()
    
    def unfocus_element(self) -> None:
        self.__handle_bind_event()

    def init_bind(self) -> None:
        self.__handle_bind_event()
    
    def get_selected_text(self) -> str:
        if self.selection_start == -1 or self.selection_end == -1:
            return ""
        
        return self.text[min(self.selection_start, self.selection_end):max(self.selection_start, self.selection_end)]

    def handle_selection(self, mouse_position: tuple[int, int], is_mouse_down: bool, is_mouse_move: bool, is_mouse_up: bool, parent_coords: tuple[int, int, int, int]) -> None:
        parent_rect: pygame.Rect = pygame.Rect(parent_coords[0], parent_coords[1], parent_coords[2], parent_coords[3])
        
        if not self.focus or not parent_rect:
            return
        
        pressed_keys: list = pygame.key.get_pressed()

        if (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]) and is_mouse_down:
            return

        if is_mouse_down and parent_rect.collidepoint(mouse_position):
            self.select_mode = True

            self.caret_position = self.get_caret_position_from_mouse_position(mouse_position)
            self.selection_start = self.caret_position
            self.selection_end = self.caret_position

        if is_mouse_move and self.select_mode:
            self.caret_position = self.get_caret_position_from_mouse_position(mouse_position)
            self.selection_end = self.caret_position
        
        if is_mouse_up:
            self.select_mode = False

    def copy_selection_text(self) -> None:
        if self.selection_start == -1 or self.selection_end == -1 or self.selection_start == self.selection_end:
            return

        selected_text: str = self.get_selected_text()

        if not pygame.scrap.get_init():
            pygame.scrap.init()

        pygame.scrap.put(pygame.SCRAP_TEXT, selected_text.encode("utf-8"))
    
    def paste_copied_text(self) -> None:
        if not pygame.scrap.get_init():
            pygame.scrap.init()

        copied_text: bytes | str | None = pygame.scrap.get(pygame.SCRAP_TEXT)

        if not copied_text:
            return
        
        if isinstance(copied_text, bytes):
            try:
                copied_text = copied_text.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    copied_text = copied_text.decode("utf-16")
                except UnicodeDecodeError:
                    copied_text = copied_text.decode("latin-1", errors="replace")
        else:
            return

        copied_text = copied_text.replace("\0", "")

        if self.input_type == "number":
            replace: str = ""

            for letter in copied_text:
                if not (letter.isdigit() or ((letter == "+" or letter == "-") and self.text.count("+") + self.text.count("-") + replace.count("-") + replace.count("+") < 2)):
                    continue

                replace += letter
            
            copied_text = replace

        if self.selection_start == -1 or self.selection_end == -1 or self.selection_start == self.selection_end:
            display_copied_text: str = copied_text

            if self.input_type == "password":
                display_copied_text = ""

                for _ in range(len(copied_text)):
                    display_copied_text += "*"

            self.text = self.text[:self.caret_position] + display_copied_text + self.text[self.caret_position:]
            self.secret = self.secret[:self.caret_position] + copied_text + self.secret[self.caret_position:]
            self.caret_position += len(copied_text)

            self.selection_start = self.caret_position
            self.selection_end = self.caret_position
        else:
            start: int = min(self.selection_start, self.selection_end)
            end: int = max(self.selection_start, self.selection_end)

            self.text = self.text[:start] + copied_text + self.text[end:]
            self.secret = self.secret[:start] + copied_text + self.secret[end:]
            self.caret_position = start + len(copied_text)
            self.selection_start = self.selection_end = -1

        self.__handle_bind_event()

    def move_caret_right(self, is_shift: bool) -> None:
        self.caret_position += 1

        if self.caret_position > len(self.text):
            self.caret_position = len(self.text)
        
        if is_shift:
            if self.caret_position - 1 == self.selection_start:
                self.selection_start += 1
            elif self.caret_position - 1 == self.selection_end:
                self.selection_end += 1
            else:
                if self.caret_position == self.selection_end:
                    self.selection_end = self.caret_position
                else:
                    self.selection_start = self.caret_position
        else:
            self.selection_start = self.caret_position
            self.selection_end = self.caret_position

    def move_caret_left(self, is_shift: bool) -> None:
        self.caret_position -= 1

        if self.caret_position < 0:
            self.caret_position = 0
        
        if is_shift:
            if self.caret_position + 1 == self.selection_start:
                self.selection_start -= 1
            elif self.caret_position + 1 == self.selection_end:
                self.selection_end -= 1
            else:
                if self.caret_position == self.selection_end:
                    self.selection_end = self.caret_position
                else:
                    self.selection_start = self.caret_position
        else:
            self.selection_start = self.caret_position
            self.selection_end = self.caret_position

    def handle_input(self, active_keys: dict, created_events: list[str], created_event_attrs: list[dict]) -> None:
        if not self.focus:
            return

        pressed_keys: list = pygame.key.get_pressed()

        is_shift: bool = pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]
        is_ctrl: bool = pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]

        if is_ctrl and "keydown" in created_events:
            event_attrs: dict = created_event_attrs[created_events.index("keydown")]

            if event_attrs["key"] == pygame.K_c:
                self.copy_selection_text()

                return
            elif event_attrs["key"] == pygame.K_v:
                self.paste_copied_text()

                return

        time: int = pygame.time.get_ticks()

        if (time - self.prev_input_active_time) > 50:
            self.prev_input_active_time = time

            if pygame.K_RIGHT in active_keys and active_keys[pygame.K_RIGHT].get("press_time", pygame.time.get_ticks()) <= time - 500:
                self.move_caret_right(is_shift)
            elif pygame.K_LEFT in active_keys and active_keys[pygame.K_LEFT].get("press_time", pygame.time.get_ticks()) <= time - 500:
                self.move_caret_left(is_shift)
            elif pygame.K_DOWN in active_keys:
                self.caret_position = len(self.text)

                if is_shift:
                    if self.caret_position == self.selection_end:
                        self.selection_end = self.caret_position
                    else:
                        self.selection_start = self.caret_position
            elif pygame.K_UP in active_keys:
                self.caret_position = 0

                if is_shift:
                    if self.caret_position == self.selection_end:
                        self.selection_end = self.caret_position
                    else:
                        self.selection_start = self.caret_position
            elif pygame.K_BACKSPACE in active_keys and self.caret_position > 0 and active_keys[pygame.K_BACKSPACE].get("press_time", pygame.time.get_ticks()) <= time - 500:
                self.remove_character()
            elif pygame.K_RETURN in active_keys or pygame.K_TAB in active_keys or pygame.K_LSHIFT in active_keys or pygame.K_RSHIFT in active_keys or pygame.K_LCTRL in active_keys or pygame.K_RCTRL in active_keys:
                pass
            
        if "keydown" in created_events:
            event_attrs: dict = created_event_attrs[created_events.index("keydown")]

            if event_attrs["key"] in [
                pygame.K_RETURN, pygame.K_TAB, pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_LALT, pygame.K_RALT,
                pygame.K_UP, pygame.K_DOWN, pygame.K_PAGEUP, pygame.K_PAGEDOWN
            ]:
                pass
            elif event_attrs["key"] == pygame.K_BACKSPACE:
                self.remove_character()
            elif event_attrs["key"] == pygame.K_LEFT:
                self.move_caret_left(is_shift)
            elif event_attrs["key"] == pygame.K_RIGHT:
                self.move_caret_right(is_shift)
            else:
                self.write_character(event_attrs.get("unicode", ""))

    def write_character(self, char: str) -> None:
        if self.input_type == "number":
            if not (char.isdigit() or ((char == "+" or char == "-") and self.text.count("+") + self.text.count("-") < 2)):
                return

        if not (self.selection_start == -1 or self.selection_end == -1 or self.selection_start == self.selection_end):
            self.remove_character()

        display_char: str = char

        if self.input_type == "password":
            display_char = "*"

        self.text = self.text[
            :self.caret_position
        ] + display_char + self.text[
            self.caret_position:
        ]

        self.secret = self.secret[
            :self.caret_position
        ] + char + self.secret[
            self.caret_position:
        ]

        self.caret_position += 1

        self.selection_start = self.caret_position
        self.selection_end = self.caret_position

        self.__handle_bind_event()
    
    def remove_character(self) -> None:
        if self.selection_start == -1 or self.selection_end == -1 or self.selection_start == self.selection_end:
            if self.caret_position > 0 and len(self.text) > 0:
                self.text = self.text[
                    :self.caret_position - 1
                ] + self.text[
                    self.caret_position:
                ]

                self.secret = self.secret[
                    :self.caret_position - 1
                ] + self.secret[
                    self.caret_position:
                ]

                self.caret_position -= 1
            
            self.selection_start = self.caret_position
            self.selection_end = self.caret_position

            self.calc_offset = True
        else:
            start: int = min(self.selection_start, self.selection_end)
            end: int = max(self.selection_start, self.selection_end)

            self.text = self.text[:start] + self.text[end:]
            self.secret = self.secret[:start] + self.secret[end:]
            self.caret_position = start
            self.selection_start = self.selection_end = -1

            self.calc_offset = True
        
        self.__handle_bind_event()

    def get_caret_position_from_mouse_position(self, mouse_position: tuple[int, int]) -> int:
        caret_pos: int = 0

        if mouse_position[0] < self.rect.x:
            return 0

        if mouse_position[0] > self.rect.x + self.rect.width:
            return len(self.text)

        relative_x: int = mouse_position[0] - self.rect.x - 5

        for i in range(len(self.text) + 1):
            width: int = self.font.size(self.text[:i])[0]

            if width > relative_x:
                caret_pos = i

                break
        
        return caret_pos

    def reset_selection(self) -> None:
        self.selection_end = -1
        self.selection_start = -1

    def click_to_select_caret_position(self, mouse_position: tuple[int, int]) -> None:
        pressed_keys: list = pygame.key.get_pressed()

        if (pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]):
            if self.selection_end == -1 or self.selection_start == -1 or self.selection_start == self.selection_end:
                self.selection_start = self.caret_position

                new_pos: int = self.get_caret_position_from_mouse_position(mouse_position)

                self.caret_position = new_pos
                self.selection_end = new_pos
            else:
                new_pos: int = self.get_caret_position_from_mouse_position(mouse_position)

                if self.caret_position == self.selection_end:
                    self.selection_end = new_pos
                else:
                    self.selection_start = new_pos

                self.caret_position = new_pos

            return

        self.caret_position = self.get_caret_position_from_mouse_position(mouse_position)

        before_text_surface: pygame.Surface = self.font.render(self.text[:self.caret_position], True, (0, 0, 0))
        before_text_rect: pygame.Rect = before_text_surface.get_rect()

        n_caret_x: int = self.all_text_x + before_text_rect.width - 1

        self.prev_caret_x = n_caret_x

    def draw_selection(self, screen: pygame.Surface, text_x: int, text_y: int, padding: tuple[int, int, int, int], ui_render_object: UIRenderObject) -> None:
        if self.selection_end == -1 or self.selection_start == -1 or self.selection_start == self.selection_end:
            return
        
        start: int = min(self.selection_start, self.selection_end)
        end: int = max(self.selection_start, self.selection_end)

        start_x: int = text_x + self.font.size(self.text[:start])[0] - self.offset_x
        end_x: int = text_x + self.font.size(self.text[:end])[0] - self.offset_x

        if ui_render_object.overflow_surface:
            local_overflow_surface: pygame.Surface = pygame.Surface((int(ui_render_object.overflow_surface[0]), int(ui_render_object.overflow_surface[1])), pygame.SRCALPHA)

            pygame.draw.rect(local_overflow_surface, (100, 100, 255), (
                int(start_x - ui_render_object.overflow_surface_x), int(text_y - ui_render_object.overflow_surface_y), int(end_x - start_x), int(self.rect.height)
            ))

            screen.blit(local_overflow_surface, (int(ui_render_object.overflow_surface_x), int(ui_render_object.overflow_surface_y)))
        else:
            pygame.draw.rect(screen, (100, 100, 255), (
                int(start_x), int(text_y), int(end_x - start_x), int(self.rect.height)
            ))

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, padding: tuple[int, int, int, int], margin: tuple[int, int, int, int], offset: tuple[int, int, int, int], outer_position: tuple[int, int, int, int]) -> None:
        if self.focus and self.surface:
            position: tuple[int, int] = self.get_text_position(outer_position, padding)

            all_text_x: int = position[0]
            all_text_y: int = position[1]

            self.all_text_x: int = all_text_x

            before_text_surface: pygame.Surface = self.font.render(self.text[:self.caret_position], True, (0, 0, 0))
            before_text_rect: pygame.Rect = before_text_surface.get_rect()
            
            caret_height: int = before_text_rect.height

            caret_x: int = all_text_x + before_text_rect.width - 1 - self.offset_x
            n_caret_x: int = all_text_x + before_text_rect.width - 1

            self.padding = padding

            actual_input_text_max_width: int = outer_position[2] - padding[1] - padding[3]

            self.actual_input_text_max_width = actual_input_text_max_width

            if before_text_rect.width > actual_input_text_max_width and self.prev_caret_x < n_caret_x or self.calc_offset and before_text_rect.width > actual_input_text_max_width:
                self.offset_x = before_text_rect.width - actual_input_text_max_width
            elif before_text_rect.width < self.offset_x and self.prev_caret_x > n_caret_x or self.calc_offset and before_text_rect.width < self.offset_x:
                self.offset_x = before_text_rect.width

            self.calc_offset = False
            self.prev_caret_x = n_caret_x

            if self.offset_x < 0:
                self.offset_x = 0

            render_offset_overflow_right = padding[1]
            render_offset_overflow_left = padding[3]

            ui_render_object.overflow_surface = (ui_render_object.overflow_surface[0] - (render_offset_overflow_left + render_offset_overflow_right), ui_render_object.overflow_surface[1])
            ui_render_object.overflow_surface_x += render_offset_overflow_left

            self.draw_selection(screen, all_text_x, all_text_y, padding, ui_render_object)

            if self.selection_start == -1 or self.selection_end == -1 or self.selection_start == self.selection_end:
                time: int = pygame.time.get_ticks()

                if time - self.caret_timer > 500:
                    self.caret_timer = time

                    self.caret_visible = not self.caret_visible

                if self.caret_visible:
                    if ui_render_object.overflow_surface:
                        local_overflow_surface: pygame.Surface = pygame.Surface((int(ui_render_object.overflow_surface[0]), int(ui_render_object.overflow_surface[1])), pygame.SRCALPHA)

                        pygame.draw.rect(
                            local_overflow_surface,
                            (0, 0, 0),
                            (
                                int(caret_x - ui_render_object.overflow_surface_x), 
                                int(all_text_y - ui_render_object.overflow_surface_y), 
                                int(self.caret_size_x), 
                                int(caret_height)
                            )
                        )

                        screen.blit(local_overflow_surface, (int(ui_render_object.overflow_surface_x), int(ui_render_object.overflow_surface_y)))
                    else:
                        pygame.draw.rect(
                            screen,
                            (0, 0, 0),
                            (int(caret_x), int(all_text_y), int(self.caret_size_x), int(caret_height))
                        )
        
        return super().draw(screen, ui_render_object, padding, margin, offset, outer_position)

class INPUT_BUTTON(TextElement):
    def __init__(self, input_type: str, name: str) -> INPUT_BUTTON:
        self.input_type = input_type
        self.active = False
        self.name = name

        super().__init__("")

        if self.input_type == "radio":
            add_radio_input(self)
    
    def __handle_bind_event(self) -> None:
        if "bind:checked" in self.root.binds:
            update_bind(self.root.binds["bind:checked"], self.active)

    def init_bind(self) -> None:
        self.__handle_bind_event()

    def check(self) -> None:
        if self.input_type == "radio":
            neighbor_inputs: list[INPUT_BUTTON] | None = get_radio_inputs(self.name)

            if neighbor_inputs:
                for neighbor_input in neighbor_inputs:
                    neighbor_input.active = False
            
            self.active = True
        elif self.input_type == "checkbox":
            self.active = not self.active

        self.__handle_bind_event()

    def draw(self, screen: pygame.Surface, ui_render_object: UIRenderObject, padding: tuple[int, int, int, int], margin: tuple[int, int, int, int], offset: tuple[int, int, int, int], outer_position: tuple[int, int, int, int]) -> None:
        if self.input_type == "radio":
            center: tuple[int, int] = (
                outer_position[0] + int(outer_position[2] / 2),
                outer_position[1] + int(outer_position[3] / 2)
            )

            radius: int = 0

            if outer_position[2] < outer_position[3]:
                radius = int(outer_position[2] / 2 - ((padding[1] + padding[3]) / 2))
            else:
                radius = int(outer_position[3] / 2 - ((padding[0] + padding[2]) / 2))

            color: tuple[int, int, int] = (255, 255, 255)

            if ui_render_object.overflow_surface:
                local_overflow_surface: pygame.Surface = pygame.Surface(ui_render_object.overflow_surface)

                if self.active:
                    color = (0, 128, 0)

                    inner_radius: int = int(radius / 1.75)

                    pygame.draw.circle(
                        local_overflow_surface, 
                        color, 
                        (
                            int(center[0] - ui_render_object.overflow_surface_x),
                            int(center[1] - ui_render_object.overflow_surface_y)
                        ),
                        int(inner_radius))

                pygame.draw.circle(
                    local_overflow_surface, 
                    color, 
                    (
                        int(center[0] - ui_render_object.overflow_surface_x),
                        int(center[1] - ui_render_object.overflow_surface_y)
                    ),
                    int(radius), 
                    width=2
                )

                screen.blit(local_overflow_surface, (int(ui_render_object.overflow_surface_x), int(ui_render_object.overflow_surface_y)))

            else:
                if self.active:
                    color = (0, 128, 0)

                    inner_radius: int = int(radius / 1.75)

                    pygame.draw.circle(screen, color, (int(center[0]), int(center[1])), int(inner_radius))

                pygame.draw.circle(screen, color, (int(center[0]), int(center[1])), int(radius), width=2)
        elif self.input_type == "checkbox":
            size: int = 0

            if outer_position[2] < outer_position[3]:
                size = int(outer_position[2] - (padding[1] + padding[3]))
            else:
                size = int(outer_position[3] - (padding[0] + padding[2]))
            
            position: tuple[int, int] = (
                outer_position[0] + int((outer_position[2] - size) / 2),
                outer_position[1] + int((outer_position[3] - size) / 2)
            )

            color: tuple[int, int, int] = (255, 255, 255)
            border_width: int = 2

            if self.active:
                color = (0, 128, 0)
                border_width = 0

            if ui_render_object.overflow_surface:
                local_overflow_surface: pygame.Surface = pygame.Surface((int(ui_render_object.overflow_surface[0]), int(ui_render_object.overflow_surface[1])), pygame.SRCALPHA)

                pygame.draw.rect(
                    local_overflow_surface, 
                    color, 
                    (
                        int(position[0] - ui_render_object.overflow_surface_x),
                        int(position[1] - ui_render_object.overflow_surface_y),
                        int(size),
                        int(size)
                    )
                )

                if self.active:
                    mark_image: pygame.image = get_framework_image("mark")

                    if mark_image and size > 0:
                        mark_image = pygame.transform.smoothscale(mark_image, (int(size), int(size)))
                
                        local_overflow_surface.blit(mark_image, (int(position[0] - ui_render_object.overflow_surface_x), int(position[1] - ui_render_object.overflow_surface_y), int(size), int(size)))

                screen.blit(local_overflow_surface, (int(ui_render_object.overflow_surface_x), int(ui_render_object.overflow_surface_y)))
            else:
                pygame.draw.rect(screen, color, (int(position[0]), int(position[1]), int(size), int(size)), width=int(border_width))

                if self.active:
                    mark_image: pygame.image = get_framework_image("mark")

                    if mark_image and size > 0:
                        mark_image = pygame.transform.smoothscale(mark_image, (int(size), int(size)))
                
                        screen.blit(mark_image, (int(position[0]), int(position[1]), int(size), int(size)))
