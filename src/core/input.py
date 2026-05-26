from typing import Any, Callable
import glfw
from src.core.window import Window


class Input:

    def __init__(self, window: Window):
        self.__window = window
        self._on_key:          Callable[..., Any] | None = None
        self._on_mouse_move:   Callable[..., Any] | None = None
        self._on_mouse_click:  Callable[..., Any] | None = None

        self.__window.set_key_callback(self._key_callback)
        self.__window.set_cursor_pos_callback(self._mouse_move_callback)
        self.__window.set_mouse_button_callback(self._mouse_click_callback)

    def bind(
        self,
        on_key:          Callable[..., Any] | None = None,
        on_mouse_move:   Callable[..., Any] | None = None,
        on_mouse_click:  Callable[..., Any] | None = None,
    ) -> None:
        self._on_key = on_key
        self._on_mouse_move = on_mouse_move
        self._on_mouse_click = on_mouse_click

    def _key_callback(self, window: Any, key: int, scancode: int, action: int, mods: int) -> None:
        if self._on_key:
            self._on_key(key, action, mods)

    def _mouse_move_callback(self, window: Any, x: float, y: float) -> None:
        if self._on_mouse_move:
            self._on_mouse_move(x, y)

    def _mouse_click_callback(self, window: Any, button: int, action: int, mods: int) -> None:
        if action == glfw.PRESS and self._on_mouse_click:
            x, y = glfw.get_cursor_pos(window)
            self._on_mouse_click(button, x, y)
