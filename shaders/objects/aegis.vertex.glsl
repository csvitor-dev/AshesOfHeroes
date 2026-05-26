#version 460

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;

uniform mat4 projection;
uniform mat4 camera;
uniform mat4 model;

out vec3 out_color;
out vec3 out_normal;
out vec3 fragPosition;

void main() {
    vec4 worldPosition = model * vec4(position, 1.0);
    fragPosition     = worldPosition.xyz;
    out_color        = color;
    gl_Position    = projection * camera * worldPosition;
}