from rich.console import Console as RichConsole
from functools import lru_cache
from typing import Sequence
from enum import StrEnum

from pararag.shared.models import MemoryEntry


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
    
    def print(
        self, 
        content: str | Sequence[object],
        *,
        color: Color = Color.WHITE, 
        bold: bool = False, 
        empty_line: bool = False,
        end: str = "\n"
     ) -> None:
        """Utility function for pretty printing. Handles strings and sequences as content"""

        style = f"bold {color}" if bold else color

        if isinstance(content, Sequence) and not isinstance(content, str):
            for item in content:
                self.console.print(str(item), style=style, end=end)
        else:
            self.console.print(str(content), style=style, end=end)
        
        if empty_line:
            self.console.print()
    
    def print_queries(self, queries: list[str]) -> None:
        if len(queries) > 0:
            self.print("Decomposition into sub-queries: ", color=Color.BRIGHT_MAGENTA, bold=True)
            self.print(queries, color=Color.BRIGHT_MAGENTA, empty_line=True)

    def print_memories(self, memories: list[MemoryEntry]) -> None:
        if len(memories) > 0:
            self.print("Obtained memories: ", color=Color.MAGENTA, bold=True)
            self.print(memories, color=Color.MAGENTA, empty_line=True)
    
    def print_assertions(self, assertions: list[str]) -> None:
        if len(assertions) > 0:
            self.print("The following assertions were extracted: ", color=Color.MAGENTA, bold=True)
            self.print(assertions, color=Color.MAGENTA, empty_line=True)
    
    def print_assistant_msg(self, text: str) -> None:
        self.print(f"Assistant: {text}", color=Color.BLUE, bold=True, empty_line=True)
        
    def print_prompt_user(self) -> None:
        self.print(f"User: ", color=Color.BRIGHT_WHITE, bold=True, end="")
    
    def print_deduplication(self, assertions: list[str]) -> None:
        if len(assertions) > 0:
            self.print("The following assertions are droped by deduplication: ", color=Color.RED, bold=True)
            self.print(assertions, color=Color.RED, empty_line=True)


@lru_cache(maxsize=1)
def get_console() -> Console:
    return Console()
