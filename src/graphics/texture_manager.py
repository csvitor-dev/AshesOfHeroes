from PIL import Image
import numpy as np
from OpenGL.GL import *


class TextureManager:
    def __init__(self):
        self._cache: dict[str, int] = {}

    def load(self, path: str) -> int:
        if path in self._cache:
            return self._cache[path]

        img = Image.open(path).convert('RGBA')
        # img = img.transpose(Image.FLIP_TOP_BOTTOM)
        data = np.array(img, dtype=np.uint8)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                        GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            img.width, img.height,
            0, GL_RGBA, GL_UNSIGNED_BYTE, data
        )
        glGenerateMipmap(GL_TEXTURE_2D)

        glBindTexture(GL_TEXTURE_2D, 0)
        self._cache[path] = tex_id
        return tex_id

    def bind(self, path: str, slot: int = 0):
        glActiveTexture(GL_TEXTURE0 + slot)
        glBindTexture(GL_TEXTURE_2D, self._cache[path])

    def delete(self, path: str):
        if path in self._cache:
            glDeleteTextures(1, [self._cache.pop(path)])

    def delete_all(self):
        for tex_id in self._cache.values():
            glDeleteTextures(1, [tex_id])
        self._cache.clear()
