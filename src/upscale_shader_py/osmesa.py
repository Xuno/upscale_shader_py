from pathlib import Path

from OpenGL import platform
from OpenGL import osmesa
from OpenGL.GL import *
import numpy as np
from PIL import Image

BASE_RESOURCE = Path(__file__).parent.parent.parent.joinpath("tests")
print(BASE_RESOURCE)

exit()

# Initialize offscreen rendering context (OSMesa)
osmesaContext = osmesa.OSMesaCreateContext(0, None)
osmesa.OSMesaMakeCurrent(osmesaContext, None, 0, 512, 512)

# Create framebuffer (offscreen buffer)
fbo = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, fbo)

# Set up texture to hold the output (1024x1024 for 2x upscaling)
output_width, output_height = 1024, 1024
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, output_width, output_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

# Load the compiled shader and weight file (.bin)
# Assuming you have a method to load and apply the shader binary to the OpenGL program
shader_program = load_shader("shader_shader.bin")  # Example, adjust as necessary

# Apply the shader and weights on an image or texture
glUseProgram(shader_program)

# Set up the texture for the input image (assuming 512x512 image)
input_texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, input_texture)

# Load your input image (512x512) or use the texture to apply transformations
input_image = Image.open("input_image.png")
input_image_data = np.array(input_image)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, input_image_data.shape[1], input_image_data.shape[0], 0, GL_RGBA, GL_UNSIGNED_BYTE, input_image_data)

# Render the input texture to the framebuffer using the shader for upscaling
glActiveTexture(GL_TEXTURE0)
glBindTexture(GL_TEXTURE_2D, input_texture)

# Apply the shader and render the upscale
# Assuming the shader does the necessary transformations for upscale
# (For example, it can use the current texture to scale to a larger size)
# Note: Depending on your shader, you may need to set uniform variables for texture and scale.

# Perform drawing to apply the shader
glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

# Extract the processed image (upscaled) from the framebuffer
glReadBuffer(GL_FRONT)
result = glReadPixels(0, 0, output_width, output_height, GL_RGBA, GL_UNSIGNED_BYTE)

# Save the output as an image
image = Image.fromarray(np.frombuffer(result, dtype=np.uint8).reshape((output_height, output_width, 4)))
image.save("output_upscaled.png")