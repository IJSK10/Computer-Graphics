#version 410 core
layout (quads, equal_spacing, ccw) in;
out vec3 ourNormal;
out vec3 ourFragPos;
out vec3 ourColor;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 center;
uniform float majorRadius;  // Distance from the center of the tube to the center of the torus
uniform float minorRadius;  // Radius of the tube
uniform vec3 color;
const float kPi = 3.14159265358979323846f;

void main()
{
    float u = gl_TessCoord.x;
    float v = gl_TessCoord.y;
    
    // Parametric equations for a torus
    float phi = u * 2.0f * kPi;    // Angle around the major circle
    float theta = v * 2.0f * kPi;  // Angle around the minor circle
    
    // Torus geometry generation
    vec3 pos = center + vec3(
        (majorRadius + minorRadius * cos(theta)) * cos(phi),
        (majorRadius + minorRadius * cos(theta)) * sin(phi),
        minorRadius * sin(theta)
    );
    
    gl_Position = projection * view * model * vec4(pos, 1.0f);
    ourFragPos = vec3(model * vec4(pos, 1.0f));
    
    // Normal calculation for torus
    vec3 normal = vec3(
        cos(theta) * cos(phi),
        cos(theta) * sin(phi),
        sin(theta)
    );
    ourNormal = vec3(transpose(inverse(model)) * vec4(normal, 1.0f));
    
    ourColor = color;
}