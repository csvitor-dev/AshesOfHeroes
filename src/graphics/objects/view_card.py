# carta.py
from OpenGL.GL import *
import numpy as np
import ctypes

class Carta:
    def __init__(self):
        # Dimensões da carta
        self.largura = 0.8
        self.altura = 1.2
        self.espessura = 0.05
        
        # Calculando as coordenadas dos vértices
        z_front = self.espessura / 2
        z_back = -self.espessura / 2
        x_left = -self.largura / 2
        x_right = self.largura / 2
        y_bottom = -self.altura / 2
        y_top = self.altura / 2
        
        self.vertices = [
            # Face frontal (MARROM) - antes era branco
            [x_left, y_bottom, z_front,  0.4, 0.2, 0.0],  # marrom escuro
            [x_right, y_bottom, z_front,  0.4, 0.2, 0.0],
            [x_right, y_top, z_front,  0.4, 0.2, 0.0],
            [x_left, y_bottom, z_front,  0.4, 0.2, 0.0],
            [x_right, y_top, z_front,  0.4, 0.2, 0.0],
            [x_left, y_top, z_front,  0.4, 0.2, 0.0],
            
            # Face traseira (BRANCO) - antes era marrom
            [x_right, y_bottom, z_back,  1.0, 1.0, 1.0],  # branco
            [x_left, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_left, y_top, z_back,  1.0, 1.0, 1.0],
            [x_right, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_left, y_top, z_back,  1.0, 1.0, 1.0],
            [x_right, y_top, z_back,  1.0, 1.0, 1.0],
            
            # Face lateral esquerda (MARROM)
            [x_left, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_left, y_bottom, z_front,  1.0, 1.0, 1.0],
            [x_left, y_top, z_front,  1.0, 1.0, 1.0],
            [x_left, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_left, y_top, z_front,  1.0, 1.0, 1.0],
            [x_left, y_top, z_back,  1.0, 1.0, 1.0],
            
            # Face lateral direita (MARROM)
            [x_right, y_bottom, z_front,  1.0, 1.0, 1.0],
            [x_right, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_right, y_top, z_back,  1.0, 1.0, 1.0],
            [x_right, y_bottom, z_front,  1.0, 1.0, 1.0],
            [x_right, y_top, z_back,  1.0, 1.0, 1.0],
            [x_right, y_top, z_front,  1.0, 1.0, 1.0],
            
            # Face superior (MARROM)
            [x_left, y_top, z_front,  1.0, 1.0, 1.0],
            [x_right, y_top, z_front,  1.0, 1.0, 1.0],
            [x_right, y_top, z_back,  1.0, 1.0, 1.0],
            [x_left, y_top, z_front,  1.0, 1.0, 1.0],
            [x_right, y_top, z_back,  1.0, 1.0, 1.0],
            [x_left, y_top, z_back,  1.0, 1.0, 1.0],
            
            # Face inferior (MARROM)
            [x_left, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_right, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_right, y_bottom, z_front,  1.0, 1.0, 1.0],
            [x_left, y_bottom, z_back,  1.0, 1.0, 1.0],
            [x_right, y_bottom, z_front,  1.0, 1.0, 1.0],
            [x_left, y_bottom, z_front,  1.0, 1.0, 1.0]
        ]
        
        self.qtdVertices = len(self.vertices)
        self.vertices_array = np.array(self.vertices, dtype=np.float32)
        self.configurar_buffers()
    
    def configurar_buffers(self):
        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)
        
        vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vboId)
        glBufferData(GL_ARRAY_BUFFER, self.vertices_array.nbytes, self.vertices_array, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6*4, ctypes.c_void_p(3*4))
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
    
    def render(self):
        glBindVertexArray(self.vaoId)
        glDrawArrays(GL_TRIANGLES, 0, self.qtdVertices)
        glBindVertexArray(0)