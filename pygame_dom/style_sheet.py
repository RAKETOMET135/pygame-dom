from __future__ import annotations
from importlib import resources
from typing import Any
from pygame_dom.data.named_colors import CSS_NAMED_COLORS
from pygame_dom.cache.registry import add_framework_image
from pygame_dom.cache.cache import get_style, add_style
import pygame
import math
import copy

class StyleRule:
    def __init__(self, name: str, value: str) -> StyleRule:
        self.name = name
        self.value = value
    
    def __str__(self) -> str:
        return f"StyleRule(name: {self.name}, value: {self.value})"

class TagStyle:
    def __init__(self, selector: str, style_rules: list[StyleRule]) -> TagStyle:
        self.selector = selector
        self.style_rules = style_rules

class ClassStyle:
    def __init__(self, style_class: str, style_rules: list[StyleRule]) -> ClassStyle:
        self.style_class = style_class
        self.style_rules = style_rules

class IdStyle:
    def __init__(self, style_id: str, style_rules: list[StyleRule]) -> IdStyle:
        self.style_id = style_id
        self.style_rules = style_rules

class StyleSheet:
    def __init__(self, css_file_path: str, state_parser: Any) -> StyleSheet:
        self.default_style = []
        self.global_style = []
        self.tag_styles = []
        self.class_styles = []
        self.id_styles = []

        self.state_parser = state_parser

        is_file_loaded: bool = False
        css_content: str = ""

        try:
            with open(css_file_path, "r") as file:
                css_content = file.read()
                is_file_loaded = True
        except:
            print(f"Could not open CSS file on path: {css_file_path}")
        
        if not is_file_loaded:
            return
        
        with resources.files("pygame_dom.images").joinpath("mark.png").open("rb") as file:
            image: pygame.Surface = pygame.image.load(file).convert_alpha()

            add_framework_image(image, "mark")
        
        self.__load_default_css()

        css_content = self.__polish_css_string(css_content)

        self.parser(css_content)

    def load_another_css(self, another_css_file_path: str) -> None:
        is_file_loaded: bool = False
        css_content: str = ""

        try:
            with open(another_css_file_path, "r") as file:
                css_content = file.read()
                is_file_loaded = True
        except:
            print(f"Could not open CSS file on path: {another_css_file_path}")
        
        if not is_file_loaded:
            return
        
        css_content = self.__polish_css_string(css_content)

        self.parser(css_content)

    def __load_default_css(self) -> None:
        try:
            with resources.open_text("pygame_dom.style", "default.css") as file:
                css_content: str = file.read()
                css_content = self.__polish_css_string(css_content)

                self.parser(css_content, is_default=True)
        except:
            pass

    def get_style_rule(self, style_rules: list[StyleRule], style_rule: StyleRule) -> StyleRule | None:
        for sr in style_rules:
            if not sr.name == style_rule.name:
                continue

            return sr
        
        return None

    def get_tag_style(self, tag_selector: str) -> TagStyle | None:
        for tag_style in self.tag_styles:
            if not tag_style.selector == tag_selector:
                continue

            return tag_style
        
        return None

    def get_default_tag_style(self, tag_selector: str) -> TagStyle | None:
        for tag_style in self.default_style:
            if not tag_style.selector == tag_selector:
                continue

            return tag_style
        
        return None

    def get_class_style(self, class_selector: str) -> ClassStyle | None:
        class_selector = class_selector[1:]

        for class_style in self.class_styles:
            if not class_style.style_class == class_selector:
                continue

            return class_style
        
        return None
    
    def get_id_style(self, id_selector: str) -> IdStyle | None:
        id_selector = id_selector[1:]

        for id_style in self.id_styles:
            if not id_style.style_id == id_selector:
                continue

            return id_style
        
        return None

    def parse_root_selector(self, content: list[StyleRule]) -> None:
        for style_rule in content:
            sr: StyleRule | None = self.get_style_rule(self.global_style, style_rule)

            if not sr:
                self.global_style.append(style_rule)
            else:
                sr.value = style_rule.value

    def parse_tag_selector(self, selector: str, content: list[StyleRule]) -> None:
        tag_style: TagStyle | None = self.get_tag_style(selector)

        if not tag_style:
            self.tag_styles.append(TagStyle(selector, content))
        else:
            for style_rule in content:
                sr: StyleRule | None = self.get_style_rule(tag_style.style_rules, style_rule)

                if not sr:
                    tag_style.style_rules.append(style_rule)
                else:
                    sr.value = style_rule.value

    def parse_default_tag_selector(self, selector: str, content: list[StyleRule]) -> None:
        tag_style: TagStyle | None = self.get_default_tag_style(selector)

        if not tag_style:
            self.default_style.append(TagStyle(selector, content))
        else:
            for style_rule in content:
                sr: StyleRule | None = self.get_style_rule(tag_style.style_rules, style_rule)

                if not sr:
                    tag_style.style_rules.append(style_rule)
                else:
                    sr.value = style_rule.value

    def parse_class_selector(self, selector: str, content: list[StyleRule]) -> None:
        class_style: ClassStyle | None = self.get_class_style(selector)

        if not class_style:
            self.class_styles.append(ClassStyle(selector[1:], content))
        else:
            for style_rule in content:
                sr: StyleRule | None = self.get_style_rule(class_style.style_rules, style_rule)

                if not sr:
                    class_style.style_rules.append(style_rule)
                else:
                    sr.value = style_rule.value

    def parse_id_selector(self, selector: str, content: list[StyleRule]) -> None:
        id_style: IdStyle | None = self.get_id_style(selector)

        if not id_style:
            self.id_styles.append(IdStyle(selector[1:], content))
        else:
            for style_rule in content:
                sr: StyleRule | None = self.get_style_rule(id_style.style_rules, style_rule)

                if not sr:
                    id_style.style_rules.append(style_rule)
                else:
                    sr.value = style_rule.value

    def handle_parsed_selector(self, selector: str, content: list[StyleRule], is_default: bool = False) -> None:
        if is_default and (selector[0] == "." or selector[0] == "#"):
            return

        if selector == "*":
            self.parse_root_selector(content)
        elif selector[0] == ".":
            self.parse_class_selector(selector, content)
        elif selector[0] == "#":
            self.parse_id_selector(selector, content)
        else:
            if is_default:
                self.parse_default_tag_selector(selector, content)

                return

            self.parse_tag_selector(selector, content)

    def parser(self, css_string: str, is_default: bool = False) -> None:
        parsed_selector: str = ""
        is_in_selector: bool = False

        property_name: str = ""
        property_value: str = ""
        content: list[StyleRule] = []
        is_in_property_value: bool = False

        for i in range(len(css_string)):
            letter: str = css_string[i]

            if is_in_selector:
                if letter == "}":
                    is_in_selector = False

                    if len(property_value) > 0:
                        content.append(StyleRule(property_name, property_value))

                        property_name = ""
                        property_value = ""

                    self.handle_parsed_selector(parsed_selector, content, is_default=is_default)

                    parsed_selector = ""
                    content = []

                    continue
                
                if is_in_property_value:
                    if letter == ";":
                        is_in_property_value = False

                        content.append(StyleRule(property_name, property_value))

                        property_name = ""
                        property_value = ""

                        continue

                    property_value += letter

                    continue

                if letter == ":":
                    is_in_property_value = True

                    continue

                property_name += letter

                continue

            if letter == "{":
                is_in_selector = True

                continue

            parsed_selector += letter

    
    def __polish_css_string(self, css_string: str) -> str:
        polished_css_string: str = ""

        css_string = css_string.replace("\n", "")
        css_string = css_string.replace("\t", "")
        css_string = css_string.replace("\r", "")

        for i in range(len(css_string)):
            letter: str = css_string[i]

            if letter == " ":
                continue

            polished_css_string += letter

        return polished_css_string

    def parse_inline_style(self, inline_style_raw: str, ui_element: Any) -> dict:
        inline_style: dict = {}

        property_name: str = ""
        property_value: str = ""

        is_value: bool = False

        for letter in inline_style_raw:
            if letter == ":":
                is_value = True

                continue
            
            if letter == ";":
                is_value = False

                inline_style[property_name] = property_value

                property_name = ""
                property_value = ""

                continue

            if is_value:
                property_value += letter
            else:
                if letter == " ":
                    continue

                property_name += letter
        
        if len(property_name) > 0:
            inline_style[property_name] = property_value
        
        applied_inline_style: dict = {}

        for key, value in inline_style.items():
            if value.count("{") > 0 and value.count("}") > 0:
                self.state_parser.detect_state(ui_element, value, f"css.{key}", True)

                continue

            style_rule: StyleRule = StyleRule(key, value)

            self.apply_style_rule(applied_inline_style, style_rule)

        return applied_inline_style

    def parse_reactive_inline_style(self, reactive_inline_style: dict, inline_style: dict) -> None:
        if not hasattr(self, "_temp_style_rule"):
            self._temp_style_rule = StyleRule("", "")

        for key, value in reactive_inline_style.items():
            self._temp_style_rule.name = key
            self._temp_style_rule.value = value

            if not value or value == "None":
                continue

            self.apply_style_rule(inline_style, self._temp_style_rule)

    def overwrite_main_style(self, main_style: dict, overwrite: dict) -> None:
        for key, value in overwrite.items():
            main_style[key] = value

    def apply_style_rule(self, style: dict, style_rule: StyleRule) -> None:
        style_rule.value = style_rule.value.replace(" ", "")

        match style_rule.name:
            case "color":
                style["color"] = self.get_pygame_color(style_rule.value)
            case "font-family":
                style["font-family"] = self.get_pygame_font(style_rule.value)
            case "font-size":
                style["font-size"] = self.get_pygame_font_size(style_rule.value)
            case "font-weight":
                style["font-weight"] = self.get_pygame_font_weight(style_rule.value)
            case "font-style":
                style["font-style"] = self.get_pygame_font_style(style_rule.value)
            case "background-color":
                style["background-color"] = self.get_pygame_color(style_rule.value)
            case "padding-top":
                style["padding-top"] = self.get_pygame_onevalue_size(style_rule.value)
            case "padding-right":
                style["padding-right"] = self.get_pygame_onevalue_size(style_rule.value)
            case "padding-bottom":
                style["padding-bottom"] = self.get_pygame_onevalue_size(style_rule.value)
            case "padding-left":
                style["padding-left"] = self.get_pygame_onevalue_size(style_rule.value)
            case "padding":
                padding: list[int] = self.get_pygame_padding(style_rule.value)

                style["padding-top"] = padding[0]
                style["padding-right"] = padding[1]
                style["padding-bottom"] = padding[2]
                style["padding-left"] = padding[3]
            case "margin-top":
                style["margin-top"] = self.get_pygame_onevalue_size(style_rule.value)
            case "margin-right":
                style["margin-right"] = self.get_pygame_onevalue_size(style_rule.value)
            case "margin-bottom":
                style["margin-bottom"] = self.get_pygame_onevalue_size(style_rule.value)
            case "margin-left":
                style["margin-left"] = self.get_pygame_onevalue_size(style_rule.value)
            case "margin":
                margin: list[int] = self.get_pygame_padding(style_rule.value)

                style["margin-top"] = margin[0]
                style["margin-right"] = margin[1]
                style["margin-bottom"] = margin[2]
                style["margin-left"] = margin[3]
            case "border-top-left-radius":
                style["border-top-left-radius"] = self.get_pygame_onevalue_size(style_rule.value)
            case "border-top-right-radius":
                style["border-top-right-radius"] = self.get_pygame_onevalue_size(style_rule.value)
            case "border-bottom-left-radius":
                style["border-bottom-left-radius"] = self.get_pygame_onevalue_size(style_rule.value)
            case "border-bottom-right-radius":
                style["border-bottom-right-radius"] = self.get_pygame_onevalue_size(style_rule.value)
            case "border-radius":
                radius: list[int] = self.get_pygame_border_radius(style_rule.value)

                style["border-top-left-radius"] = radius[0]
                style["border-top-right-radius"] = radius[1]
                style["border-bottom-left-radius"] = radius[2]
                style["border-bottom-right-radius"] = radius[3]
            case "position":
                style["position"] = self.get_pygame_position(style_rule.value)
            case "left":
                style["left"] = self.get_pygame_onevalue_size(style_rule.value)
                style["right"] = -1
            case "top":
                style["top"] = self.get_pygame_onevalue_size(style_rule.value)
                style["bottom"] = -1
            case "right":
                style["right"] = self.get_pygame_onevalue_size(style_rule.value)
                style["left"] = -1
            case "bottom":
                style["bottom"] = self.get_pygame_onevalue_size(style_rule.value)
                style["top"] = -1
            case "width":
                style["width"] = self.get_pygame_onevalue_size(style_rule.value)
            case "height":
                style["height"] = self.get_pygame_onevalue_size(style_rule.value)
            case "display":
                style["display"] = self.get_pygame_display(style_rule.value)
            case "align-items":
                style["align-items"] = self.get_pygame_align_items(style_rule.value)
            case "cursor":
                style["cursor"] = self.get_pygame_cursor(style_rule.value)
            case "visibility":
                style["visibility"] = self.get_pygame_visibility(style_rule.value)
            case "scale":
                style["scale"] = self.get_pygame_scale(style_rule.value)
            case "transition":
                style["transition"] = self.get_pygame_transition(style_rule.value)
            case "translate":
                style["translate"] = self.get_pygame_translate(style_rule.value)
            case "text-align":
                style["text-align"] = self.get_pygame_text_align(style_rule.value)
            case "text-decoration-line":
                style["text-decoration-line"] = self.get_pygame_text_decoration(style_rule.value)
            case "text-decoration-color":
                style["text-decoration-color"] = self.get_pygame_color(style_rule.value)
            case "text-decoration-thickness":
                style["text-decoration-thickness"] = self.get_pygame_onevalue_size(style_rule.value)
            case "text-decoration":
                output_decoration: tuple = self.get_pygame_text_decoration_multi(style_rule.value)

                style["text-decoration-line"] = output_decoration[0]
                style["text-decoration-color"] = output_decoration[1]
                style["text-decoration-thickness"] = output_decoration[2]

    def get_style(self, _type: str, classes: list[str], _id: str, modifiers: dict) -> dict:
        cached_style: dict | None = get_style(_type, classes, _id, modifiers)

        if cached_style:
            return cached_style

        style: dict = {
            "color": (0, 0, 0, 0),
            "font-family": "timesnewroman",
            "font-size": 0,
            "font-weight": 400,
            "font-style": "normal",
            "background-color": (0, 0, 0, 0),
            "padding-top": 0,
            "padding-right": 0,
            "padding-bottom": 0,
            "padding-left": 0,
            "margin-top": 0,
            "margin-right": 0,
            "margin-bottom": 0,
            "margin-left": 0,
            "border-top-left-radius": 0,
            "border-top-right-radius": 0,
            "border-bottom-left-radius": 0,
            "border-bottom-right-radius": 0,
            "border-color": (0, 0, 0, 0),
            "border-width": 0,
            "position": "static",
            "left": 0,
            "top": 0,
            "right": 0,
            "bottom": 0,
            "width": 0,
            "height": 0,
            "display": "block",
            "align-items": "stretch",
            "cursor": "default",
            "visibility": "visible",
            "scale": 1,
            "transition": {},
            "translate": (0, 0),
            "text-align": "left",
            "text-decoration-line": "none",
            "text-decoration-color": None,
            "text-decoration-thickness": 2
        }

        if modifiers.get("input_type", "") in ["text", "password", "number"]:
            style["cursor"] = "text"

        for tag_style in self.default_style:
            if not tag_style.selector == _type:
                continue

            for style_rule in tag_style.style_rules:
                self.apply_style_rule(style, style_rule)

            break

        for style_rule in self.global_style:
            self.apply_style_rule(style, style_rule)
        
        for tag_style in self.tag_styles:
            if not tag_style.selector == _type:
                continue
            
            for style_rule in tag_style.style_rules:
                self.apply_style_rule(style, style_rule)

            break

        for class_style in self.class_styles:
            if not class_style.style_class in classes:
                continue

            for style_rule in class_style.style_rules:
                self.apply_style_rule(style, style_rule)

        for id_style in self.id_styles:
            if not id_style.style_id == _id:
                continue

            for style_rule in id_style.style_rules:
                self.apply_style_rule(style, style_rule)

            break

        for modifier, state in modifiers.items():
            if not state:
                continue

            mod: str = _type + ":" + modifier

            for tag_style in self.default_style:
                if not tag_style.selector == mod:
                    continue

                for style_rule in tag_style.style_rules:
                    self.apply_style_rule(style, style_rule)

                break
            
            for tag_style in self.tag_styles:
                if not tag_style.selector == mod and not tag_style.selector == "*:hover":
                    continue
            
                for style_rule in tag_style.style_rules:
                    self.apply_style_rule(style, style_rule)

                break

            _classes: list[str] = []

            for _class in classes:
                _classes.append(_class + ":" + modifier)

            for class_style in self.class_styles:
                if not class_style.style_class in _classes:
                    continue

                for style_rule in class_style.style_rules:
                    self.apply_style_rule(style, style_rule)

            for id_style in self.id_styles:
                if not id_style.style_id == _id + ":" + modifier:
                    continue

                for style_rule in id_style.style_rules:
                    self.apply_style_rule(style, style_rule)

                break

        add_style(_type, classes, _id, modifiers, copy.deepcopy(style))

        return style

    def __unit_split(self, string: str) -> list[str]:
        final: list[str] = []

        builded_word: str = ""
        for letter in string:
            if letter.isdigit():
                if len(builded_word) > 0 and (builded_word[len(builded_word) - 1].isalpha() or builded_word[len(builded_word) - 1] == "%"):
                    final.append(builded_word)

                    builded_word = ""
            
            builded_word += letter
        
        if len(builded_word) > 0:
            final.append(builded_word)

        return final

    def __get_time_unit_number(self, unit_string: str) -> float:
        if unit_string.endswith("ms"):
            return float(unit_string[:len(unit_string) - 2])
        elif unit_string.endswith("s"):
            return float(unit_string[:len(unit_string) - 1]) * 1_000

        return 0

    def get_pygame_text_decoration_multi(self, multi_text_decoration: str) -> tuple[str, tuple[int, int, int] | tuple[int, int, int, int] | None, int]:
        if multi_text_decoration.startswith("none"):
            return ("none", None, 2)
        
        does_start: bool = False
        line: str = "none"

        if multi_text_decoration.startswith("underline"):
            line = "underline"
            does_start = True
        elif multi_text_decoration.startswith("overline"):
            line = "overline"
            does_start = True
        elif multi_text_decoration.startswith("line-through"):
            line = "line-through"
            does_start = True
        
        if not does_start:
            return ("none", None, 2)
        
        multi_text_decoration = multi_text_decoration.replace(line, "", 1)

        r_number: str = ""

        if multi_text_decoration.endswith("px"):
            for i in range(len(multi_text_decoration) - 2):
                letter = multi_text_decoration[len(multi_text_decoration) - 3 - i]

                if letter.isalpha() or letter == ")":
                    break

                r_number += letter

        number: str = ""

        for i in range(len(r_number)):
            number += r_number[len(r_number) - 1 - i]

        number += "px"

        multi_text_decoration = multi_text_decoration.replace(number, "", 1)

        return (line, self.get_pygame_color(multi_text_decoration), self.get_pygame_onevalue_size(number))

    def get_pygame_text_decoration(self, text_decoration: str) -> str:
        if text_decoration == "none" or text_decoration == "underline" or text_decoration == "overline" or text_decoration == "line-through":
            return text_decoration
        
        return "none"

    def get_pygame_text_align(self, text_align: str) -> str:
        if text_align == "left" or text_align == "right" or text_align == "center":
            return text_align
        
        return "left"

    def get_pygame_translate(self, translate: str) -> tuple[int | str, int | str]:
        params: list[int | str] = []

        num: str = ""

        is_unit: bool = False

        for letter in translate:
            if letter.isdigit() or letter == "-":
                if is_unit:
                    is_unit = False

                    params.append(num)

                    num = ""

                num += letter
            else:
                if len(num) > 0:
                    is_unit = True
                    num += letter
        
        if len(num) > 0:
            params.append(num)
        
        for i in range(len(params)):
            params[i] = self.get_pygame_onevalue_size(params[i])
        
        if len(params) == 1:
            params.append(0)
        elif len(params) > 2:
            params = params[:2]

        return tuple(params)

    def get_pygame_transition(self, transition: str) -> dict:
        o_transition: dict = {}

        pro_type: str = ""
        pro_duration: str = ""
        pro_ease: str = ""
        pro_delay: str = ""

        is_type: bool = False
        is_dur: bool = False
        is_del: bool = False
        is_ease: bool = False

        is_start: bool = False
        skip_next: bool = False

        for letter in transition:
            if letter == ",":
                o_transition[pro_type] = [self.__get_time_unit_number(pro_duration), pro_ease, self.__get_time_unit_number(pro_delay)]

                pro_type = ""
                pro_duration = ""
                pro_ease = ""
                pro_delay = ""

                is_start = False
                is_ease = False
                is_del = False
                is_dur = False
                is_type = False

                continue

            if skip_next:
                skip_next = False

                continue

            if letter.isalpha():
                if is_dur and (letter == "s" or letter == "m"):
                    pro_duration += letter

                    if letter == "m":
                        pro_duration += "s"

                        skip_next = True
                    
                    is_start = True
                    is_dur = False

                    continue
                elif is_del and (letter == "s" or letter == "m"):
                    pro_delay += letter

                    if letter == "m":
                        pro_delay += "s"

                        skip_next = True
                    
                    is_ease = True
                    is_del = False
                    
                    continue
                else:
                    if is_start:
                        is_ease = True
                    else:
                        is_type = True
            
            if letter.isdigit():
                if is_type:
                    is_type = False

                    is_dur = True
                
                if is_start:
                    is_del = True
                
                is_ease = False

            if is_type:
                pro_type += letter
            
            if is_dur:
                pro_duration += letter
            
            if is_del:
                pro_delay += letter
            
            if is_ease:
                pro_ease += letter

        if len(pro_type) > 0:
            o_transition[pro_type] = [self.__get_time_unit_number(pro_duration), pro_ease, self.__get_time_unit_number(pro_delay)]

        f_o_transition: dict = {}

        for o_key, o_item in o_transition.items():
            f_o_transition[o_key] = o_item

            if o_key == "border-radius":
                f_o_transition["border-top-left-radius"] = o_item
                f_o_transition["border-top-right-radius"] = o_item
                f_o_transition["border-bottom-left-radius"] = o_item
                f_o_transition["border-bottom-right-radius"] = o_item
            elif o_key == "padding":
                f_o_transition["padding-bottom"] = o_item
                f_o_transition["padding-top"] = o_item
                f_o_transition["padding-left"] = o_item
                f_o_transition["padding-right"] = o_item
            elif o_key == "margin":
                f_o_transition["margin-bottom"] = o_item
                f_o_transition["margin-top"] = o_item
                f_o_transition["margin-left"] = o_item
                f_o_transition["margin-right"] = o_item

        return f_o_transition

    def get_pygame_scale(self, scale: str) -> float:
        try:
            s: float = float(scale)

            if s < 0:
                return 0
            elif s > 100:
                return 100
            
            return s
        except:
            pass
        
        return 1

    def get_pygame_visibility(self, visibility: str) -> str:
        if visibility == "visible" or visibility == "hidden":
            return visibility
        
        return "hidden"

    def get_pygame_cursor(self, cursor: str) -> str:
        if cursor == "default" or cursor == "pointer" or cursor == "text" or cursor == "wait" or cursor == "crosshair" or cursor == "move":
            return cursor
        
        if cursor.startswith("url(") and cursor.endswith(")"):
            return cursor
        
        return "default"

    def get_pygame_align_items(self, align_items: str):
        if align_items == "stretch" or align_items == "end" or align_items == "start" or align_items == "center":
            return align_items
        
        if align_items == "flex-end":
            return "end"
        
        if align_items == "flex-start":
            return "start"
        
        return "stretch"

    def get_pygame_display(self, display: str) -> str:
        if display == "inline" or display == "block" or display == "none":
            return display
        
        return "block"

    def get_pygame_position(self, position: str) -> str:
        if position == "absolute" or position == "relative":
            return position
        
        return "static"

    def get_pygame_border_radius(self, border_radius: str) -> tuple[int, int, int, int]:
        border_radiuses: list[str] = self.__unit_split(border_radius)

        if len(border_radiuses) == 1:
            radius: int = self.get_pygame_onevalue_size(border_radiuses[0])

            return (radius, radius, radius, radius)
        elif len(border_radiuses) == 2:
            tlbr: int = self.get_pygame_onevalue_size(border_radiuses[0])
            trbl: int = self.get_pygame_onevalue_size(border_radiuses[1])

            return (tlbr, trbl, trbl, tlbr)
        elif len(border_radiuses) == 3:
            tl: int = self.get_pygame_onevalue_size(border_radiuses[0])
            trbl: int = self.get_pygame_onevalue_size(border_radiuses[1])
            br: int = self.get_pygame_onevalue_size(border_radiuses[2])

            return (tl, trbl, trbl, br)
        elif len(border_radiuses) == 4:
            tl: int = self.get_pygame_onevalue_size(border_radiuses[0])
            tr: int = self.get_pygame_onevalue_size(border_radiuses[1])
            br: int = self.get_pygame_onevalue_size(border_radiuses[2])
            bl: int = self.get_pygame_onevalue_size(border_radiuses[3])

            return (tl, tr, bl, br)

        return (0, 0, 0, 0)

    def get_pygame_padding(self, padding: str) -> tuple[int, int, int, int]:
        paddings: list[str] = self.__unit_split(padding)

        if len(paddings) == 1:
            padding: int = self.get_pygame_onevalue_size(paddings[0])

            return (padding, padding, padding, padding)
        elif len(paddings) == 2:
            padding_vertical: int = self.get_pygame_onevalue_size(paddings[0])
            padding_horizontal: int = self.get_pygame_onevalue_size(paddings[1])

            return (padding_vertical, padding_horizontal, padding_vertical, padding_horizontal)
        elif len(paddings) == 3:
            padding_top: int = self.get_pygame_onevalue_size(paddings[0])
            padding_horizontal: int = self.get_pygame_onevalue_size(paddings[1])
            padding_bottom: int = self.get_pygame_onevalue_size(paddings[2])

            return (padding_top, padding_horizontal, padding_bottom, padding_horizontal)
        elif len(paddings) == 4:
            padding_top: int = self.get_pygame_onevalue_size(paddings[0])
            padding_right: int = self.get_pygame_onevalue_size(paddings[1])
            padding_bottom: int = self.get_pygame_onevalue_size(paddings[2])
            padding_left: int = self.get_pygame_onevalue_size(paddings[3])

            return (padding_top, padding_right, padding_bottom, padding_left)

        return (0, 0, 0, 0)

    def get_pygame_onevalue_size(self, size: str) -> int:
        if size == "0":
            return 0

        if size.endswith("px"):
            return int(size[:len(size) - 2])

        return size

    def get_pygame_font_style(self, style: str) -> str:
        if style == "italic" or style == "normal":
            return style
        
        if style == "oblique":
            return "italic"
        
        return "normal"

    def get_pygame_font_weight(self, weight: str) -> int:
        if weight == "bold" or weight == "bolder":
            return 700

        if weight == "normal" or weight == "lighter":
            return 400
        
        try:
            weight_number: int = int(weight)

            weight_number = math.floor(weight_number / 100) * 100

            if weight_number < 100 or weight_number > 900:
                return 400
            
            return weight_number
        except:
            return 400

    def get_pygame_font_size(self, size: str) -> int:
        if size.endswith("px"):
            return int(size[:len(size) - 2])

        return size

    def get_pygame_font(self, css_font: str) -> str:
        css_font: str = css_font.strip().lower()

        if css_font[0] == '"':
            css_font = css_font[1:len(css_font) - 1]

        if css_font in pygame.sysfont.get_fonts():
            return css_font
        
        if css_font.startswith("url(") and css_font.endswith(")"):
            return css_font

        return "timesnewroman"

    def get_pygame_color(self, css_color: str) -> tuple[int, int, int] | tuple[int, int, int, int]:
        css_color: str = css_color.strip().lower()

        if css_color in CSS_NAMED_COLORS:
            return CSS_NAMED_COLORS[css_color]

        if css_color.startswith("rgb") and not css_color.startswith("rgba"):
            rgb_color: str = css_color[4:len(css_color) - 1]
            
            rgb: list[str] = rgb_color.split(",")

            if len(rgb) < 2:
                return (0, 0, 0)

            return (int(rgb[0]), int(rgb[1]), int(rgb[2]))

        if css_color.startswith("rgba"):
            rgba_color: str = css_color[5:len(css_color) - 1]

            rgba: list[str] = rgba_color.split(",")

            if len(rgba) < 3:
                return (0, 0, 0, 0)

            return (int(rgba[0]), int(rgba[1]), int(rgba[2]), int(float(rgba[3]) * 100))

        if css_color.startswith("#"):
            hex_value: str = css_color[1:]

            if len(hex_value) == 3:
                r: int = int(hex_value[0] * 2, 16)
                g: int = int(hex_value[1] * 2, 16)
                b: int = int(hex_value[2] * 2, 16)

                return (r, g, b)
            elif len(hex_value) == 4:
                r: int = int(hex_value[0]*2, 16)
                g: int = int(hex_value[1]*2, 16)
                b: int = int(hex_value[2]*2, 16)
                a: int = int(hex_value[3]*2, 16)

                return (r, g, b, a)
            elif len(hex_value) == 6:
                r: int = int(hex_value[0:2], 16)
                g: int = int(hex_value[2:4], 16)
                b: int = int(hex_value[4:6], 16)

                return (r, g, b)
            elif len(hex_value) == 8:
                r: int = int(hex_value[0:2], 16)
                g: int = int(hex_value[2:4], 16)
                b: int = int(hex_value[4:6], 16)
                a: int = int(hex_value[6:8], 16)

                return (r, g, b, a)