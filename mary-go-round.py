"""
Mary, Go Round! - PyWeek #32 - Thomas Perl (thp.io)

How to play:

    You are the WHITE THING ("MARY").
    You go ROUND.
    Avoid GAPS to achieve HIGH SCORE.
    Use UP and DOWN arrow keys to set the next lane.

Dependencies:

    PySDL2 (+ SDL2 + SDL2_mixer)
    PyOpenGL (+ some kind of OpenGL driver)

This uses the fancy old fixed function pipeline of OpenGL. All is good.
If your (i)GPU is really old, disable the SDL_GL_SetAttribute lines.

"""

title = __doc__.strip().splitlines()[0]
howto = '\n'.join(__doc__.splitlines()[1:])

print(howto)

from sdl2 import *
from sdl2.sdlmixer import *
from ctypes import *
from OpenGL.GL import *

from math import sin, cos, pi
from colorsys import hsv_to_rgb
from random import choice


SDL_Init(SDL_INIT_EVERYTHING)

Mix_Init(0)
Mix_OpenAudio(44100, AUDIO_S16, 1, 1024)

w = 960
h = 540
aspect = w / h

lanes = 3
chunks = 13

explosion_sound = Mix_LoadWAV('explosion.wav'.encode())
jump_sounds = [Mix_LoadWAV(f'jump{lane}.wav'.encode()) for lane in range(lanes)]

SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 1)
SDL_GL_SetAttribute(SDL_GL_MULTISAMPLESAMPLES, 4)

win = SDL_CreateWindow(title.encode(), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, w, h, SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN)


ctx = SDL_GL_CreateContext(win)

def brick(layer, chunk, color, fat, alpha):
    angle0 = -rotate + (chunk * 360 / chunks) / 180 * pi
    angle1 = -rotate + ((chunk + 1) * 360 / chunks) / 180 * pi

    s0 = sin(angle0)
    s1 = sin(angle1)

    c0 = cos(angle0)
    c1 = cos(angle1)

    inner = 0.1
    step = 0.3
    width = 0.5 * step

    r0 = inner + step * (2 - layer)
    r1 = r0 + width

    if fat:
        r0 -= 0.03
        r1 += 0.03

    glBegin(GL_TRIANGLE_STRIP)
    glColor(*color, alpha)
    # inner 0 -- inner 1, inner
    glVertex2f(r0 * s0 / aspect, r0 * c0)
    glVertex2f(r0 * s1 / aspect, r0 * c1)
    glVertex2f(r1 * s0 / aspect, r1 * c0)
    glVertex2f(r1 * s1 / aspect, r1 * c1)
    glEnd()

rotate = 0
current_lane = 0
next_lane = 0

# difficulty settings
max_per_lane = 5
rotation_delta = 0.001

def update(dt):
    global rotate, rotation_delta
    rotate += rotation_delta * dt

walls = [[False for chunk in range(chunks)] for lane in range(lanes)]

last_chunk_laid = None
last_pos = None
last_collision = False
last_collision_coordinate = None
score = 0
max_health = 7
health = max_health

def render():
    global last_chunk_laid, last_pos, current_lane, next_lane, last_collision, last_collision_coordinate, score, health

    if last_collision:
        glClearColor(1, 1, 1, 1)
        last_collision = False
    else:
        glClearColor(.1, .1, .1, 1)

    glClear(GL_COLOR_BUFFER_BIT)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    pos = int((rotate+pi-(pi/chunks)) / (2 * pi) * chunks)
    if last_pos != pos:
        current_lane = next_lane
        last_pos = pos
        score += 1
        Mix_PlayChannel(-1, jump_sounds[current_lane], 0)
        last_collision_coordinate = None

    vis_a_vis = (int(pos) + int(chunks/2) + 1) % chunks
    if last_chunk_laid != vis_a_vis:
        for i in range(lanes):
            walls[i][vis_a_vis] = False
        put_lane = choice(list(range(lanes)))
        on_this_lane = sum(chunk for chunk in walls[put_lane])
        on_this_chunk = sum(walls[lane][vis_a_vis] for lane in range(lanes))
        if on_this_lane < max_per_lane and on_this_chunk == 0 and last_chunk_laid is not None and not walls[put_lane][last_chunk_laid]:
            walls[put_lane][vis_a_vis] = choice([True, False, False])
        last_chunk_laid = vis_a_vis

    hue_delta = 0.3

    lane_hues = [rotate*0.1+i*hue_delta for i in range(lanes)]

    for i in range(chunks):
        colors = [hsv_to_rgb(hue%1, 0.5+0.2*(i+rotate)%2, 0.8) for hue in lane_hues]

        for j in range(lanes):
            c = colors[j]

            collision = (current_lane == j and (i == (pos%chunks)))

            if walls[j][i]:
                if collision:
                    collision_coordinate = (j, i)
                    if last_collision_coordinate != collision_coordinate:
                        print('collision', j, i)
                        Mix_PlayChannel(-1, explosion_sound, 0)
                        health -= 1
                        if health == 0:
                            print(f"""
    Final score: {score}

    Thank you for playing :)
    Website: https://thp.io/
    Itch.io: https://thp.itch.io/
""")
                            raise SystemExit()
                    last_collision_coordinate = collision_coordinate
                    last_collision = True
            else:
                brick(j, i, c, False, 1.0)

    brick(current_lane, pos, (1, 1, 1), True, 0.9)
    brick(next_lane, (pos+1)%chunks, (1, 1, 1), True, 0.3)



started = SDL_GetTicks()

quit = False

e = SDL_Event()
while not quit:
    SDL_SetWindowTitle(win, f'{title} -- Score: {score} -- Health: {health}/{max_health}'.encode())
    while SDL_PollEvent(byref(e)):
        if e.type == SDL_QUIT:
            quit = True
            break
        elif e.type == SDL_KEYDOWN and e.key.repeat == 0:
            if e.key.keysym.sym == SDLK_UP:
                next_lane = min(lanes-1, (current_lane + 1))
            elif e.key.keysym.sym == SDLK_DOWN:
                next_lane = max(0, (current_lane - 1))
        #print(e)

    now = SDL_GetTicks()
    update(now - started)
    started = now

    render()
    SDL_GL_SwapWindow(win)

SDL_GL_DeleteContext(ctx)
SDL_DestroyWindow(win)
SDL_Quit()
