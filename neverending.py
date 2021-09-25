from sdl2 import *
from ctypes import *
from OpenGL.GL import *
from math import *


SDL_Init(SDL_INIT_EVERYTHING)

w = 960
h = 540
aspect = w / h

chunks = 13

win = SDL_CreateWindow(b'Neverending - PyWeek 0b100000 (32) - thp.io',
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, w, h, SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN)

ctx = SDL_GL_CreateContext(win)

def brick(layer, chunk, color):
    angle0 = rotate + (chunk * 360 / chunks) / 180 * pi
    angle1 = rotate + ((chunk + 1) * 360 / chunks) / 180 * pi

    s0 = sin(angle0)
    s1 = sin(angle1)

    c0 = cos(angle0)
    c1 = cos(angle1)

    inner = 0.1
    step = 0.3
    width = 0.5 * step

    r0 = inner + step * (2 - layer)
    r1 = r0 + width

    glBegin(GL_TRIANGLE_STRIP)
    glColor(*color)
    # inner 0 -- inner 1, inner
    glVertex2f(r0 * s0 / aspect, r0 * c0)
    glVertex2f(r0 * s1 / aspect, r0 * c1)
    glVertex2f(r1 * s0 / aspect, r1 * c0)
    glVertex2f(r1 * s1 / aspect, r1 * c1)
    glEnd()

rotate = 0
lane = 0

def update(dt):
    global rotate
    rotate += 0.0001 * dt

def render():
    glClearColor(.2, .2, .2, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    pos = rotate / pi * chunks

    for i in range(chunks):
        c = (0, 0.5 / ((i+1)*.1), 0, 1)
        if lane == 0 and (i <= pos <= i+1 or i <= pos+1 <= i+1):
            c = (1, 0, 0, 1)
        brick(0, i, c)
        c = (0, 0, 0.5 / ((i+1)*.1), 1)
        brick(1, i, c)
        c = (0.5 / ((i+1)*.1), 0, 0, 1)
        brick(2, i, c)

    brick(lane, pos, (1, 1, 1, 1))



started = SDL_GetTicks()

quit = False

e = SDL_Event()
while not quit:
    while SDL_PollEvent(byref(e)):
        if e.type == SDL_QUIT:
            quit = True
            break
        elif e.type == SDL_KEYDOWN and e.key.repeat == 0:
            if e.key.keysym.sym == SDLK_1:
                lane = 0
            elif e.key.keysym.sym == SDLK_2:
                lane = 1
            elif e.key.keysym.sym == SDLK_3:
                lane = 2
        #print(e)

    now = SDL_GetTicks()
    update(now - started)
    started = now

    render()
    SDL_GL_SwapWindow(win)

SDL_GL_DeleteContext(ctx)
SDL_DestroyWindow(win)
SDL_Quit()
