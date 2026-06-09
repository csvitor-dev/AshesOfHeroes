import ctypes
import numpy as np
from pyglm import glm
from OpenGL.GL import *


class Entity3D:
    def __init__(self):
        self._vao: int = 0
        self._vbo: int = 0
        self._ebo: int | None = 0
        self._index_count: int = 0

        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)
        self.color = glm.vec4(1.0, 1.0, 1.0, 1.0)

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

        stride = 6 * 4

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def model_matrix(self) -> glm.mat4x4:
        model = glm.translate(glm.mat4(1.0), self.position)
        model = glm.rotateX(model, glm.radians(
            self.rotation.x)) if self.rotation.x != 0.0 else model
        model = glm.rotateY(model, glm.radians(
            self.rotation.y)) if self.rotation.y != 0.0 else model
        model = glm.rotateZ(model, glm.radians(
            self.rotation.z)) if self.rotation.z != 0.0 else model
        model = glm.scale(model, self.scale)
        return model

    def draw(self, shader_program: int):
        loc_model = glGetUniformLocation(shader_program, "model")
        loc_color = glGetUniformLocation(shader_program, "color")
        loc_normal = glGetUniformLocation(shader_program, "normal")
        
        model = self.model_matrix()        
        normal_matrix = glm.transpose(glm.inverse(glm.mat3(model)))

        glUniformMatrix4fv(loc_model, 1, GL_FALSE,
                           glm.value_ptr(model))
        glUniformMatrix3fv(loc_normal, 1, GL_FALSE, glm.value_ptr(normal_matrix))
        glUniform4fv(loc_color, 1, glm.value_ptr(self.color))

        glBindVertexArray(self._vao)
        glDrawElements(GL_TRIANGLES, self._index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def delete(self):
        glDeleteVertexArrays(1, [self._vao])
        self._vao = 0

        glDeleteBuffers(
            1, [buf for buf in (self._ebo, self._vbo) if buf is not None])
        self._ebo = 0
        self._vbo = 0
