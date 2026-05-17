import ctypes
import numpy as np
from OpenGL.GL import *


class Entity3D:
    def __init__(self):
        self._vao: int = 0
        self._vbo: int = 0
        self._ebo: int = 0
        self._index_count: int = 0

        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.rotation = np.array(
            [0.0, 0.0, 0.0], dtype=np.float32)
        self.scale = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.color = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)

    def _upload(self, vertices: np.ndarray, indices: np.ndarray):
        self._index_count = len(indices)

        self._vao = glGenVertexArrays(1)
        self._vbo = glGenBuffers(1)
        self._ebo = glGenBuffers(1)

        glBindVertexArray(self._vao)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes,
                     vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                     indices.nbytes, indices, GL_STATIC_DRAW)

        stride = 6 * 4  # 6 floats × 4 bytes

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def model_matrix(self) -> np.ndarray:
        return mat4_trs(self.position, self.rotation, self.scale)

    def draw(self, shader_program: int):
        loc_model = glGetUniformLocation(shader_program, "u_model")
        loc_color = glGetUniformLocation(shader_program, "u_color")

        glUniformMatrix4fv(loc_model, 1, GL_FALSE, self.model_matrix())
        glUniform4fv(loc_color, 1, self.color)

        glBindVertexArray(self._vao)
        glDrawElements(GL_TRIANGLES, self._index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def delete(self):
        glDeleteVertexArrays(1, [self._vao])
        glDeleteBuffers(1, [self._vbo, self._ebo])
