#version 330 core

in vec2 out_uv;

uniform sampler2D atlas;
uniform vec4 color;

out vec4 fragColor;

void main() {
    float coverage = texture(atlas, out_uv).r;
    fragColor = vec4(color.rgb, color.a * coverage);
}