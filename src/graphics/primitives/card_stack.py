import numpy as np
import ctypes
from OpenGL.GL import *
from pyglm import glm

from src.graphics.primitives.entity_3d import Entity3D
from src.graphics.objects.view_card import ViewCard


class CardStack(Entity3D):
    CARD_W:      float = 1.07
    CARD_D:      float = 1.47
    SLOT_H:      float = 0.04
    CARD_THICK:  float = 0.018

    def __init__(
        self,
        color_tray: tuple[float, float, float] = (0.25, 0.25, 0.28),
        color_edge: tuple[float, float, float] = (0.45, 0.44, 0.42),
    ):
        super().__init__()
        self._color_tray = color_tray
        self._color_edge = color_edge
        self._cards: list[ViewCard] = []
        vertices, count = self._build_tray()
        self._upload_mesh(vertices, count)

    @property
    def cards(self) -> list[ViewCard]:
        return self._cards

    @property
    def count(self) -> int:
        return len(self._cards)

    def _build_tray(self) -> tuple[np.ndarray, int]:
        tris: list[list[float]] = []
        ct = self._color_tray
        ce = self._color_edge
        hw = self.CARD_W / 2
        hd = self.CARD_D / 2
        z0 = 0.005
        z1 = z0 + self.SLOT_H

        def tri(p0: list[float], p1: list[float], p2: list[float], color: tuple[float, float, float]):
            v0 = np.array(p0, dtype=np.float32)
            v1 = np.array(p1, dtype=np.float32)
            v2 = np.array(p2, dtype=np.float32)
            n = np.cross(v1 - v0, v2 - v0)
            nm = np.linalg.norm(n)
            n = (n / nm).tolist() if nm > 1e-6 else [0.0, 0.0, 1.0]
            c = list(color)
            tris.extend([p0 + c + n, p1 + c + n, p2 + c + n])

        bot = [[-hw, -hd, z0], [hw, -hd, z0], [hw, hd, z0], [-hw, hd, z0]]
        top = [[-hw, -hd, z1], [hw, -hd, z1], [hw, hd, z1], [-hw, hd, z1]]

        tri(top[0], top[1], top[2], ct)
        tri(top[0], top[2], top[3], ct)
        tri(bot[2], bot[1], bot[0], ce)
        tri(bot[3], bot[2], bot[0], ce)

        for i in range(4):
            j = (i + 1) % 4
            tri(bot[i], bot[j], top[j], ce)
            tri(bot[i], top[j], top[i], ce)

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

    def push_card(self, card: ViewCard) -> None:
        index = len(self._cards)
        offset = self.SLOT_H + 0.005 + index * self.CARD_THICK
        card.position = glm.vec3(
            self.position.x,
            self.position.y,
            self.position.z + offset,
        )
        self._cards.append(card)

    def pop_card(self) -> ViewCard | None:
        if not self._cards:
            return None
        return self._cards.pop()

    def peek(self) -> ViewCard | None:
        return self._cards[-1] if self._cards else None

    @property
    def count(self) -> int:
        return len(self._cards)

    def draw(self, shader_program: int) -> None:
        model = self.model_matrix()
        glUniformMatrix4fv(
            glGetUniformLocation(shader_program, "model"),
            1, GL_FALSE, glm.value_ptr(model),
        )
        glBindVertexArray(self._vao)
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)
        glBindVertexArray(0)
