# controller.py
from multiprocessing import Process, Queue
from render_proc import renderer, Commands

class DisplayManager:
    def __init__(self):
        self.processes = {}
        self.queues = {}

    def start_display(self, display_index=0, size=(1280, 720)):
        if display_index in self.processes:
            return
        q = Queue()
        p = Process(target=renderer, args=(display_index, size[0], size[1], q), daemon=False)
        p.start()
        self.processes[display_index] = p
        self.queues[display_index] = q

    def load_animation(self, display_index, name, **params):
        self.queues[display_index].put((Commands.LOAD, {"name": name, "params": params}))

    def set_param(self, display_index, **params):
        self.queues[display_index].put((Commands.PARAM, params))

    def pause(self, display_index, flag=True):
        self.queues[display_index].put((Commands.PAUSE, flag))

    def stop_display(self, display_index):
        self.queues[display_index].put((Commands.QUIT, None))
        self.processes[display_index].join()
        del self.processes[display_index]
        del self.queues[display_index]

if __name__ == "__main__":
    import time
    from animations.base import _ANIM_REGISTRY
    from animations import Bouncer, VerticalGratings, RotatingArcs
    dm = DisplayManager()
    # Start on monitor 1 (0-based); change to 0 if single-monitor
    dm.start_display(0,size=(1920, 1080))
    
    dm.load_animation(0,"rotating_arcs", num_arcs=12, speed_deg_s=60)
    # dm.load_animation(0,"grating", wavelength_px=60, speed_px_s=180)
    # dm.load_animation(0,"bouncer", radius=60, speed=(420, 300))
    # time.sleep(3)  # Run for 10 seconds
    # dm.pause(0, True)
    # time.sleep(1)
    # dm.pause(0, False)
    # time.sleep(1)
    # Later from your UI thread or CLI, you can:
    # dm.set_param(1, color=(0,255,0))
    # dm.pause(1, True)
    # dm.load_animation(1, "grating", spatial_freq=0.1, speed_dps=30)
