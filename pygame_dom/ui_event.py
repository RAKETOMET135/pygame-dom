from __future__ import annotations
from typing import Any

class UIEvent:
    def __init__(self, event_type: str, event_root: Any) -> UIEvent:
        self.event_type = event_type
        self.event_root = event_root

        self.key = None
        self.button = None
        self.delta_x = None
        self.delta_y = None
        self.unicode = None

        self.propagation = True
    
    def stop_propagation(self) -> None:
        """
        Prevents the event from propagating to parent elements
        """

        self.propagation = False