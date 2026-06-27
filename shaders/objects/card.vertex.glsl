#version 460

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uv;

uniform mat4 projection;
uniform mat4 camera;
uniform mat4 model;
uniform float face_flip;   // 0.0 = normal, 1.0 = flip V (for opponent-side cards)

out vec2 out_uv;

void main() {
    gl_Position = projection * camera * model * vec4(position, 1.0);
    out_uv = vec2(uv.x, mix(uv.y, 1.0 - uv.y, face_flip));
}