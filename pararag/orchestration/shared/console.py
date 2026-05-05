from rich.console import Console as RichConsole
from functools import lru_cache
from enum import StrEnum

class Color(StrEnum):
    BLACK = "black"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = "white"

    BRIGHT_BLACK = "bright_black"
    BRIGHT_RED = "bright_red"
    BRIGHT_GREEN = "bright_green"
    BRIGHT_YELLOW = "bright_yellow"
    BRIGHT_BLUE = "bright_blue"
    BRIGHT_MAGENTA = "bright_magenta"
    BRIGHT_CYAN = "bright_cyan"
    BRIGHT_WHITE = "bright_white"

class Console:
    def __init__(self):
        self.console = RichConsole()
    
    def print(self, text: str, color: Color = Color.WHITE, bold: bool = False) -> None:
        if bold:    
            self.console.print(text, style=f"bold {color}")
        else:
            self.console.print(text, style=color)

@lru_cache(maxsize=1)
def get_console() -> Console:
    return Console()
