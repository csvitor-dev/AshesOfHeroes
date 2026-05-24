from dataclasses import dataclass
import numpy as np
import freetype
from pyglm import glm
from OpenGL.GL import *
from utils.filesystem import get_asset_path
from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute


_LAYOUT = VertexLayout([
    VertexAttribute("position", GL_FLOAT, 2),
    VertexAttribute("uv",       GL_FLOAT, 2),
])

_QUAD_IDX = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)


@dataclass
class GlyphInfo:
    uv_x:      float
    uv_y:      float
    uv_w:      float
    uv_h:      float
    w:         int
    h:         int
    bearing_x: int
    bearing_y: int
    advance:   int


class FontAtlas:

    ATLAS_W = 512
    ATLAS_H = 512

    def __init__(self, font_path: str, size_px: int = 48):
        self.size_px = size_px
        self.glyphs: dict[str, GlyphInfo] = {}
        self._tex_id: int = 0
        self._load(font_path, size_px)

    def _load(self, path: str, size: int):
        face = freetype.Face(path)
        face.set_pixel_sizes(0, size)

        atlas = np.zeros((self.ATLAS_H, self.ATLAS_W), dtype=np.uint8)
        PAD = 2

        cursor_x = PAD
        cursor_y = PAD
        row_h = 0

        chars = [chr(c) for c in range(32, 127)]

        for ch in chars:
            face.load_char(ch, freetype.FT_LOAD_RENDER)
            bmp = face.glyph.bitmap
            w, h = bmp.width, bmp.rows

            if cursor_x + w + PAD > self.ATLAS_W:
                cursor_x = PAD
                cursor_y += row_h + PAD
                row_h = 0

            if cursor_y + h + PAD > self.ATLAS_H:

                self.glyphs[ch] = GlyphInfo(
                    uv_x=0, uv_y=0, uv_w=0, uv_h=0,
                    w=0, h=0,
                    bearing_x=face.glyph.bitmap_left,
                    bearing_y=face.glyph.bitmap_top,
                    advance=face.glyph.advance.x,
                )
                continue

            if w > 0 and h > 0:
                buf = np.array(bmp.buffer, dtype=np.uint8).reshape(h, w)
                atlas[cursor_y: cursor_y + h, cursor_x: cursor_x + w] = buf

            self.glyphs[ch] = GlyphInfo(
                uv_x=cursor_x / self.ATLAS_W,
                uv_y=cursor_y / self.ATLAS_H,
                uv_w=w / self.ATLAS_W,
                uv_h=h / self.ATLAS_H,
                w=w,
                h=h,
                bearing_x=face.glyph.bitmap_left,
                bearing_y=face.glyph.bitmap_top,
                advance=face.glyph.advance.x,
            )

            cursor_x += w + PAD
            row_h = max(row_h, h)

        self._tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._tex_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RED,
            self.ATLAS_W, self.ATLAS_H,
            0, GL_RED, GL_UNSIGNED_BYTE, atlas,
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self, slot: int = 0):
        glActiveTexture(GL_TEXTURE0 + slot)
        glBindTexture(GL_TEXTURE_2D, self._tex_id)

    def delete(self):
        if self._tex_id:
            glDeleteTextures(1, [self._tex_id])
            self._tex_id = 0


class FontRenderer:

    def __init__(
        self,
        font_name: str,
        renderer:  Renderer,
        size_px:   int = 48,
    ):
        self._path = get_asset_path("fonts", f"{font_name}.ttf")
        self._renderer = renderer
        self._size_px = size_px
        self._atlas:   FontAtlas | None = None

    def load(self):
        self._atlas = FontAtlas(self._path, self._size_px)
        self._renderer.load_program("fonts", "text")

    def unload(self):
        if self._atlas:
            self._atlas.delete()
            self._atlas = None

    def measure(self, text: str, scale: float = 1.0) -> float:
        if not self._atlas:
            return 0.0
        total = 0.0

        for ch in text:
            g = self._atlas.glyphs.get(ch)
            if g:
                total += (g.advance >> 6) * scale
        return total

    def draw(
        self,
        text:       str,
        x:          float,
        y:          float,
        color:      glm.vec4,
        projection: glm.mat4,
        scale:      float = 1.0,
        anchor_x:   str = "left",
    ) -> None:
        if not self._atlas:
            return

        if anchor_x == "center":
            x -= self.measure(text, scale) / 2
        elif anchor_x == "right":
            x -= self.measure(text, scale)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)

        prog = self._renderer.use("fonts_text")

        glUniformMatrix4fv(
            glGetUniformLocation(prog, "projection"),
            1, GL_FALSE, glm.value_ptr(projection),
        )
        glUniform4f(
            glGetUniformLocation(prog, "color"),
            color.x, color.y, color.z, color.w,
        )
        glUniform1i(glGetUniformLocation(prog, "atlas"), 0)

        self._atlas.bind(slot=0)

        cursor = x
        for ch in text:
            g = self._atlas.glyphs.get(ch)
            if not g:
                continue

            xpos = cursor + g.bearing_x * scale
            ypos = y - g.bearing_y * scale
            w = g.w * scale
            h = g.h * scale

            verts = np.array([
                xpos,     ypos,     g.uv_x,          g.uv_y,
                xpos + w, ypos,     g.uv_x + g.uv_w, g.uv_y,
                xpos + w, ypos + h, g.uv_x + g.uv_w, g.uv_y + g.uv_h,
                xpos,     ypos + h, g.uv_x,           g.uv_y + g.uv_h,
            ], dtype=np.float32)

            key = f"_glyph_{id(self)}_{ch}"
            self._renderer.upload(key, verts, _LAYOUT,
                                  _QUAD_IDX, usage=GL_DYNAMIC_DRAW)
            self._renderer.draw(key)
            self._renderer.delete(key)

            cursor += (g.advance >> 6) * scale
