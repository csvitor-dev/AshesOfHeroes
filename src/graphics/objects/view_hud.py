from OpenGL.GL import *
from pyglm import glm
import numpy as np

from src.graphics.rendering.renderer import Renderer
from src.graphics.rendering.font_renderer import FontRenderer
from src.graphics.vertex import VertexLayout, VertexAttribute
from src.logic.game_state import GameState
from src.logic.heroes_aegis import HeroesAegis
from lib.types import GameSide

_LAYOUT = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])
_IDX    = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

W, H = 1280, 720
_BAR_W, _BAR_H = 200, 10

_ALLY_BAR_X,  _ALLY_BAR_Y  = 460, 688
_ALLY_TEXT_Y, _ALLY_TURN_Y = 672, 715

_ENEMY_BAR_X, _ENEMY_BAR_Y = 460, 38
_ENEMY_TEXT_Y               = 72

_ROUND_X, _ROUND_Y = W - 12, 22

_SIDE_COLOR = {
    GameSide.BLUE: glm.vec4(0.40, 0.65, 1.00, 1.0),
    GameSide.RED:  glm.vec4(1.00, 0.40, 0.40, 1.0),
}


class ViewHud:
    def __init__(self, renderer: Renderer):
        self._renderer = renderer
        self._font: FontRenderer | None = None

    def load_assets(self) -> None:
        self._font = FontRenderer("CinzelDecorative-Regular", self._renderer, 22)
        self._font.load()
        self._upload_bars()

    def unload_assets(self) -> None:
        if self._font:
            self._font.unload()
            self._font = None
        for key in ("hud_ally_bg", "hud_ally_fill", "hud_enemy_bg", "hud_enemy_fill", "hud_overlay"):
            self._renderer.delete(key)

    def _upload_bars(self) -> None:
        self._renderer.upload(
            "hud_ally_bg",
            _bar_quad(_ALLY_BAR_X, _ALLY_BAR_Y, _BAR_W, _BAR_H),
            _LAYOUT, _IDX,
        )
        self._renderer.upload(
            "hud_ally_fill",
            _bar_quad(_ALLY_BAR_X, _ALLY_BAR_Y, _BAR_W, _BAR_H),
            _LAYOUT, _IDX, usage=GL_DYNAMIC_DRAW,
        )
        self._renderer.upload(
            "hud_enemy_bg",
            _bar_quad(_ENEMY_BAR_X, _ENEMY_BAR_Y, _BAR_W, _BAR_H),
            _LAYOUT, _IDX,
        )
        self._renderer.upload(
            "hud_enemy_fill",
            _bar_quad(_ENEMY_BAR_X, _ENEMY_BAR_Y, _BAR_W, _BAR_H),
            _LAYOUT, _IDX, usage=GL_DYNAMIC_DRAW,
        )
        self._renderer.upload(
            "hud_overlay",
            np.array([0, 0, W, 0, W, H, 0, H], dtype=np.float32),
            _LAYOUT, _IDX,
        )

    def render(self, proj: glm.mat4, state: GameState, camera_side: GameSide) -> None:
        enemy_side = GameSide.RED if camera_side == GameSide.BLUE else GameSide.BLUE
        ally  = state.aegis(camera_side)
        enemy = state.aegis(enemy_side)
        is_my_turn = state.current_side == camera_side

        prog = self._renderer.use("scenes_battleground")
        _up_proj(prog, proj)

        self._draw_bar(prog, ally,  "hud_ally_bg",   "hud_ally_fill",
                       _ALLY_BAR_X,  _ALLY_BAR_Y)
        self._draw_bar(prog, enemy, "hud_enemy_bg",  "hud_enemy_fill",
                       _ENEMY_BAR_X, _ENEMY_BAR_Y)

        if not self._font:
            return

        ally_col  = _SIDE_COLOR[camera_side]
        enemy_col = glm.vec4(_SIDE_COLOR[enemy_side].x,
                             _SIDE_COLOR[enemy_side].y,
                             _SIDE_COLOR[enemy_side].z, 0.70)

        self._draw_stats(proj, ally, camera_side.name,
                         _ALLY_BAR_X, _ALLY_TEXT_Y, ally_col)

        if is_my_turn:
            turn_text  = f"SEU TURNO  |  Rodada {state.round_number}"
            turn_color = glm.vec4(0.95, 0.85, 0.30, 1.0)
        else:
            turn_text  = f"Turno: {enemy_side.name}  |  Rodada {state.round_number}"
            turn_color = glm.vec4(0.55, 0.55, 0.60, 0.75)
        self._font.draw(
            text=turn_text, x=W // 2, y=_ALLY_TURN_Y,
            color=turn_color, projection=proj,
            scale=0.85, anchor_x="center",
        )

        self._draw_stats(proj, enemy, enemy_side.name,
                         _ENEMY_BAR_X, _ENEMY_TEXT_Y, enemy_col)

        self._font.draw(
            text=f"Rodada {state.round_number}",
            x=_ROUND_X, y=_ROUND_Y,
            color=glm.vec4(0.80, 0.80, 0.85, 0.80),
            projection=proj,
            scale=1.0, anchor_x="right",
        )

    def render_match_end(self, proj: glm.mat4, is_winner: bool) -> None:
        prog = self._renderer.use("scenes_battleground")
        _up_proj(prog, proj)
        glUniform4f(glGetUniformLocation(prog, "color"), 0.0, 0.0, 0.0, 0.72)
        glUniform1f(glGetUniformLocation(prog, "alpha"), 0.72)
        self._renderer.draw("hud_overlay")

        if not self._font:
            return
        text  = "VITORIA!" if is_winner else "DERROTA"
        color = (glm.vec4(0.95, 0.85, 0.30, 1.0) if is_winner
                 else glm.vec4(1.00, 0.30, 0.30, 1.0))
        self._font.draw(text=text, x=W // 2, y=H // 2,
                        color=color, projection=proj, scale=2.0, anchor_x="center")
        self._font.draw(
            text="Pressione ESC para sair",
            x=W // 2, y=H // 2 + 50,
            color=glm.vec4(0.75, 0.75, 0.80, 0.80),
            projection=proj, scale=0.9, anchor_x="center",
        )

    def _draw_bar(
        self, prog: int, aegis: HeroesAegis,
        bg_key: str, fill_key: str, x: float, y: float,
    ) -> None:
        ratio   = aegis.current_health / max(aegis.max_health, 1)
        fill_w  = _BAR_W * ratio

        glUniform4f(glGetUniformLocation(prog, "color"), 0.12, 0.12, 0.15, 0.85)
        glUniform1f(glGetUniformLocation(prog, "alpha"), 1.0)
        self._renderer.draw(bg_key)

        r, g = 1.0 - ratio, ratio
        glUniform4f(glGetUniformLocation(prog, "color"), r, g, 0.1, 1.0)
        self._renderer.update(fill_key, _bar_quad(x, y, max(fill_w, 0), _BAR_H))
        self._renderer.draw(fill_key)

    def _draw_stats(
        self, proj: glm.mat4,
        aegis: HeroesAegis, label: str,
        x: float, y: float, color: glm.vec4,
    ) -> None:
        self._font.draw(
            text=f"{label}  Vida: {aegis.current_health}",
            x=x, y=y, color=color,
            projection=proj, scale=1.0, anchor_x="left",
        )
        self._font.draw(
            text=f"Gold: {aegis.gold}",
            x=x + 290, y=y,
            color=glm.vec4(0.95, 0.80, 0.30, color.w),
            projection=proj, scale=1.0, anchor_x="left",
        )
        self._font.draw(
            text=f"Ess: {aegis.essences}",
            x=x + 410, y=y,
            color=glm.vec4(0.60, 0.85, 1.00, color.w),
            projection=proj, scale=1.0, anchor_x="left",
        )



def _bar_quad(x: float, y: float, w: float, h: float) -> np.ndarray:
    return np.array([x, y, x + w, y, x + w, y + h, x, y + h], dtype=np.float32)


def _up_proj(prog: int, proj: glm.mat4) -> None:
    glUniformMatrix4fv(
        glGetUniformLocation(prog, "projection"),
        1, GL_FALSE, glm.value_ptr(proj),
    )
