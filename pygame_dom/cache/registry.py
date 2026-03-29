import inspect
from typing import Callable
from pygame_dom.ui_event import UIEvent

FUNCTION_REGISTRY: dict = {}

def exec_function(function_name: str, event: UIEvent) -> None:
    func: Callable = FUNCTION_REGISTRY.get(function_name)

    if not func:
        return

    sig: inspect.Signature = inspect.signature(func)

    if len(sig.parameters) == 0:
        func()
    else:
        func(event)

def add_function(func: Callable, function_name: str | None = None) -> None:
    FUNCTION_REGISTRY[function_name or func.__name__] = func