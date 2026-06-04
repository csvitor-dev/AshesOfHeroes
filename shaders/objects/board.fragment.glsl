#version 460

in vec3 out_color;

uniform vec4 color;
uniform float alpha;

out vec4 fragColor;

void main() {
    vec3 final_color = (color.a > 0.01) ? color.rgb : out_color;
    fragColor = vec4(final_color, alpha);
}