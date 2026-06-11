from rich.console import Console as RichConsole
from functools import lru_cache
from typing import Sequence
from enum import StrEnum
from dotenv import find_dotenv, load_dotenv
import os

from pararag.shared.models import MemoryEntry

load_dotenv(find_dotenv())

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
    def __init__(self, record: bool = False):
        self.console = RichConsole(record=record)
    
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
    
    def print_queries(self, queries: list[str], query: str) -> None:
        if len(queries) > 0:
            self.print(f"Decomposing '{query}' into sub-queries: ", color=Color.BRIGHT_MAGENTA, bold=True)
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
    
    def print_locomo_msg(self, content: str, speaker: str, id: str) -> None:
        self.print(f"{speaker}: ", color=Color.BRIGHT_WHITE, bold=True, end="")
        self.print(f"{content} [{id}]", color=Color.BRIGHT_WHITE, empty_line=True)
        
    def print_prompt_user(self) -> None:
        self.print(f"User: ", color=Color.BRIGHT_WHITE, bold=True, end="")
    
    def print_deduplication(self, memories_with_decisions: list[dict]) -> None:
        if len(memories_with_decisions) > 0:
            self.print("Results of deduplication: ", color=Color.MAGENTA, bold=True)

            for memory in memories_with_decisions:
                if memory["decision"] == "yes":
                    self.print(f"{memory['memory']} (added, reason: {memory['reason']})", color=Color.GREEN, empty_line=True)

                elif memory["decision"] == "no":
                    self.print(f"{memory['memory']} (dropped, reason: {memory['reason']})", color=Color.RED, empty_line=True)
    
    def print_profile_update(self, user: str, previous_profile: str, new_profile: str) -> None:
        self.print(f"Updating {user} profile", color=Color.GREEN, bold=True)
        self.print(previous_profile, color=Color.BRIGHT_GREEN)
        self.print(new_profile, color=Color.GREEN, empty_line=True)
    
    def print_exception(self, exc: Exception) -> None:
        content =f"Error [{type(exc).__name__}]: {str(exc)}"
        self.print(content, color=Color.RED, empty_line=True)
    
    def save_html(self, path: str) -> None:
        self.console.save_html(path)


@lru_cache(maxsize=1)
def get_console() -> Console:
    record = True if os.getenv("FOR_LOCOMO") == "true" else False
    return Console(record=record)
