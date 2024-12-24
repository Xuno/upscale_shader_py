from OpenGL.GL import *
import glfw
import numpy as np

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW could not be initialized")

# Create a windowed mode window and its OpenGL context
window = glfw.create_window(800, 600, "GLFW + OpenGL Example", None, None)
if not window:
    glfw.terminate()
    raise Exception("GLFW window could not be created")

# Make the window's context current
glfw.make_context_current(window)

# Set the clear color (background color)
glClearColor(0.2, 0.3, 0.3, 1.0)

# Main loop
while not glfw.window_should_close(window):
    # Clear the color buffer
    glClear(GL_COLOR_BUFFER_BIT)

    # Render a triangle
    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.0, 0.0)  # Red
    glVertex2f(-0.5, -0.5)
    glColor3f(0.0, 1.0, 0.0)  # Green
    glVertex2f(0.5, -0.5)
    glColor3f(0.0, 0.0, 1.0)  # Blue
    glVertex2f(0.0, 0.5)
    glEnd()

    # Swap front and back buffers
    glfw.swap_buffers(window)

    # Poll for and process events
    glfw.poll_events()

# Clean up and exit
glfw.terminate()
