"""Interactive arrow-key integration selector using readchar."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel


def select_integration(
    choices: list[tuple[str, str]],
    *,
    console: Console | None = None,
) -> str | None:
    """Display an interactive arrow-key selector for AI assistant integration.

    *choices* is a list of (key, display_name) tuples.
    Returns the selected key, or None if the user cancels (Esc).
    """
    import readchar

    if console is None:
        console = Console()

    selected = 0

    while True:
        _render_menu(console, choices, selected)

        key = readchar.readkey()

        if key == readchar.key.UP:
            selected = (selected - 1) % len(choices)
        elif key == readchar.key.DOWN:
            selected = (selected + 1) % len(choices)
        elif key in (readchar.key.ENTER, readchar.key.CR, readchar.key.LF):
            return choices[selected][0]
        elif key == readchar.key.ESC:
            return None
        elif key in ("\x03",):  # Ctrl+C
            raise KeyboardInterrupt

    return None


def _render_menu(
    console: Console,
    choices: list[tuple[str, str]],
    selected: int,
) -> None:
    """Render the menu panel."""
    lines = []
    for i, (key, display_name) in enumerate(choices):
        marker = "[bold cyan]\u25b6[/]  " if i == selected else "   "
        style = "bold bright_cyan" if i == selected else "dim"
        lines.append(f"  {marker}[{style}]{key} ({display_name})[/]")

    lines.append("")
    lines.append("  [dim]Use \u2191/\u2193 to navigate, Enter to select, Esc to cancel[/]")

    content = "\n".join(lines)
    panel = Panel(
        content,
        title="[bold]Choose your AI IDE:[/]",
        border_style="cyan",
        padding=(1, 2),
    )

    # Clear screen area and render
    console.clear()
    console.print(panel)
