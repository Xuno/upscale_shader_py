#version 330 core
in vec2 TexCoord;  // Texture coordinate from vertex shader
out vec4 FragColor;

uniform sampler2D input_texture;  // Texture sampler

void main() {
    // Sample the texture at the texture coordinates
    FragColor = texture(input_texture, TexCoord);
}
