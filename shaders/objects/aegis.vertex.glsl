#version 460

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

uniform mat4 projection;
uniform mat4 model;

out vec3 out_normal;
out vec3 out_fragPosition;

void main() {
    vec4 worldPosition = model * vec4(position, 1.0);
    out_fragPosition = worldPosition.xyz;
    out_normal = mat3(transpose(inverse(model))) * normal;

    gl_Position = projection * worldPosition;
}