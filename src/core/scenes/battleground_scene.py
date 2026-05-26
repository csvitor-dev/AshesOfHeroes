from typing import Any
from OpenGL.GL import *
from pyglm import glm
import glfw

from src.core.event import EventManager
from src.core.scene import Scene, SceneManager
from src.core.animation import AnimationQueue
from src.graphics.camera import Camera
from src.graphics.rendering.renderer import Renderer
from src.graphics.texture_manager import TextureManager
from src.graphics.rendering.battleground_renderer import BattlegroundRenderer
from src.logic.game_state import GameState


class BattlegroundScene(Scene):
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
        self._animation_queue: AnimationQueue | None = None
        self._board: BattlegroundRenderer | None = None

    def on_enter(self, **params: Any) -> None:
        self._animation_queue = AnimationQueue()
        self._board = BattlegroundRenderer(
            renderer=self._renderer,
            event_manager=self._events,
            animation_queue=self._animation_queue,
            textures=TextureManager(),
            game_state=self._game_state,
        )
        self._board.load_assets()

    def on_exit(self) -> None:
        if self._board:
            self._board.unload_assets()
            self._board = None
        self._animation_queue = None

    def on_pause(self) -> None: ...

    def on_resume(self) -> None: ...

    def update(self, dt: float) -> None:
        if self._animation_queue:
            self._animation_queue.update(dt)

        if self._board:
            self._board.update(dt)

    def render(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self._board:
            self._board.render(
                proj3d = self._camera.projection(),
                view   = self._camera.view(),
                proj2d = self._camera.ortho(),
            )

    def handle_input(self) -> None: ...

    def on_key(self, key: int, action: int) -> None:
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            self._scenes.pop_scene()

    def on_mouse_move(self, mx: float, my: float) -> None:
        if self._board:
            self._board.on_mouse_move(mx, my)

    def on_mouse_click(self, mx: float, my: float) -> None:
        if self._board:
            self._board.on_mouse_click(mx, my)
