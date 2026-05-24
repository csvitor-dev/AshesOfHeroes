from typing import Any
import numpy as np
from OpenGL.GL import *
from pyglm import glm
from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute


class HudRenderer:

    W, H = 1280, 720

    HEALTH_BAR_X = 700
    HEALTH_BAR_Y = 620
    HEALTH_BAR_W = 130
    HEALTH_BAR_H = 10

    ESSENCE_X = 700
    ESSENCE_Y = 645
    ESSENCE_R = 7
    ESSENCE_GAP = 18

    GOLD_X = 820
    GOLD_Y = 600

    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        layout = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])

        self.renderer.upload(
            "hud_health_bg",
            self._bar_quad(self.HEALTH_BAR_X, self.HEALTH_BAR_Y,
                           self.HEALTH_BAR_W, self.HEALTH_BAR_H),
            layout, usage=GL_STATIC_DRAW,
        )
        self.renderer.upload(
            "hud_health_fill",
            self._bar_quad(self.HEALTH_BAR_X, self.HEALTH_BAR_Y,
                           self.HEALTH_BAR_W, self.HEALTH_BAR_H),
            layout, usage=GL_DYNAMIC_DRAW,
        )

        # orbs de essência (6 círculos aproximados com 12-gons)
        self._essence_verts = self._build_essence_polys(6)
        self.renderer.upload(
            "hud_essences", self._essence_verts, layout, usage=GL_DYNAMIC_DRAW)

    # ───────────────────────────────────────────────────────── helpers

    @staticmethod
    def _bar_quad(x: int, y: int, w: int, h: int) -> np.ndarray:
        return np.array([x, y, x+w, y, x+w, y+h, x, y+h], dtype=np.float32)

    def _build_essence_polys(self, count: int, active: int = 6) -> np.ndarray:
        import math
        segs = 12
        verts: list[float] = []
        for i in range(count):
            cx = self.ESSENCE_X + i * self.ESSENCE_GAP
            cy = self.ESSENCE_Y
            for s in range(segs):
                a = 2 * math.pi * s / segs
                verts += [cx + math.cos(a) * self.ESSENCE_R,
                          cy + math.sin(a) * self.ESSENCE_R]
        return np.array(verts, dtype=np.float32)

    def render(self, game_state: Any):
        proj = glm.ortho(0, self.W, self.H, 0, -1, 1)

        prog = self.renderer.use("slot")
        glUniformMatrix4fv(glGetUniformLocation(
            prog, "u_projection"), 1, GL_FALSE, proj)

        glUniform4f(glGetUniformLocation(prog, "color"), 0.2, 0.2, 0.2, 0.9)
        self.renderer.draw("hud_health_bg", GL_TRIANGLE_FAN)

        hp_ratio = game_state.player_health / game_state.player_max_health
        fill_w = self.HEALTH_BAR_W * hp_ratio
        layout = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])
        self.renderer.update(
            "hud_health_fill",
            self._bar_quad(self.HEALTH_BAR_X, self.HEALTH_BAR_Y,
                           fill_w, self.HEALTH_BAR_H),
        )
        r = 1.0 - hp_ratio
        g = hp_ratio
        glUniform4f(glGetUniformLocation(prog, "u_color"), r, g, 0.1, 1.0)
        self.renderer.draw("hud_health_fill", GL_TRIANGLE_FAN)

        active = game_state.aegis_essences
        for i in range(6):
            if i < active:
                glUniform4f(glGetUniformLocation(
                    prog, "u_color"), 0.3, 0.7, 1.0, 1.0)
            else:
                glUniform4f(glGetUniformLocation(
                    prog, "u_color"), 0.2, 0.2, 0.3, 0.6)
            glBindVertexArray(self.renderer._vaos["hud_essences"])
            glDrawArrays(GL_TRIANGLE_FAN, i * 12, 12)
            glBindVertexArray(0)
