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
    with open(vertex_path, 'r') as v_file, open(fragment_path, 'r') as f_file:
        vertex_src = v_file.read()
        fragment_src = f_file.read()

    # Compile shaders
    vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
    if glGetShaderiv(vertex_shader, GL_COMPILE_STATUS) != GL_TRUE:
        print(f"Vertex Shader compile failed: {glGetShaderInfoLog(vertex_shader)}")

    fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
    if glGetShaderiv(fragment_shader, GL_COMPILE_STATUS) != GL_TRUE:
        print(f"Fragment Shader compile failed: {glGetShaderInfoLog(fragment_shader)}")

    shader_program = compileProgram(vertex_shader, fragment_shader)
    if glGetProgramiv(shader_program, GL_LINK_STATUS) != GL_TRUE:
        print(f"Program Link failed: {glGetProgramInfoLog(shader_program)}")

    return shader_program


def create_texture(image_path):
    """Load an image into an OpenGL texture."""
    image = Image.open(image_path).convert("RGBA")
    image_data = np.array(image, dtype=np.uint8)
    width, height = image.size

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture, width, height


def main(input_image_path, vertex_shader_path, fragment_shader_path, output_image_path):
    if not glfw.init():
        raise Exception("GLFW could not be initialized")

    window = glfw.create_window(800, 600, "Offscreen Rendering", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window could not be created")

    glfw.make_context_current(window)

    shader_program = load_shader(vertex_shader_path, fragment_shader_path)
    texture, width, height = create_texture(input_image_path)

    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)

    output_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, output_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output_texture, 0)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError("Framebuffer is not complete")

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glViewport(0, 0, width, height)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glUseProgram(shader_program)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture)
    glUniform1i(glGetUniformLocation(shader_program, "input_texture"), 0)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(-1.0, -1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(1.0, -1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(1.0, 1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(-1.0, 1.0)
    glEnd()

    result = glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE)

    output_image = Image.fromarray(np.frombuffer(result, dtype=np.uint8).reshape((height, width, 4)))
    output_image = output_image.transpose(Image.FLIP_TOP_BOTTOM)
    output_image.save(output_image_path)

    glDeleteTextures([texture, output_texture])
    glDeleteFramebuffers(1, [fbo])
    glUseProgram(0)
    glfw.terminate()


if __name__ == "__main__":
    input_image = IMG_DIR.joinpath("dicom_test-img-source.png")
    vertex_shader = SHADER_DIR.joinpath("vertex_shader.glsl")
    fragment_shader = SHADER_DIR.joinpath("fragment_shader.glsl")
    output_image = IMG_DIR.joinpath("output.png")

    main(input_image, vertex_shader, fragment_shader, output_image)
