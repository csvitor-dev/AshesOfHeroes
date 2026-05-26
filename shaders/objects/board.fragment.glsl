#version 460

in vec3 out_color;

uniform float alpha;

out vec4 fragColor;

void main() {
    fragColor = vec4(out_color, alpha);
}