#version 330 core

in vec3 Color;
in vec3 Normal;
in vec3 FragPos;

// --- DUAS LUZES ---
uniform vec3 light1_pos;
uniform vec3 light1_color;
uniform vec3 light2_pos;
uniform vec3 light2_color;

uniform vec3 viewPos;
uniform float constant = 1.0;
uniform float linear = 0.09;
uniform float quadratic = 0.032;

uniform vec4 color;   // não usado, pois usamos Color do vértice
uniform float alpha;

out vec4 fragColor;

const float AMBIENT_STRENGTH = 0.8;

vec3 calculatePointLight(vec3 lightPos, vec3 lightColor, vec3 fragPos, vec3 normal, vec3 baseColor) {
    vec3 lightDir = normalize(lightPos - fragPos);
    float distance = length(lightPos - fragPos);
    float attenuation = 1.0 / (constant + linear * distance + quadratic * (distance * distance));
    
    vec3 norm = normalize(normal);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = lightColor * baseColor * diff;
    
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 halfDir = normalize(lightDir + viewDir);
    float spec = pow(max(dot(norm, halfDir), 0.0), 16.0);
    vec3 specular = lightColor * spec * 0.3;
    
    return (diffuse + specular) * attenuation;
}

void main() {
    vec3 light1 = calculatePointLight(light1_pos, light1_color, FragPos, Normal, Color);
    vec3 light2 = calculatePointLight(light2_pos, light2_color, FragPos, Normal, Color);
    vec3 ambient = Color * AMBIENT_STRENGTH;
    vec3 finalColor = ambient + light1 + light2;
    
    fragColor = vec4(finalColor, alpha);
}