import math
import numpy as np
from OpenGL.GL import *
from pyglm import glm

from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute
from src.graphics.rendering.font_renderer import FontRenderer


W, H = 1280, 720

_COLOR_BG = glm.vec4(0.07, 0.07, 0.08, 1.00)
_COLOR_BORDER = glm.vec4(0.55, 0.54, 0.52, 0.40)
_COLOR_BORDER_HOVER = glm.vec4(0.92, 0.91, 0.88, 0.90)
_COLOR_BTN_HOVER_FILL = glm.vec4(1.00, 1.00, 1.00, 0.06)
_COLOR_TITLE = glm.vec4(0.80, 0.80, 0.90, 1.00)
_COLOR_BTN_PRIMARY = glm.vec4(0.92, 0.91, 0.88, 1.00)
_COLOR_BTN_EXIT = glm.vec4(0.55, 0.54, 0.52, 1.00)

_LAYOUT_POS2 = VertexLayout([VertexAttribute("position", GL_FLOAT, 2)])


class Button:
    def __init__(self, cx: float, cy: float, w: float, h: float,
                 label: str, key: str,
                 font_size: int = 28,
                 color: glm.vec4 = _COLOR_BTN_PRIMARY):
        self.cx, self.cy = cx, cy
        self.w,  self.h = w,  h
        self.label = label
        self.key = key
        self.font_size = font_size
        self.color = glm.vec4(color)
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
        self._alpha = 0.0
        self.title = FontRenderer(
            font_name="CinzelDecorative-Bold",
            renderer=self.renderer,
            size_px=72,
        )
        self.subtitle = FontRenderer(
            font_name="CinzelDecorative-Regular",
            renderer=self.renderer,
            size_px=32,
        )

        cx = W / 2
        self._buttons = [
            Button(
                cx=cx, cy=H / 2 + 20,
                w=360, h=52,
                label="Campo de Batalha",
                key="battle",
                font_size=26,
                color=_COLOR_BTN_PRIMARY,
            ),
            Button(
                cx=cx, cy=H / 2 + 90,
                w=360, h=38,
                label="Sair",
                key="exit",
                font_size=20,
                color=_COLOR_BTN_EXIT,
            ),
        ]

        self._fonts: dict[int, FontRenderer] = {
            72: self.title, 32: self.subtitle}
        self._build_hex_logo()

    def load_assets(self) -> None:
        self.renderer.load_program("scenes", "menu")
        self.title.load()
        self.subtitle.load()

        sizes = {btn.font_size for btn in self._buttons}

        for size in sizes:
            fr = FontRenderer(
                font_name="CinzelDecorative-Regular",
                renderer=self.renderer,
                size_px=size,
            )
            fr.load()
            self._fonts[size] = fr
        self._upload_geometry()

    def unload_assets(self) -> None:
        self.title.unload()
        self.subtitle.unload()

        for fr in self._fonts.values():
            fr.unload()
        self._fonts.clear()

        for key in ("menu_bg", "hex_outer", "hex_inner", "hex_dot"):
            self.renderer.delete(key)

        for btn in self._buttons:
            self.renderer.delete(f"btn_{btn.key}_bg")
            self.renderer.delete(f"btn_{btn.key}_border")

    def _font(self, size: int) -> FontRenderer:
        return self._fonts[size]

    def _draw_text_centered(
        self,
        text:  str,
        cx:    float,
        cy:    float,
        size:  int,
        color: glm.vec4,
        proj:  glm.mat4,
    ) -> None:
        self._font(size).draw(
            text=text,
            x=cx,
            y=cy + size * 0.35,
            color=color,
            projection=proj,
            scale=1.0,
            anchor_x="center",
        )

    def update(self, t: float) -> None:
        self._t = t
        self._alpha = min(1.0, t / 0.6)

    def hit_test(self, mx: float, my: float) -> str | None:
        for btn in self._buttons:
            if btn.contains(mx, my):
                return btn.key
        return None

    def set_hover(self, mx: float, my: float) -> None:
        for btn in self._buttons:
            btn.hovered = btn.contains(mx, my)

    def _build_hex_logo(self):
        cx, cy = W / 2, H / 2 - 110
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

        dc, dy = self._dot_cx, self._dot_cy
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

    def render(self, proj: glm.mat4) -> None:
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        a = self._alpha

        self._render_background(proj)
        self._render_logo(proj, a)
        self._render_title(proj, a)
        self._render_buttons(proj, a)

    def _render_background(self, proj: glm.mat4):
        prog = self.renderer.use("scenes_menu")
        _up_proj(prog, proj)
        _up_color(prog, _COLOR_BG)
        _up_alpha(prog, 1.0)
        self.renderer.draw("menu_bg")

    def _render_logo(self, proj: glm.mat4, a: float):
        prog = self.renderer.use("scenes_menu")
        _up_proj(prog, proj)

        pulse = 0.55 + 0.20 * math.sin(self._t * 1.8)

        _up_color(prog, glm.vec4(0.55, 0.54, 0.52, pulse * a))
        _up_alpha(prog, pulse * a)
        glBindVertexArray(self.renderer.get_vao_id_by_key("hex_outer"))
        glDrawArrays(GL_LINE_LOOP, 0, 6)
        glBindVertexArray(0)

        inner_a = (0.35 + 0.15 * math.sin(self._t * 1.8 + 0.4)) * a
        _up_color(prog, glm.vec4(0.55, 0.54, 0.52, inner_a))
        _up_alpha(prog, inner_a)
        glBindVertexArray(self.renderer.get_vao_id_by_key("hex_inner"))
        glDrawArrays(GL_LINE_LOOP, 0, 6)
        glBindVertexArray(0)

        _up_color(prog, glm.vec4(0.55, 0.54, 0.52, pulse * a))
        _up_alpha(prog, pulse * a)
        self.renderer.draw("hex_dot")

    def _render_title(self, proj: glm.mat4, a: float):
        self._draw_text_centered(
            text="ASHES OF HEROES",
            cx=W / 2,
            cy=H / 2 - 260,
            size=72,
            color=glm.vec4(_COLOR_TITLE.x, _COLOR_TITLE.y,
                           _COLOR_TITLE.z, _COLOR_TITLE.w * a),
            proj=proj,
        )
        self._draw_text_centered(
            text="Escolha seu destino",
            cx=W / 2,
            cy=H / 2 - 200,
            size=32,
            color=glm.vec4(0.60, 0.58, 0.55, 0.65 * a),
            proj=proj,
        )

    def _render_buttons(self, proj: glm.mat4, a: float):
        prog = self.renderer.use("scenes_menu")
        _up_proj(prog, proj)

        for btn in self._buttons:
            self._render_button_bg(btn, prog, a)
            self._render_button_border(btn, prog, a)
            self._render_button_label(btn, proj, a)

    def _render_button_bg(self, btn: Button, prog: int, a: float):
        if btn.hovered and btn.key == "battle":
            _up_color(prog, _COLOR_BTN_HOVER_FILL)
            _up_alpha(prog, a)
            self.renderer.draw(f"btn_{btn.key}_bg")

    def _render_button_border(self, btn: Button, prog: int, a: float):
        if btn.key == "exit":
            return
        border = _COLOR_BORDER_HOVER if btn.hovered else _COLOR_BORDER
        _up_color(prog, border)
        _up_alpha(prog, a)
        glBindVertexArray(self.renderer.get_vao_id_by_key(
            f"btn_{btn.key}_border"))
        glDrawArrays(GL_LINE_LOOP, 0, 4)
        glBindVertexArray(0)

    def _render_button_label(self, btn: Button, proj: glm.mat4, a: float):
        base = btn.color
        boost = 0.15 if btn.hovered else 0.0
        color = glm.vec4(
            min(1.0, base.x + boost),
            min(1.0, base.y + boost),
            min(1.0, base.z + boost),
            base.w * a,
        )
        self._draw_text_centered(
            text=btn.label,
            cx=btn.cx,
            cy=btn.cy,
            size=btn.font_size,
            color=color,
            proj=proj,
        )


def _up_proj(prog: int, proj: glm.mat4):
    glUniformMatrix4fv(glGetUniformLocation(prog, "projection"),
                       1, GL_FALSE, glm.value_ptr(proj))


def _up_color(prog: int, c: glm.vec4):
    glUniform4f(glGetUniformLocation(prog, "color"), c.x, c.y, c.z, c.w)


def _up_alpha(prog: int, a: float):
    glUniform1f(glGetUniformLocation(prog, "alpha"), a)
