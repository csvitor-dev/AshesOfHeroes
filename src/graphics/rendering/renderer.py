import ctypes
from dataclasses import dataclass
from typing import Optional
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from src.utils.filesystem import read_vertex_shader, read_fragment_shader


@dataclass
class VertexAttribute:
    name:       str
    gl_type:    int
    count:      int
    normalized: bool = False

    @property
    def byte_size(self) -> int:
        return {
            GL_FLOAT:          4,
            GL_UNSIGNED_BYTE:  1,
            GL_UNSIGNED_INT:   4,
            GL_SHORT:          2,
            GL_UNSIGNED_SHORT: 2,
        }[self.gl_type] * self.count


@dataclass
class VertexLayout:
    attributes: list[VertexAttribute]

    @property
    def stride(self) -> int:
        return sum(a.byte_size for a in self.attributes)

    def bind(self) -> None:
        offset = 0
        for location, attr in enumerate(self.attributes):
            glEnableVertexAttribArray(location)
            glVertexAttribPointer(
                location,
                attr.count,
                attr.gl_type,
                GL_TRUE if attr.normalized else GL_FALSE,
                self.stride,
                ctypes.c_void_p(offset),
            )
            offset += attr.byte_size


@dataclass
class _BufferSet:
    vao:      int
    vbo:      int
    ebo:      Optional[int]
    count:    int
    indexed:  bool


class Renderer:
    def __init__(self):
        self.__buffers: dict[str, _BufferSet] = {}
        self.__programs: dict[str, int] = {}

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def load_program(self, name: str, scope: str, filename: str) -> int:
        vertex_src = read_vertex_shader(scope, filename)
        fragment_src = read_fragment_shader(scope, filename)

        vertex_shader = shaders.compileShader(vertex_src, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(
            fragment_src, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vertex_shader, fragment_shader)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        self.__programs[name] = program
        return program

    def use(self, name: str):
        glUseProgram(self.__programs[name])

    def upload(
        self,
        name:     str,
        vertices: np.ndarray,
        layout:   VertexLayout,
        indices:  Optional[np.ndarray] = None,
        usage:    int = GL_STATIC_DRAW,
    ) -> None:
        if name in self.__buffers:
            self.delete(name)

        verts = np.ascontiguousarray(vertices.flatten(), dtype=np.float32)
        vertex_count = len(verts) * 4 // layout.stride

        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindVertexArray(vao)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, usage)

        layout.bind()
        ebo, index_count = self.__resolve_indices(indices, usage)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.__buffers[name] = _BufferSet(
            vao=vao, vbo=vbo, ebo=ebo,
            count=index_count if indices is not None else vertex_count,
            indexed=indices is not None,
        )

    def __resolve_indices(self, indices: Optional[np.ndarray], usage: int) -> tuple[Optional[int], int]:
        if indices is None:
            return None, 0
        idx = np.ascontiguousarray(indices.flatten(), dtype=np.uint32)
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx.nbytes, idx, usage)

        return ebo, len(idx)

    def update(self, name: str, vertices: np.ndarray):
        buf = self.__buffers[name]
        verts = np.ascontiguousarray(vertices.flatten(), dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, buf.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, name: str, mode: int = GL_TRIANGLES, count: Optional[int] = None):
        buf = self.__buffers[name]
        n = count if count is not None else buf.count
        glBindVertexArray(buf.vao)

        if buf.indexed:
            glDrawElements(mode, n, GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(mode, 0, n)
        glBindVertexArray(0)

    def draw_instanced(self, name: str, instance_count: int, mode: int = GL_TRIANGLES):
        buf = self.__buffers[name]
        glBindVertexArray(buf.vao)

        if buf.indexed:
            glDrawElementsInstanced(
                mode, buf.count, GL_UNSIGNED_INT, None, instance_count)
        else:
            glDrawArraysInstanced(mode, 0, buf.count, instance_count)
        glBindVertexArray(0)

    def delete(self, name: str) -> None:
        if name not in self.__buffers:
            return
        buf = self.__buffers.pop(name)
        glDeleteVertexArrays(1, [buf.vao])
        glDeleteBuffers(1, [buf.vbo])

        if buf.ebo is not None:
            glDeleteBuffers(1, [buf.ebo])

    def delete_all(self) -> None:
        for name in list(self.__buffers):
            self.delete(name)

        for prog in self.__programs.values():
            glDeleteProgram(prog)
        self.__programs.clear()

    def uniform_f(self, prog: str, name: str, value: float):
        loc = glGetUniformLocation(self.__programs[prog], name)
        glUniform1f(loc, value)

    def uniform_i(self, prog: str, name: str, value: int):
        loc = glGetUniformLocation(self.__programs[prog], name)
        glUniform1i(loc, value)

    def uniform_mat4(self, prog: str, name: str, matrix: np.ndarray):
        loc = glGetUniformLocation(self.__programs[prog], name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, matrix.astype(np.float32))
