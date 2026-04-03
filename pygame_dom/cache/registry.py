import inspect
import pygame
from typing import Callable, Any
from pygame_dom.ui_event import UIEvent

FUNCTION_REGISTRY: dict = {}
STATE_REGISTRY: dict = {}
BIND_REGISTRY: dict = {}
PAGES: dict = {}
RADIO_INPUTS: dict = {}
FRAMEWORK_IMAGES: dict = {}

class DuplicateStateError(Exception):
    pass

class DuplicateBindError(Exception):
    pass

def exec_function(function_name: str, event: UIEvent) -> None:
    func: Callable | None = FUNCTION_REGISTRY.get(function_name)

    if not func:
        return

    sig: inspect.Signature = inspect.signature(func)

    if len(sig.parameters) == 0:
        func()
    else:
        func(event)

def add_function(func: Callable, function_name: str | None = None) -> None:
    FUNCTION_REGISTRY[function_name or func.__name__] = func

def add_page(page: Any) -> None:
    PAGES[len(PAGES)] = page

    page.state_parser.render_all_states()

def add_state(state: Any) -> None:
    existing_state: Any | None = STATE_REGISTRY.get(state.name)

    if existing_state:
        raise DuplicateStateError(f"State '{state.name}' already exists")
    
    STATE_REGISTRY[state.name] = state

    for page in PAGES.values():
        page.state_parser.on_state_created_by_user(state.name)

def get_state(state_name: str) -> Any | None:
    state: Any | None = STATE_REGISTRY.get(state_name)

    return state

def state_update(state_name: str) -> None:
    for page in PAGES.values():
        page.state_parser.on_state_created_by_user(state_name)

def add_bind(bind: Any) -> None:
    existing_binds: list | None = BIND_REGISTRY.get(bind.name)

    if not existing_binds:
        BIND_REGISTRY[bind.name] = [bind]
    else:
        BIND_REGISTRY[bind.name].append(bind)

def update_bind(bind_name: str, new_value: Any) -> None:
    binds: list | None = BIND_REGISTRY.get(bind_name)

    if not binds:
        return
    
    for bind in binds:
        bind._value = new_value

def add_radio_input(radio_input: Any) -> None:
    key: str = radio_input.name

    if key == "":
        return

    if key in RADIO_INPUTS:
        RADIO_INPUTS[key].append(radio_input)
    else:
        RADIO_INPUTS[key] = [radio_input]

def get_radio_inputs(name: str) -> Any | None:
    if name in RADIO_INPUTS:
        return RADIO_INPUTS[name]

    return None

def add_framework_image(surface: pygame.Surface, name: str) -> None:
    FRAMEWORK_IMAGES[name] = surface

def get_framework_image(name: str) -> pygame.Surface | None:
    if name in FRAMEWORK_IMAGES:
        return FRAMEWORK_IMAGES[name]
    
    return None