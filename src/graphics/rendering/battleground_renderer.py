from OpenGL.GL import *
from pyglm import glm

from src.core.event import EventManager
from src.core.animation import AnimationQueue
from src.graphics.camera import Camera
from src.graphics.slots import BattleSlot
from src.graphics.texture_manager import TextureManager
from src.graphics.rendering.renderer import Renderer
from src.graphics.objects.view_board import ViewBoard
from src.graphics.objects.view_aegis import ViewAegis
from src.graphics.objects.view_deck import ViewDeck
from src.graphics.objects.view_hud import ViewHud
from src.graphics.objects.view_inventory import ViewInventory
from src.logic.game_state import GameState
from lib.types import GameSide


class BattlegroundRenderer:
    def __init__(
        self,
        renderer: Renderer,
        event_manager: EventManager,
        animation_queue: AnimationQueue,
        textures: TextureManager,
        game_state: GameState,
        camera: Camera,
    ):
        self.__proj3d: glm.mat4 = glm.mat4(1.0)
        self.__view: glm.mat4 = glm.mat4(1.0)

        self._renderer = renderer
        self._game_state = game_state
        self._camera = camera

        self._view_aegis = ViewAegis(renderer)
        self._view_board = ViewBoard(
            event_manager, animation_queue, renderer, textures, camera)
        self._view_deck = ViewDeck(
            renderer, event_manager, textures, camera,
            can_act=game_state.can_act,
        )
        self._view_hud = ViewHud(renderer)
        self._view_hand_blue = ViewInventory(
            event_manager, renderer, textures, GameSide.BLUE,
            round_number_fn=lambda: game_state.round_number,
        )
        self._view_hand_red = ViewInventory(
            event_manager, renderer, textures, GameSide.RED,
            round_number_fn=lambda: game_state.round_number,
        )

    def load_assets(self) -> None:
        self._renderer.load_program("scenes", "battleground")

        self._view_aegis.load_assets()
        self._view_board.load_assets()
        self._view_deck.load_assets()
        self._view_hud.load_assets()
        self._view_hand_blue.load_assets()
        self._view_hand_red.load_assets()

    def unload_assets(self) -> None:
        self._view_aegis.unload_assets()
        self._view_board.unload_assets()
        self._view_deck.unload_assets()
        self._view_hud.unload_assets()
        self._view_hand_blue.unload_assets()
        self._view_hand_red.unload_assets()

    def _active_hand(self) -> ViewInventory:
        return (self._view_hand_blue
                if self._camera.current_perspective == GameSide.BLUE
                else self._view_hand_red)

    def update(self, dt: float) -> None:
        self._view_board.update(dt)
        self._view_hand_blue.update(dt)
        self._view_hand_red.update(dt)

    def render(self, proj3d: glm.mat4, view: glm.mat4, proj2d: glm.mat4) -> None:
        self.__proj3d = proj3d
        self.__view = view

        self._render_3d(proj3d, view)
        self._render_2d(proj2d)
        self._render_hud(proj2d)

    def _render_3d(self, proj: glm.mat4, view: glm.mat4) -> None:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        self._view_board.render(proj, view)
        self._view_deck.render(proj, view)
        self._view_aegis.render(proj, view)

    def _render_2d(self, proj: glm.mat4) -> None:
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        cam = self._camera.current_perspective
        self._view_hand_blue.render(proj, self._game_state, cam)
        self._view_hand_red.render(proj, self._game_state, cam)

    def _render_hud(self, proj: glm.mat4) -> None:
        self._view_hud.render(proj, self._game_state, self._camera.current_perspective)

    def on_mouse_move(self, mx: float, my: float) -> None:
        if self.__proj3d and self.__view:
            vp = (0, 0, 1280, 720)
            self._view_board.on_mouse_move(
                mx, my, self.__proj3d, self.__view, vp)
            self._view_deck.on_mouse_move(
                mx, my, self.__proj3d, self.__view, vp)
        self._active_hand().on_mouse_move(mx, my)

    def on_mouse_click(self, mx: float, my: float) -> None:
        if self.__proj3d and self.__view:
            vp = (0, 0, 1280, 720)
            btn_hit = self._view_deck.on_mouse_click(
                mx, my, self.__proj3d, self.__view, vp)
            if not btn_hit:
                can_act = self._game_state.can_act(self._camera.current_perspective)
                self._view_board.on_mouse_click(
                    mx, my, self.__proj3d, self.__view, vp, can_act=can_act)
        self._active_hand().on_mouse_click(mx, my)

    def render_match_end(self, winner_side: GameSide, camera_side: GameSide, proj: glm.mat4) -> None:
        self._view_hud.render_match_end(proj, winner_side == camera_side)

    def on_mouse_press(self, mx: float, my: float) -> None:
        self._active_hand().on_mouse_press(mx, my)

    def on_mouse_release(self, mx: float, my: float) -> None:
        if not (self.__proj3d and self.__view):
            return

        state = self._game_state
        camera_side = self._camera.current_perspective
        can_place = state.can_act(camera_side)

        def _can_interact(slot: BattleSlot) -> bool:
            return can_place and self._view_board._can_interact(slot)

        self._active_hand().on_mouse_release(
            mx, my,
            proj=self.__proj3d,
            view=self.__view,
            viewport=(0, 0, 1280, 720),
            board_layout=self._view_board.layout,
            can_interact=_can_interact,
        )
