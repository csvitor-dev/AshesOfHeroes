import math
import numpy as np
from OpenGL.GL import *
from pyglm import glm

from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute
from src.graphics.rendering.font_renderer import FontRenderer


W, H = 1280, 720

_COLOR_BG          = glm.vec4(0.07, 0.07, 0.08, 1.00)
_COLOR_BORDER      = glm.vec4(0.55, 0.54, 0.52, 0.40)
_COLOR_BORDER_HOV  = glm.vec4(0.92, 0.91, 0.88, 0.90)
_COLOR_BTN_HOV     = glm.vec4(1.00, 1.00, 1.00, 0.06)
_COLOR_WIN         = glm.vec4(0.95, 0.85, 0.30, 1.00)
_COLOR_LOSE        = glm.vec4(1.00, 0.30, 0.30, 1.00)
_COLOR_SUBTITLE    = glm.vec4(0.60, 0.58, 0.55, 0.75)
_COLOR_BTN_LABEL   = glm.vec4(0.92, 0.91, 0.88, 1.00)

_LAYOUT_POS2 = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])


class GameOverRenderer:
    def __init__(self, renderer: Renderer, is_winner: bool):
        self._renderer = renderer
        self._is_winner = is_winner
        self._t = 0.0
        self._alpha = 0.0

        self._title_font = FontRenderer("CinzelDecorative-Bold", renderer, 72)
        self._sub_font   = FontRenderer("CinzelDecorative-Regular", renderer, 28)
        self._btn_font   = FontRenderer("CinzelDecorative-Regular", renderer, 22)

        cx = W / 2
        self._btn_cx, self._btn_cy = cx, H / 2 + 60
        self._btn_w, self._btn_h = 320, 46
        self._btn_hovered = False

        cx_hex = W / 2
        cy_hex = H / 2 - 120
        self._hex_center = glm.vec2(cx_hex, cy_hex)
        self._hex_outer_verts = _hex_verts(cx_hex, cy_hex, 36)
        self._hex_inner_verts = _hex_verts(cx_hex, cy_hex, 26)
        self._dot_cx, self._dot_cy = cx_hex, cy_hex

    def load_assets(self) -> None:
        self._renderer.load_program("scenes", "menu")
        self._title_font.load()
        self._sub_font.load()
        self._btn_font.load()
        self._upload_geometry()

    def unload_assets(self) -> None:
        self._title_font.unload()
        self._sub_font.unload()
        self._btn_font.unload()
        for key in ("go_bg", "go_hex_outer", "go_hex_inner", "go_hex_dot",
                    "go_btn_bg", "go_btn_border"):
            self._renderer.delete(key)

    def _upload_geometry(self) -> None:
        bg = np.array([0, 0, W, 0, W, H, 0, H], dtype=np.float32)
        self._renderer.upload("go_bg", bg, _LAYOUT_POS2,
                              np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32))

        self._renderer.upload("go_hex_outer", self._hex_outer_verts, _LAYOUT_POS2)
        self._renderer.upload("go_hex_inner", self._hex_inner_verts, _LAYOUT_POS2)

        dc, dy = self._dot_cx, self._dot_cy
        dot = np.array([dc-4, dy-4, dc+4, dy-4, dc+4, dy+4, dc-4, dy+4],
                       dtype=np.float32)
        self._renderer.upload("go_hex_dot", dot, _LAYOUT_POS2,
                              np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32))

        bx = self._btn_cx - self._btn_w / 2
        by = self._btn_cy - self._btn_h / 2
        bx1, by1 = bx + self._btn_w, by + self._btn_h
        btn_quad = np.array([bx, by, bx1, by, bx1, by1, bx, by1], dtype=np.float32)
        btn_bord = np.array([bx+1, by+1, bx1-1, by+1, bx1-1, by1-1, bx+1, by1-1],
                            dtype=np.float32)
        self._renderer.upload("go_btn_bg", btn_quad, _LAYOUT_POS2,
                              np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32))
        self._renderer.upload("go_btn_border", btn_bord, _LAYOUT_POS2)

    def update(self, t: float) -> None:
        self._t = t
        self._alpha = min(1.0, t / 0.6)

    def set_hover(self, mx: float, my: float) -> None:
        self._btn_hovered = self._btn_contains(mx, my)

    def hit_test(self, mx: float, my: float) -> str | None:
        return "menu" if self._btn_contains(mx, my) else None

    def _btn_contains(self, mx: float, my: float) -> bool:
        return (abs(mx - self._btn_cx) <= self._btn_w / 2 and
                abs(my - self._btn_cy) <= self._btn_h / 2)

    def render(self, proj: glm.mat4) -> None:
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        a = self._alpha
        self._render_bg(proj)
        self._render_hex(proj, a)
        self._render_texts(proj, a)
        self._render_button(proj, a)

    def _render_bg(self, proj: glm.mat4) -> None:
        prog = self._renderer.use("scenes_menu")
        _up_proj(prog, proj)
        _up_color(prog, _COLOR_BG)
        _up_alpha(prog, 1.0)
        self._renderer.draw("go_bg")

    def _render_hex(self, proj: glm.mat4, a: float) -> None:
        prog = self._renderer.use("scenes_menu")
        _up_proj(prog, proj)
        pulse = 0.55 + 0.20 * math.sin(self._t * 1.8)
        hex_col = _COLOR_WIN if self._is_winner else _COLOR_LOSE

        _up_color(prog, glm.vec4(hex_col.x, hex_col.y, hex_col.z, pulse * a * 0.7))
        _up_alpha(prog, pulse * a * 0.7)
        glBindVertexArray(self._renderer.get_vao_id_by_key("go_hex_outer"))
        glDrawArrays(GL_LINE_LOOP, 0, 6)
        glBindVertexArray(0)

        inner_a = (0.35 + 0.15 * math.sin(self._t * 1.8 + 0.4)) * a * 0.7
        _up_color(prog, glm.vec4(hex_col.x, hex_col.y, hex_col.z, inner_a))
        _up_alpha(prog, inner_a)
        glBindVertexArray(self._renderer.get_vao_id_by_key("go_hex_inner"))
        glDrawArrays(GL_LINE_LOOP, 0, 6)
        glBindVertexArray(0)

        _up_color(prog, glm.vec4(hex_col.x, hex_col.y, hex_col.z, pulse * a * 0.7))
        _up_alpha(prog, pulse * a * 0.7)
        self._renderer.draw("go_hex_dot")

    def _render_texts(self, proj: glm.mat4, a: float) -> None:
        title = "VITORIA!" if self._is_winner else "DERROTA"
        t_col = _COLOR_WIN if self._is_winner else _COLOR_LOSE
        self._title_font.draw(
            text=title, x=W / 2, y=H / 2 - 230,
            color=glm.vec4(t_col.x, t_col.y, t_col.z, t_col.w * a),
            projection=proj, scale=1.0, anchor_x="center",
        )
        sub = "Bem jogado!" if self._is_winner else "Mais sorte na proxima vez."
        self._sub_font.draw(
            text=sub, x=W / 2, y=H / 2 - 175,
            color=glm.vec4(_COLOR_SUBTITLE.x, _COLOR_SUBTITLE.y,
                           _COLOR_SUBTITLE.z, _COLOR_SUBTITLE.w * a),
            projection=proj, scale=1.0, anchor_x="center",
        )

    def _render_button(self, proj: glm.mat4, a: float) -> None:
        prog = self._renderer.use("scenes_menu")
        _up_proj(prog, proj)

        if self._btn_hovered:
            _up_color(prog, _COLOR_BTN_HOV)
            _up_alpha(prog, a)
            self._renderer.draw("go_btn_bg")

        border = _COLOR_BORDER_HOV if self._btn_hovered else _COLOR_BORDER
        _up_color(prog, border)
        _up_alpha(prog, a)
        glBindVertexArray(self._renderer.get_vao_id_by_key("go_btn_border"))
        glDrawArrays(GL_LINE_LOOP, 0, 4)
        glBindVertexArray(0)

        boost = 0.15 if self._btn_hovered else 0.0
        lbl_col = glm.vec4(
            min(1.0, _COLOR_BTN_LABEL.x + boost),
            min(1.0, _COLOR_BTN_LABEL.y + boost),
            min(1.0, _COLOR_BTN_LABEL.z + boost),
            _COLOR_BTN_LABEL.w * a,
        )
        self._btn_font.draw(
            text="Voltar ao Menu",
            x=self._btn_cx, y=self._btn_cy + 22 * 0.35,
            color=lbl_col, projection=proj,
            scale=1.0, anchor_x="center",
        )


def _hex_verts(cx: float, cy: float, r: int) -> np.ndarray:
    pts: list[float] = []
    for i in range(6):
        a = math.radians(60 * i - 30)
        pts += [cx + math.cos(a) * r, cy + math.sin(a) * r]
    return np.array(pts, dtype=np.float32)


def _up_proj(prog: int, proj: glm.mat4) -> None:
    glUniformMatrix4fv(glGetUniformLocation(prog, "projection"),
                       1, GL_FALSE, glm.value_ptr(proj))


def _up_color(prog: int, c: glm.vec4) -> None:
    glUniform4f(glGetUniformLocation(prog, "color"), c.x, c.y, c.z, c.w)


def _up_alpha(prog: int, a: float) -> None:
    glUniform1f(glGetUniformLocation(prog, "alpha"), a)
