#version 410 core
layout (quads, equal_spacing, ccw) in;
out vec3 ourNormal;
out vec3 ourFragPos;
out vec3 ourColor;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 center;
uniform float height;
uniform float radius;
uniform vec3 color;
const float kPi = 3.14159265358979323846f;

void main()
{
    float u = gl_TessCoord.x;
    float v = gl_TessCoord.y;
    
    // Cylinder geometry generation
    float phi = 2.0f * kPi * u;
    float h = mix(0.0, height, v);
    vec3 pos = center + vec3(
        radius * cos(phi), 
        h, 
        radius * sin(phi)
    );
    
    gl_Position = projection * view * model * vec4(pos, 1.0f);
    ourFragPos = vec3(model * vec4(pos, 1.0f));
    ourNormal = vec3(transpose(inverse(model)) * vec4(
        cos(phi), 
        0.0, 
        sin(phi), 
        1.0f
    ));
    ourColor = color;
}