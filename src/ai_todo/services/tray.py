from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from threading import Thread


@dataclass(slots=True)
class TrayCallbacks:
    show_main_window: Callable[[], None]
    quit_application: Callable[[], None]


class TrayService:
    def __init__(self) -> None:
        self._icon = None

    def start(self, callbacks: TrayCallbacks) -> None:
        try:
            import pystray
            from PIL import Image, ImageDraw
        except Exception:
            return

        def create_image():
            image = Image.new("RGB", (64, 64), color=(26, 95, 180))
            draw = ImageDraw.Draw(image)
            draw.rectangle((14, 14, 50, 50), outline="white", width=4)
            draw.line((22, 34, 30, 42, 44, 24), fill="white", width=4)
            return image

        menu = pystray.Menu(
            pystray.MenuItem(
                "显示主窗口",
                lambda _icon=None, _item=None: callbacks.show_main_window(),
            ),
            pystray.MenuItem("退出", lambda _icon=None, _item=None: callbacks.quit_application()),
        )
        self._icon = pystray.Icon("ai-todo", create_image(), "AI Todo", menu)
        Thread(target=self._icon.run, daemon=True).start()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
