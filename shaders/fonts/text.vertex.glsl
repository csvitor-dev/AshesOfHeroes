#version 460

layout(location = 0) in vec2 position;
layout(location = 1) in vec2 uv;

uniform mat4 projection;

out vec2 out_uv;

void main() {
    gl_Position = projection * vec4(position, 0.0, 1.0);
    out_uv = uv;
}