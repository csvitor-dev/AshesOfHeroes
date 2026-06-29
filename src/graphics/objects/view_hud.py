from OpenGL.GL import *
from pyglm import glm

from src.graphics.rendering.renderer import Renderer
from src.graphics.rendering.font_renderer import FontRenderer
from src.graphics.vertex import VertexLayout, VertexAttribute
from src.logic.game_state import GameState
import numpy as np

_LAYOUT = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])
_IDX = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

W, H = 1280, 720


class ViewHud:
    def __init__(self, renderer: Renderer):
        self._renderer = renderer
        self._font: FontRenderer | None = None

    def load_assets(self) -> None:
        self._font = FontRenderer(
            "CinzelDecorative-Regular", self._renderer, 22)
        self._font.load()
        self._upload_bars()

    def unload_assets(self) -> None:
        if self._font:
            self._font.unload()
            self._font = None
        self._renderer.delete("hud_health_bg")
        self._renderer.delete("hud_health_fill")

    def _upload_bars(self) -> None:
        self._renderer.upload(
            "hud_health_bg",
            self._bar_quad(700, 630, 130, 10),
            _LAYOUT, _IDX,
        )
        self._renderer.upload(
            "hud_health_fill",
            self._bar_quad(700, 630, 130, 10),
            _LAYOUT, _IDX, usage=GL_DYNAMIC_DRAW,
        )

    @staticmethod
    def _bar_quad(x: float, y: float, w: float, h: float) -> np.ndarray:
        return np.array(
            [x, y, x+w, y, x+w, y+h, x, y+h], dtype=np.float32
        )

    def render(self, proj: glm.mat4, state: GameState) -> None:
        prog = self._renderer.use("scenes_battleground")
        _up_proj(prog, proj)
        current_player = state.active_player

        ratio = current_player.current_health / \
            max(current_player.max_health, 1)
        fill_w = 130 * ratio

        glUniform4f(glGetUniformLocation(
            prog, "color"), 0.15, 0.15, 0.18, 0.85)
        glUniform1f(glGetUniformLocation(prog, "alpha"), 1.0)
        self._renderer.draw("hud_health_bg")

        r = 1.0 - ratio
        g = ratio
        glUniform4f(glGetUniformLocation(prog, "color"), r, g, 0.1, 1.0)
        self._renderer.update(
            "hud_health_fill",
            self._bar_quad(700, 630, fill_w, 10),
        )
        self._renderer.draw("hud_health_fill")

        if self._font:
            self._font.draw(
                text=f"Vida: {current_player.current_health}",
                x=700,
                y=622,
                color=glm.vec4(0.85, 0.85, 0.90, 0.9),
                projection=proj,
                scale=1.0,
                anchor_x="left",
            )
            self._font.draw(
                text=f"Gold: {current_player.gold}",
                x=840,
                y=622,
                color=glm.vec4(0.95, 0.80, 0.30, 0.9),
                projection=proj,
                scale=1.0,
                anchor_x="left",
            )
            self._font.draw(
                text=f"Essencias: {current_player.essences}",
                x=980,
                y=622,
                color=glm.vec4(0.60, 0.85, 1.00, 0.9),
                projection=proj,
                scale=1.0,
                anchor_x="left",
            )
            side_name = state.current_side.name
            self._font.draw(
                text=f"Turno: {side_name}  R{state.round_number}",
                x=700,
                y=605,
                color=glm.vec4(0.70, 0.70, 0.75, 0.75),
                projection=proj,
                scale=1.0,
                anchor_x="left",
            )


def _up_proj(prog: int, proj: glm.mat4x4) -> None:
    glUniformMatrix4fv(
        glGetUniformLocation(prog, "projection"),
        1, GL_FALSE, glm.value_ptr(proj),
    )
