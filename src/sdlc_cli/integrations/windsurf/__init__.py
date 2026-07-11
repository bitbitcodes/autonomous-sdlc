"""Deprecated module — Windsurf was rebranded to Devin Desktop (June 2026).

Kept only so `from sdlc_cli.integrations.windsurf import WindsurfIntegration`
does not break for anyone importing it directly. New code should use
`sdlc_cli.integrations.devin.DevinDesktopIntegration`. The CLI itself
registers the "windsurf" key as an alias in that module — importing this
one does not re-register anything.
"""

from ..devin import DevinDesktopIntegration as WindsurfIntegration  # noqa: F401
