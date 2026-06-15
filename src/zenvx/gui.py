from __future__ import annotations

from .app import ZenvXApp


def run_gui() -> None:
    try:
        import PySide6  # type: ignore
        from .gui_qt import run_gui_qt
        run_gui_qt()
    except Exception:
        from .gui_tk import run_gui_tk
        run_gui_tk()
