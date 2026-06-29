#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 projection;
uniform mat4 camera;
uniform mat4 model;

out vec3 out_color;

void main() {
    gl_Position = projection * camera * model * vec4(position, 1.0);
    out_color = color;
}