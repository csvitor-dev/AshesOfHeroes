from typing import Any
from OpenGL.GL import *
import glfw
from src.core.event import EventManager
from src.core.scene import Scene, SceneManager
from src.graphics.rendering.renderer import Renderer
from src.graphics.rendering.menu_renderer import MenuRenderer


class MenuScene(Scene):

    def __init__(self, event_manager: EventManager, scene_manager: SceneManager, renderer: Renderer):
        super().__init__(event_manager, scene_manager)
        self._renderer = renderer
        self._menu: MenuRenderer | None = None
        self._t: float = 0.0

    def on_enter(self, **params: Any) -> None:
        self._t = 0.0
        self._menu = MenuRenderer(self._renderer)
        self._menu.load_assets()

    def on_exit(self) -> None:
        if self._menu:
            self._menu.unload_assets()
            self._menu = None

    def on_pause(self) -> None: ...

    def on_resume(self) -> None:
        self._t = 0.0

    def update(self, dt: float) -> None:
        self._t += dt
        if self._menu:
            self._menu.update(self._t)

    def render(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT)
        if self._menu:
            self._menu.render()

    def handle_input(self) -> None:
        ...

    def on_key(self, key: int, action: int) -> None:
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ENTER or key == glfw.KEY_SPACE:
            self._go_battle()
        if key == glfw.KEY_ESCAPE:
            self._exit_game()

    def on_mouse_click(self, mx: float, my: float) -> None:
        if self._menu:
            hit = self._menu.hit_test(mx, my)
            if hit == "battle":
                self._go_battle()
            elif hit == "exit":
                self._exit_game()

    def on_mouse_move(self, mx: float, my: float) -> None:
        if self._menu:
            self._menu.set_hover(mx, my)

    def _go_battle(self) -> None:
        self._scenes.push_by_key("battle_ground")

    def _exit_game(self) -> None:
        self._scenes.clear()
