# render_proc.py
import os, time, pygame
from multiprocessing import Process, Queue
from animations.base import make_animation, Animation

class Commands:
    LOAD = "LOAD_ANIM"
    PARAM = "SET_PARAM"
    PAUSE = "PAUSE"
    QUIT = "QUIT"

def renderer(display_index: int, width: int, height: int, cmd_q: Queue):
    os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"
    pygame.init()

    # Target a specific monitor (Pygame 2+)
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    surface = pygame.display.set_mode((width, height), flags, display=display_index)
    pygame.display.set_caption(f"Renderer@Display{display_index}")

    clock = pygame.time.Clock()
    running = True
    paused = False
    anim = None

    # Fixed timestep for simulation
    SIM_DT = 1.0 / 120.0
    accumulator = 0.0
    last = time.perf_counter()

    while running:
        # Handle window events immediately
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            if anim:
                anim.on_event(event)

        # Drain command queue quickly (non-blocking)
        try:
            while True:
                cmd, payload = cmd_q.get_nowait()
                if cmd == Commands.LOAD:
                    if anim:
                        anim.on_stop()
                    name = payload["name"]
                    params = payload.get("params", {})
                    anim = make_animation(name, **params)
                    anim.on_start(surface)
                elif cmd == Commands.PARAM and anim:
                    # Optional: set attributes dynamically
                    for k, v in payload.items():
                        setattr(anim, k, v)
                elif cmd == Commands.PAUSE:
                    paused = bool(payload)
                elif cmd == Commands.QUIT:
                    running = False
                # else: ignore unknowns
        except Exception as e:
            if isinstance(e, ValueError) or isinstance(e, TypeError):
                print(e)
                running = False
            # empty queue

        now = time.perf_counter()
        frame_dt = now - last
        last = now
        accumulator += frame_dt

        # Update with fixed timesteps for stable physics/stimuli
        if anim and not paused:
            while accumulator >= SIM_DT:
                anim.update(SIM_DT)
                accumulator -= SIM_DT

        # Draw once per loop
        if anim:
            anim.draw(surface)
        pygame.display.flip()

        # Cap render rate ~120 fps (or let vsync do its thing)
        clock.tick(120)

    if anim:
        anim.on_stop()
    pygame.quit()
