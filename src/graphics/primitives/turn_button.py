import numpy as np
import ctypes
from OpenGL.GL import *
from pyglm import glm

from src.graphics.primitives.entity_3d import Entity3D


class TurnButton(Entity3D):
    RADIUS:   float = 0.45
    H_BASE:   float = 0.08
    H_TOP:    float = 0.14
    SEGMENTS: int = 24

    def __init__(self, color: tuple[float, float, float] = (0.85, 0.82, 0.75)):
        super().__init__()
        self._color = color
        self._pressed = False
        vertices, count = self._build_geometry(color)
        self._upload_mesh(vertices, count)

    def _build_geometry(self, c: tuple[float, float, float]) -> tuple[np.ndarray, int]:
        import math
        tris: list[list[float]] = []

        def tri(p0: list[float], p1: list[float], p2: list[float], color: tuple[float, float, float]):
            v0 = np.array(p0, dtype=np.float32)
            v1 = np.array(p1, dtype=np.float32)
            v2 = np.array(p2, dtype=np.float32)
            n = np.cross(v1 - v0, v2 - v0)
            nm = np.linalg.norm(n)
            n = (n / nm).tolist() if nm > 1e-6 else [0.0, 0.0, 1.0]
            cl = list(color)
            tris.extend([p0 + cl + n, p1 + cl + n, p2 + cl + n])

        z0 = 0.005
        z1 = z0 + self.H_BASE
        z2 = z1 + self.H_TOP
        r = self.RADIUS
        c_dark = (c[0] * 0.6, c[1] * 0.6, c[2] * 0.6)
        c_light = (min(c[0] * 1.15, 1.0), min(c[1] *
                   1.15, 1.0), min(c[2] * 1.15, 1.0))

        pts_base: list[list[float]] = []
        pts_top: list[list[float]] = []
        for i in range(self.SEGMENTS):
            a = 2 * math.pi * i / self.SEGMENTS
            pts_base.append([r * math.cos(a), r * math.sin(a), z1])
            pts_top.append([r * math.cos(a), r * math.sin(a), z2])

        for i in range(self.SEGMENTS):
            j = (i + 1) % self.SEGMENTS
            tri([0, 0, z2], pts_top[i], pts_top[j], c_light)

        for i in range(self.SEGMENTS):
            j = (i + 1) % self.SEGMENTS
            tri(pts_base[i], pts_base[j], pts_top[j],  c)
            tri(pts_base[i], pts_top[j],  pts_top[i],  c)

        r2 = r * 1.15
        pts_rim: list[list[float]] = []
        for i in range(self.SEGMENTS):
            a = 2 * math.pi * i / self.SEGMENTS
            pts_rim.append([r2 * math.cos(a), r2 * math.sin(a), z0])

        for i in range(self.SEGMENTS):
            j = (i + 1) % self.SEGMENTS
            tri(pts_rim[i], pts_rim[j], pts_base[j], c_dark)
            tri(pts_rim[i], pts_base[j], pts_base[i], c_dark)

        # face inferior
        for i in range(self.SEGMENTS):
            j = (i + 1) % self.SEGMENTS
            tri([0, 0, z0], pts_rim[j], pts_rim[i], c_dark)

        arr = np.array(tris, dtype=np.float32)
        return arr, len(tris) // 3

    def _upload_mesh(self, vertices: np.ndarray, count: int) -> None:
        self._vertex_count = count * 3
        self._vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

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
        self._vbo = vbo
        self._ebo = None

    def draw(self, shader_program: int) -> None:
        model = self.model_matrix()
        glUniformMatrix4fv(
            glGetUniformLocation(shader_program, "model"),
            1, GL_FALSE, glm.value_ptr(model),
        )
        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)
        glBindVertexArray(0)
