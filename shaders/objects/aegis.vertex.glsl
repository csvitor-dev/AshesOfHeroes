#version 460

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 projection;
uniform mat4 camera;
uniform mat4 model;
uniform mat3 normal;

out vec3 out_color;
out vec3 out_normal;

void main() {
    vec4 worldPosition = model * vec4(position, 1.0);

    out_color = color;
    out_normal = normalize(normal * position);
    gl_Position = projection * camera * worldPosition;
}