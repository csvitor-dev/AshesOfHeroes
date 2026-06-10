#version 460

in vec2 out_uv;

uniform sampler2D u_texture;
uniform vec4 color_tint;
uniform float alpha;
uniform float glow;

out vec4 fragColor;

const vec3 GLOW_COLOR = vec3(1.0, 0.85, 0.20);

void main() {
    vec4 texel = texture(u_texture, out_uv);

    if (texel.a < 0.05) discard;

    vec3 rgb = texel.rgb * color_tint.rgb;
    rgb = mix(rgb, GLOW_COLOR, glow * 0.35);

    fragColor = vec4(rgb, texel.a * color_tint.a * alpha);
}