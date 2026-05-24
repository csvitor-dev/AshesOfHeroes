import math
import numpy as np
from OpenGL.GL import *
from pyglm import glm
from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute


W, H = 1280, 720

_COLOR_TEXT_PRIMARY = glm.vec4(0.92, 0.91, 0.88, 1.00)
_COLOR_TEXT_SECONDARY = glm.vec4(0.65, 0.64, 0.61, 1.00)
_COLOR_TEXT_TERTIARY = glm.vec4(0.42, 0.41, 0.40, 1.00)
_COLOR_BORDER = glm.vec4(0.55, 0.54, 0.52, 0.40)
_COLOR_BTN_HOVER = glm.vec4(1.00, 1.00, 1.00, 0.06)
_COLOR_BG = glm.vec4(0.07, 0.07, 0.08, 1.00)

_LAYOUT_POS2 = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])


class Button:
    def __init__(self, cx: float, cy: float, w: float, h: float, label: str, key: str):
        self.cx, self.cy = cx, cy
        self.w,  self.h = w, h
        self.label = label
        self.key = key
        self.hovered = False

    def contains(self, mx: float, my: float) -> bool:
        return (abs(mx - self.cx) <= self.w / 2 and
                abs(my - self.cy) <= self.h / 2)

    def quad_verts(self) -> np.ndarray:
        x0, y0 = self.cx - self.w / 2, self.cy - self.h / 2
        x1, y1 = self.cx + self.w / 2, self.cy + self.h / 2
        return np.array([x0, y0, x1, y0, x1, y1, x0, y1], dtype=np.float32)

    def border_verts(self) -> np.ndarray:
        x0 = self.cx - self.w / 2 + 1
        y0 = self.cy - self.h / 2 + 1
        x1 = self.cx + self.w / 2 - 1
        y1 = self.cy + self.h / 2 - 1
        return np.array([x0, y0, x1, y0, x1, y1, x0, y1], dtype=np.float32)


class MenuRenderer:

    def __init__(self, renderer: Renderer):
        self.renderer = renderer
        self._t = 0.0
        self._proj = glm.ortho(0, float(W), float(H), 0, -1, 1)
        self._alpha_enter = 0.0

        cx = W / 2
        self._buttons = [
            Button(cx, H/2 + 20,  260, 48, "Battleground", "battle"),
            Button(cx, H/2 + 82,  260, 34, "Sair",         "exit"),
        ]
        self._build_logo()

    def load_assets(self) -> None:
        self.renderer.load_program("scenes", "menu")
        self._upload_geometry()

    def unload_assets(self) -> None:
        for key in ("menu_bg", "hex_outer", "hex_inner", "hex_dot",
                    "btn_battle_bg", "btn_battle_border",
                    "btn_exit_border"):
            self.renderer.delete(key)

    def _build_logo(self):
        cx, cy = W / 2, H / 2 - 130
        self._hex_center = glm.vec2(cx, cy)

        def hex_verts(r: int):
            pts: list[float] = []
            for i in range(6):
                a = math.radians(60 * i - 30)
                pts += [cx + math.cos(a) * r, cy + math.sin(a) * r]
            return np.array(pts, dtype=np.float32)

        self._hex_outer_verts = hex_verts(36)
        self._hex_inner_verts = hex_verts(26)
        self._dot_cx, self._dot_cy = cx, cy

    def _upload_geometry(self):
        bg = np.array([0, 0, W, 0, W, H, 0, H], dtype=np.float32)
        self.renderer.upload("menu_bg", bg, _LAYOUT_POS2,
                             np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32))

        self.renderer.upload("hex_outer", self._hex_outer_verts, _LAYOUT_POS2)
        self.renderer.upload("hex_inner", self._hex_inner_verts, _LAYOUT_POS2)

        dc = self._dot_cx
        dy = self._dot_cy
        dot = np.array([dc-4, dy-4, dc+4, dy-4, dc+4, dy+4, dc-4, dy+4],
                       dtype=np.float32)
        self.renderer.upload("hex_dot", dot, _LAYOUT_POS2,
                             np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32))

        for btn in self._buttons:
            self.renderer.upload(f"btn_{btn.key}_bg",
                                 btn.quad_verts(), _LAYOUT_POS2,
                                 np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32))
            self.renderer.upload(f"btn_{btn.key}_border",
                                 btn.border_verts(), _LAYOUT_POS2)

    def update(self, t: float) -> None:
        self._t = t
        self._alpha_enter = min(1.0, t / 0.6)

    def hit_test(self, mx: float, my: float) -> str | None:
        for btn in self._buttons:
            if btn.contains(mx, my):
                return btn.key
        return None

    def set_hover(self, mx: float, my: float) -> None:
        for btn in self._buttons:
            btn.hovered = btn.contains(mx, my)

    def render(self) -> None:
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        prog = self.renderer.use("scenes_menu")

        self.up_proj(prog, self._proj)

        self.up_color(prog, _COLOR_BG)
        self.up_alpha(prog, 1.0)
        self.renderer.draw("menu_bg")

        a = self._alpha_enter

        pulse = 0.55 + 0.20 * math.sin(self._t * 1.8)
        border_a = pulse * a

        self.up_color(prog, glm.vec4(0.55, 0.54, 0.52, border_a))
        self.up_alpha(prog, border_a)
        glBindVertexArray(self.renderer.get_vao_id_by_key("hex_outer"))
        glDrawArrays(GL_LINE_LOOP, 0, 6)
        glBindVertexArray(0)

        inner_a = (0.35 + 0.15 * math.sin(self._t * 1.8 + 0.4)) * a
        self.up_color(prog, glm.vec4(0.55, 0.54, 0.52, inner_a))
        self.up_alpha(prog, inner_a)
        glBindVertexArray(self.renderer.get_vao_id_by_key("hex_inner"))
        glDrawArrays(GL_LINE_LOOP, 0, 6)
        glBindVertexArray(0)

        dot_a = (0.50 + 0.20 * math.sin(self._t * 1.8)) * a
        self.up_color(prog, glm.vec4(0.55, 0.54, 0.52, dot_a))
        self.up_alpha(prog, dot_a)
        self.renderer.draw("hex_dot")

        for btn in self._buttons:
            is_battle = btn.key == "battle"

            if btn.hovered and is_battle:
                self.up_color(prog, _COLOR_BTN_HOVER)
                self.up_alpha(prog, a)
                self.renderer.draw(f"btn_{btn.key}_bg")

            border_color = (_COLOR_TEXT_SECONDARY if btn.hovered
                            else _COLOR_BORDER)
            if not is_battle:
                border_color = glm.vec4(0, 0, 0, 0)

            self.up_color(prog, border_color)
            self.up_alpha(prog, a)
            glBindVertexArray(self.renderer.get_vao_id_by_key(
                f"btn_{btn.key}_border"))
            glDrawArrays(GL_LINE_LOOP, 0, 4)
            glBindVertexArray(0)

    def up_proj(self, prog: int, proj: glm.mat4):
        loc = glGetUniformLocation(prog, "projection")
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(proj))

    def up_color(self, prog: int, c: glm.vec4):
        loc = glGetUniformLocation(prog, "color")
        glUniform4f(loc, c.x, c.y, c.z, c.w)

    def up_alpha(self, prog: int, a: float):
        loc = glGetUniformLocation(prog, "alpha")
        glUniform1f(loc, a)
