import inspect
from typing import Callable, Any
from pygame_dom.ui_event import UIEvent

FUNCTION_REGISTRY: dict = {}
STATE_REGISTRY: dict = {}
PAGES: dict = {}

class DuplicateStateError(Exception):
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