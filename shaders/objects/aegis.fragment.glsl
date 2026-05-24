#version 460

in vec3 out_normal;
in vec3 out_fragPosition;

uniform vec4 color;
uniform vec3 camera;

out vec4 fragColor;

const vec3 LIGHT_DIRECTION = normalize(vec3(1.0, 1.5, 2.0));
const vec3 LIGHT_COLOR = vec3(1.0, 0.95, 0.88);

void main() {
    vec3 norm = normalize(out_normal);

    float ambient = 0.25;
    float diffuse = max(dot(norm, LIGHT_DIRECTION), 0.0) * 0.65;

    vec3 viewDirection = normalize(camera - out_fragPosition);
    vec3 reflectDirection = reflect(-LIGHT_DIRECTION, norm);
    float specular = pow(max(dot(viewDirection, reflectDirection), 0.0), 32.0) * 0.35;

    float light = ambient + diffuse + specular;
    vec3  lit = color.rgb * LIGHT_COLOR * light;

    fragColor = vec4(lit, color.a);
}