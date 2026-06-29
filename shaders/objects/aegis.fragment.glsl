#version 330 core

in vec3 out_color;
// in vec3 out_normal;

out vec4 fragColor;

// const vec3 LIGHT_DIRECTION = normalize(vec3(0.3, 0.0, 1.0));
// const vec3 LIGHT_COLOR = vec3(1.0, 0.95, 0.88);

void main() {
    // float ambient = 0.30;
    // float diffuse = max(dot(out_normal, LIGHT_DIRECTION), 0.0) * 0.70;
    // float light = ambient + diffuse;
    
    fragColor = vec4(out_color, 1.0);
}