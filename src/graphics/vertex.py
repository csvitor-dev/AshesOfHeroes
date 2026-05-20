import ctypes
from dataclasses import dataclass
from typing import Any
from OpenGL.GL import *

@dataclass
class VertexAttribute:
    name:       str
    gl_type:    Any
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
