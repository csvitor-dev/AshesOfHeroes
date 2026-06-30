from typing import Any
from OpenGL.GL import *
import glfw
from src.core.event import EventManager
from src.core.scene import Scene, SceneManager
from src.core.animation import AnimationQueue
from src.graphics.camera import Camera
from src.graphics.rendering.renderer import Renderer
from src.graphics.texture_manager import TextureManager
from src.graphics.rendering.battleground_renderer import BattlegroundRenderer
from src.logic.game_state import GameState
from src.mechanics.match_logic import MatchLogic
from src.logic.catalog import make_blue_deck, make_red_deck
from lib.events import Events
from lib.types import GameSide


class BattlegroundScene(Scene):
    def __init__(
        self,
        event_manager: EventManager,
        scene_manager: SceneManager,
        camera:        Camera,
        renderer:      Renderer,
        game_state:    GameState,
        match_logic:   MatchLogic,
    ):
        super().__init__(event_manager, scene_manager, camera)
        self._renderer = renderer
        self._game_state = game_state
        self._match_logic = match_logic
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
            camera=self._camera,
        )
        self._board.load_assets()

        self._events.subscribe(Events.TURN_STARTED, self._on_turn_started)
        self._events.subscribe(Events.MATCH_ENDED,  self._on_match_ended)

        self._match_logic.setup_match(
            blue_deck=make_blue_deck(),
            red_deck=make_red_deck(),
        )
        self._match_logic.start_game()

    def on_exit(self) -> None:
        self._events.unsubscribe(Events.TURN_STARTED, self._on_turn_started)
        self._events.unsubscribe(Events.MATCH_ENDED,  self._on_match_ended)
        if self._board:
            self._board.unload_assets()
            self._board = None
        self._animation_queue = None

    def on_pause(self) -> None: ...

    def on_resume(self) -> None: ...

    def _on_turn_started(self, data: dict) -> None:
        side: GameSide | None = data.get("side")
        if side is not None and side != self._camera.current_perspective:
            self._camera.rotate_perspective()

    def _on_match_ended(self, data: dict) -> None:
        self._scenes.push_by_key("game_over")

    def update(self, dt: float) -> None:
        if self._animation_queue:
            self._animation_queue.update(dt)
        if self._board:
            self._board.update(dt)

    def render(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self._board:
            self._board.render(
                proj3d=self._camera.projection(),
                view=self._camera.view(),
                proj2d=self._camera.ortho(),
            )

    def handle_input(self) -> None: ...

    def on_key(self, key: int, action: int, mods: int) -> None:
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            self._scenes.pop_scene()
        elif key == glfw.KEY_K:
            self._force_victory_by_hp()

    def _force_victory_by_hp(self) -> None:
        blue_hp = self._game_state.aegis(GameSide.BLUE).current_health
        red_hp  = self._game_state.aegis(GameSide.RED).current_health
        if blue_hp == red_hp:
            return
        winner = GameSide.BLUE if blue_hp > red_hp else GameSide.RED
        self._game_state.set_winner(winner)
        self._events.emit(Events.MATCH_ENDED, winner_side=winner)

    def on_mouse_move(self, mx: float, my: float) -> None:
        if self._board:
            self._board.on_mouse_move(mx, my)

    def on_mouse_click(self, button: int, mx: float, my: float) -> None:
        if self._board:
            self._board.on_mouse_click(mx, my)

    def on_mouse_press(self, mx: float, my: float) -> None:
        if self._board:
            self._board.on_mouse_press(mx, my)

    def on_mouse_release(self, mx: float, my: float) -> None:
        if self._board:
            self._board.on_mouse_release(mx, my)
