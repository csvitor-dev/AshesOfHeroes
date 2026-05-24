#version 460

uniform vec4 color;
uniform float alpha; 

out vec4 fragColor;

void main() {
    fragColor = vec4(color.rgb, color.a * alpha);
}
