"""ASCII art banner for autonomous-sdlc CLI."""

from rich.align import Align
from rich.console import Console
from rich.text import Text

BANNER = r"""
               ___ ___ ____
   _____  ____/ / / / / __/
  / ___/ / __  / / / / /
 (__  ) / /_/ / / / / /___
/____/  \__,_/ /_/  \____/
"""

TAGLINE = "Autonomous SDLC -- Bootstrap multi-agent AI development into any repo"


def print_banner(console: Console | None = None) -> None:
    """Print the autonomous-sdlc ASCII banner with colors."""
    if console is None:
        console = Console()

    banner_lines = BANNER.strip().split("\n")
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()
