import numpy as np
import ctypes
from OpenGL.GL import *
from pyglm import glm

from src.graphics.primitives.entity_3d import Entity3D


class HeroAegis(Entity3D):
    BASE_R_BOTTOM = 0.55
    BASE_R_TOP = 0.28
    BASE_H = 0.22
    PRISM_W = 0.22
    PRISM_H = 0.80
    PYR_H = 0.40
    SLICES = 16

    def __init__(
        self,
        color_body: tuple[float, float, float] = (0.18, 0.55, 1.00),
    ):
        super().__init__()
        self._color_base = (0.58, 0.58, 0.58)
        self._color_body = color_body
        vertices, count = self._build_geometry(
            self._color_base, self._color_body)
        self._upload_color_mesh(vertices, count)

    def _build_geometry(
        self,
        cb: tuple[float, float, float],
        cy: tuple[float, float, float],
    ) -> tuple[np.ndarray, int]:
        tris = []

        z0 = 0.0
        z1 = self.BASE_H
        z2 = z1 + self.PRISM_H
        z3 = z2 + self.PYR_H
        w = self.PRISM_W
        rb = self.BASE_R_BOTTOM
        rt = self.BASE_R_TOP

        for i in range(self.SLICES):
            a0 = 2 * np.pi * i / self.SLICES
            a1 = 2 * np.pi * (i + 1) / self.SLICES

            p0b = [rb * np.cos(a0), rb * np.sin(a0), z0]
            p1b = [rb * np.cos(a1), rb * np.sin(a1), z0]
            p0t = [rt * np.cos(a0), rt * np.sin(a0), z1]
            p1t = [rt * np.cos(a1), rt * np.sin(a1), z1]

            tris += [p0b + list(cb), p1b + list(cb), p1t + list(cb)]
            tris += [p0b + list(cb), p1t + list(cb), p0t + list(cb)]
            tris += [[0, 0, z0] + list(cb), p0b + list(cb), p1b + list(cb)]
            tris += [p0t + list(cb), p1t + list(cb), [0, 0, z1] + list(cb)]

        corners_bot = [
            [-w, -w, z1], [w, -w, z1], [w,  w, z1], [-w,  w, z1],
        ]
        corners_top = [
            [-w, -w, z2], [w, -w, z2], [w,  w, z2], [-w,  w, z2],
        ]

        for i in range(4):
            j = (i + 1) % 4
            b0, b1 = corners_bot[i], corners_bot[j]
            t0, t1 = corners_top[i], corners_top[j]
            tris += [b0 + list(cy), b1 + list(cy), t1 + list(cy)]
            tris += [b0 + list(cy), t1 + list(cy), t0 + list(cy)]

        tris += [corners_bot[0] +
                 list(cy), corners_bot[1] + list(cy), corners_bot[2] + list(cy)]
        tris += [corners_bot[0] +
                 list(cy), corners_bot[2] + list(cy), corners_bot[3] + list(cy)]
        tris += [corners_top[0] +
                 list(cy), corners_top[2] + list(cy), corners_top[1] + list(cy)]
        tris += [corners_top[0] +
                 list(cy), corners_top[3] + list(cy), corners_top[2] + list(cy)]

        apex = [0.0, 0.0, z3]
        for i in range(4):
            j = (i + 1) % 4
            tris += [corners_top[i] +
                     list(cy), corners_top[j] + list(cy), apex + list(cy)]

        tris += [corners_top[0] +
                 list(cy), corners_top[1] + list(cy), corners_top[2] + list(cy)]
        tris += [corners_top[0] +
                 list(cy), corners_top[2] + list(cy), corners_top[3] + list(cy)]

        arr = np.array(tris, dtype=np.float32)
        return arr, len(tris)

    def _upload_color_mesh(self, vertices: np.ndarray, count: int) -> None:
        self._vertex_count = count

        self._vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

        stride = 6 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self._vbo = vbo
        self._ebo = None
        self._index_count = 0

    def draw(self, program: int) -> None:
        model = self.model_matrix()
        glUniformMatrix4fv(
            glGetUniformLocation(program, "model"),
            1, GL_FALSE, glm.value_ptr(model),
        )
        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)
        glBindVertexArray(0)
