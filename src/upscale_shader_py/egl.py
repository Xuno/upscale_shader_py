from pathlib import Path

from OpenGL.EGL import *
from OpenGL.GL import *
import numpy as np
from PIL import Image


BASE_RESOURCE = Path(__file__).parent.parent.parent.joinpath("tests")
print(BASE_RESOURCE)

exit()

# Initialize EGL display
egl_display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
eglInitialize(egl_display, None, None)

# Configure EGL
egl_config = eglChooseConfig(egl_display, [EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_NONE])[0]
egl_surface = eglCreatePbufferSurface(egl_display, egl_config, [EGL_WIDTH, 512, EGL_HEIGHT, 512, EGL_NONE])
egl_context = eglCreateContext(egl_display, egl_config, EGL_NO_CONTEXT, None)
eglMakeCurrent(egl_display, egl_surface, egl_surface, egl_context)

# Create and render to a texture
texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

# Render something or apply shaders here...
glClearColor(1.0, 0.0, 0.0, 1.0)  # Red background
glClear(GL_COLOR_BUFFER_BIT)

# Read pixels back to CPU
result = glReadPixels(0, 0, 512, 512, GL_RGBA, GL_UNSIGNED_BYTE)
image = Image.fromarray(np.frombuffer(result, dtype=np.uint8).reshape((512, 512, 4)))
image.save("output.png")

# Cleanup EGL
eglDestroySurface(egl_display, egl_surface)
eglDestroyContext(egl_display, egl_context)
eglTerminate(egl_display)
