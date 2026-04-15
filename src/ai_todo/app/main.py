from __future__ import annotations

from ai_todo.app.bootstrap import build_application, create_main_window


def main() -> None:
    context = build_application()
    root, window = create_main_window(context)

    def tick():
        if root.winfo_exists():
            window.refresh()
            root.after(context.config.reminder_poll_ms, tick)

    root.after(context.config.reminder_poll_ms, tick)
    root.mainloop()


if __name__ == "__main__":
    main()
