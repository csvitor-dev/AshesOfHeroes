from typing import Any
from OpenGL.GL import *
import glfw
from src.core.event import EventManager
from src.core.scene import Scene, SceneManager
from src.graphics.camera import Camera
from src.graphics.rendering.renderer import Renderer
from src.graphics.rendering.game_over_renderer import GameOverRenderer
from src.logic.game_state import GameState


class GameOverScene(Scene):
    def __init__(
        self,
        event_manager: EventManager,
        scene_manager: SceneManager,
        camera:        Camera,
        renderer:      Renderer,
        game_state:    GameState,
    ):
        super().__init__(event_manager, scene_manager, camera)
        self._renderer = renderer
        self._game_state = game_state
        self._game_over: GameOverRenderer | None = None
        self._t: float = 0.0

    def on_enter(self, **params: Any) -> None:
        self._t = 0.0
        self._game_over = GameOverRenderer(self._renderer, self._game_state.winner_side)
        self._game_over.load_assets()

    def on_exit(self) -> None:
        if self._game_over:
            self._game_over.unload_assets()
            self._game_over = None

    def on_pause(self) -> None: ...

    def on_resume(self) -> None:
        self._t = 0.0

    def update(self, dt: float) -> None:
        self._t += dt
        if self._game_over:
            self._game_over.update(self._t)

    def render(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT)
        if self._game_over:
            self._game_over.render(self._camera.ortho())

    def handle_input(self) -> None: ...

    def on_key(self, key: int, action: int, mods: int) -> None:
        if action == glfw.PRESS and key == glfw.KEY_ESCAPE:
            self._go_menu()

    def on_mouse_move(self, mx: float, my: float) -> None:
        if self._game_over:
            self._game_over.set_hover(mx, my)

    def on_mouse_click(self, button: int, mx: float, my: float) -> None:
        if not self._game_over:
            return
        if self._game_over.hit_test(mx, my) == "menu":
            self._go_menu()

    def _go_menu(self) -> None:
        self._scenes.pop_scene()
        self._scenes.pop_scene()
