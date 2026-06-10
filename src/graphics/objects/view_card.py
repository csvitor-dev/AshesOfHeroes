import ctypes
import numpy as np
from OpenGL.GL import *
from pyglm import glm

from src.graphics.primitives.entity_3d import Entity3D
from src.graphics.texture_manager import TextureManager
from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute


_LAYOUT_2D = VertexLayout([
    VertexAttribute("position", GL_FLOAT, 2),
    VertexAttribute("uv",       GL_FLOAT, 2),
])
_QUAD_IDX = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

CARD_W_3D = 0.70
CARD_D_3D = 1.00
CARD_H_3D = 0.005


class ViewCard(Entity3D):

    def __init__(
        self,
        card_id:      object,
        texture_path: str,
        renderer:     Renderer,
        textures:     TextureManager,
        position:     glm.vec2 = glm.vec2(0.0),
    ):
        super().__init__()
        self.card_id = card_id
        self.texture_path = texture_path
        self._renderer = renderer
        self._textures = textures

        self._pos_2d:    glm.vec2 = glm.vec2(position)
        self._target_2d: glm.vec2 = glm.vec2(position)

        self._dragging:  bool = False
        self._drag_pos:  glm.vec2 = glm.vec2(0.0)

        self._vao_3d: int = 0
        self._vbo_3d: int = 0
        self._vao_2d: str = f"card2d_{id(self)}"

        self._build_3d()
        self._build_2d()

    def _build_3d(self) -> None:
        hw = CARD_W_3D / 2
        hd = CARD_D_3D / 2
        z0, z1 = 0.0, CARD_H_3D
        c = (0.92, 0.90, 0.85)

        tris: list[list[float]] = []

        def tri(p0: list[float], p1: list[float], p2: list[float]):
            v0 = np.array(p0, dtype=np.float32)
            v1 = np.array(p1, dtype=np.float32)
            v2 = np.array(p2, dtype=np.float32)
            n = np.cross(v1 - v0, v2 - v0)
            nm = np.linalg.norm(n)
            n = (n / nm).tolist() if nm > 1e-6 else [0.0, 0.0, 1.0]
            tris.extend([list(p0) + list(c) + n,
                         list(p1) + list(c) + n,
                         list(p2) + list(c) + n])

        bot = [[-hw, -hd, z0], [hw, -hd, z0], [hw, hd, z0], [-hw, hd, z0]]
        top = [[-hw, -hd, z1], [hw, -hd, z1], [hw, hd, z1], [-hw, hd, z1]]

        tri(top[0], top[1], top[2])
        tri(top[0], top[2], top[3])

        for i in range(4):
            j = (i + 1) % 4
            tri(bot[i], bot[j], top[j])
            tri(bot[i], top[j], top[i])

        verts = np.array(tris, dtype=np.float32)
        self._vertex_count_3d = len(tris) * 3 // 3

        self._vao_3d = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(self._vao_3d)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

        stride = 9 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        self._vbo_3d = vbo

    def _build_2d(self) -> None:
        from src.graphics.objects.view_inventory import SLOT_W, SLOT_H
        w, h = SLOT_W - 8, SLOT_H - 8
        verts = np.array([
            0, 0, 0.0, 0.0,
            w, 0, 1.0, 0.0,
            w, h, 1.0, 1.0,
            0, h, 0.0, 1.0,
        ], dtype=np.float32)
        self._renderer.upload(self._vao_2d, verts, _LAYOUT_2D, _QUAD_IDX)

    @property
    def pos_2d(self) -> glm.vec2:
        return self._pos_2d

    @pos_2d.setter
    def pos_2d(self, v: glm.vec2) -> None:
        self._pos_2d = glm.vec2(v)
        self._target_2d = glm.vec2(v)

    def move_to(self, target: glm.vec2) -> None:
        self._target_2d = glm.vec2(target)

    def update_lerp(self, dt: float, speed: float = 10.0) -> None:
        if not self._dragging:
            alpha = min(1.0, speed * dt)
            self._pos_2d = glm.mix(self._pos_2d, self._target_2d, alpha)

    def start_drag(self, mx: float, my: float) -> None:
        self._dragging = True
        self._drag_pos = glm.vec2(mx, my)

    def update_drag(self, mx: float, my: float) -> None:
        if self._dragging:
            self._pos_2d = glm.vec2(mx - SLOT_W / 2, my - SLOT_H / 2)

    def end_drag(self) -> None:
        self._dragging = False

    @property
    def is_dragging(self) -> bool:
        return self._dragging

    def draw_3d(self, program: int) -> None:
        model = self.model_matrix()
        glUniformMatrix4fv(
            glGetUniformLocation(program, "model"),
            1, GL_FALSE, glm.value_ptr(model),
        )
        glBindVertexArray(self._vao_3d)
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count_3d)
        glBindVertexArray(0)

    def draw_2d(self, program: int, proj: glm.mat4) -> None:
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(self._pos_2d, 0.0))

        glUniformMatrix4fv(glGetUniformLocation(program, "projection"),
                           1, GL_FALSE, glm.value_ptr(proj))
        glUniformMatrix4fv(glGetUniformLocation(program, "model"),
                           1, GL_FALSE, glm.value_ptr(model))

        glUniform4f(glGetUniformLocation(
            program, "color_tint"), 1.0, 1.0, 1.0, 1.0)
        glUniform1f(glGetUniformLocation(program, "alpha"), 1.0)
        glUniform1f(glGetUniformLocation(program, "glow"),  0.0)
        glUniform1i(glGetUniformLocation(program, "u_texture"), 0)

        self._textures.bind(self.texture_path, slot=0)
        self._renderer.draw(self._vao_2d)

    def delete(self) -> None:
        if self._vao_3d:
            glDeleteVertexArrays(1, [self._vao_3d])
            glDeleteBuffers(1, [self._vbo_3d])
        self._renderer.delete(self._vao_2d)
