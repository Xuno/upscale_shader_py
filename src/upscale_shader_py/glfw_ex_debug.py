from pathlib import Path
import numpy as np
from PIL import Image
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

BASE_RESOURCE = Path(__file__).parent.parent.parent.joinpath("resources")
IMG_DIR = BASE_RESOURCE.joinpath("images")
SHADER_DIR = BASE_RESOURCE.joinpath("shaders")


def load_shader(vertex_path, fragment_path):
    """Load and compile vertex and fragment shaders from files."""
    with open(vertex_path, 'r') as v_file, open(fragment_path, 'r') as f_file:
        vertex_src = v_file.read()
        fragment_src = f_file.read()

    try:
        # Compile shaders
        vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)

        # Check if shaders compiled successfully
        if not vertex_shader or not fragment_shader:
            raise RuntimeError("Shader compilation failed")

        # Link shaders into a program
        shader_program = compileProgram(vertex_shader, fragment_shader)
        return shader_program

    except Exception as e:
        print(f"Error loading shader: {e}")
        return None


def create_texture(image_path):
    """Load an image into an OpenGL texture."""
    try:
        image = Image.open(image_path).convert("RGBA")
        image_data = np.array(image, dtype=np.uint8)
        width, height = image.size

        if width == 0 or height == 0:
            raise ValueError("Texture image has no width or height.")

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture, width, height
    except Exception as e:
        print(f"Error loading texture: {e}")
        return None, 0, 0


def main(input_image_path, vertex_shader_path, fragment_shader_path):
    """Process an image using shaders and display it in the window."""
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW could not be initialized")

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(800, 600, "Offscreen Rendering", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window could not be created")

    # Make the window's context current
    glfw.make_context_current(window)

    # Load the shaders
    shader_program = load_shader(vertex_shader_path, fragment_shader_path)
    if not shader_program:
        glfw.terminate()
        return

    # Create a texture from the input image
    texture, width, height = create_texture(input_image_path)
    if texture is None:
        glfw.terminate()
        return

    # Define vertices and texture coordinates for a fullscreen quad
    vertices = np.array([
        -1.0, -1.0, 0.0, 0.0,  # Bottom-left (position, texCoord)
         1.0, -1.0, 1.0, 0.0,  # Bottom-right
         1.0,  1.0, 1.0, 1.0,  # Top-right
        -1.0,  1.0, 0.0, 1.0   # Top-left
    ], dtype=np.float32)

    # Create the VBO and VAO
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Position attribute
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Texture coordinate attribute
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(2 * 4))
    glEnableVertexAttribArray(1)

    # Unbind the VBO and VAO
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # Set the viewport
    glViewport(0, 0, 800, 600)

    # Use the shader program
    glUseProgram(shader_program)

    # Bind the input texture
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture)
    glUniform1i(glGetUniformLocation(shader_program, "input_texture"), 0)

    while not glfw.window_should_close(window):
        # Clear the screen to black
        glClear(GL_COLOR_BUFFER_BIT)

        # Bind the VAO and draw the quad
        glBindVertexArray(vao)
        glDrawArrays(GL_QUADS, 0, 4)
        glBindVertexArray(0)

        # Swap buffers and poll events
        glfw.swap_buffers(window)
        glfw.poll_events()

    # Clean up
    glDeleteTextures([texture])
    glUseProgram(0)
    glfw.terminate()


if __name__ == "__main__":
    input_image = IMG_DIR.joinpath("dicom_test-img-source.png")
    vertex_shader = SHADER_DIR.joinpath("texture_vertex.glsl")
    fragment_shader = SHADER_DIR.joinpath("texture_fragment.glsl")

    main(input_image, vertex_shader, fragment_shader)
