#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

uniform sampler2D input_texture;

void main()
{
    vec4 color = texture(input_texture, TexCoords);
    FragColor = color; // Pass-through example
}
