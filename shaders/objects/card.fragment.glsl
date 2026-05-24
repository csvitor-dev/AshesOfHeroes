#version 460

in vec2 out_uv;

uniform vec4 color_tint;
uniform float alpha;
uniform float glow;

out vec4 fragColor;

const vec3 GLOW_COLOR = vec3(1.0, 0.85, 0.20);

void main() {
    vec3 rgb = color_tint.rgb;
    rgb = mix(rgb, GLOW_COLOR, glow * 0.35);

    fragColor = vec4(rgb, color_tint.a * alpha);
}