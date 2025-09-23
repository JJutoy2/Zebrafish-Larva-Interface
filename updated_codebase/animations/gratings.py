from animations.base import Animation, register_animation
import numpy as np
import pygame
from pygame import gfxdraw

@register_animation("grating")
class VerticalGratings(Animation):
    """
    Simple vertical square-wave grating that drifts horizontally.
    Params (pixels, px/s): wavelength_px, speed_px_s, fg, bg
    """
    
    def __init__(self, 
                 wavelength_px=80, 
                 speed_px_s=120, 
                 speed_dt = 20,
                 fg=(255,255,255), 
                 bg=(0,0,0)
                 ):
        self.lambda_px = max(4, int(wavelength_px))
        self.speed = float(speed_px_s)
        self.speed_dt = float(speed_dt)
        self.fg, self.bg = fg, bg
        self.offset = 0.0  # px
        self.tile = None
        self.w = self.h = 0

    def on_start(self, surface: pygame.Surface, **kwargs):
        self.w, self.h = surface.get_size()
        # Build a 2*lambda tile of alternating bands to scroll
        period = self.lambda_px * 2
        self.tile = pygame.Surface((period, self.h))
        self.tile.fill(self.bg)
        # draw two bands per period: [0, lambda)=fg, [lambda, 2lambda)=bg (already)
        fg_rect = pygame.Rect(0, 0, self.lambda_px, self.h)
        pygame.draw.rect(self.tile, self.fg, fg_rect)

    def update(self, dt):
        self.offset = (self.offset - self.speed * dt) % (self.lambda_px * 2)

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg)
        # Tile the pattern across the width with the current offset
        start_x = -int(self.offset)
        x = start_x
        self.tile: pygame.Surface
        while x < self.w:
            surface.blit(self.tile, (x, 0))
            x += self.tile.get_width()

    def on_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    self.speed += self.speed_dt
                case pygame.K_DOWN:
                    self.speed -= self.speed_dt
                case pygame.K_RIGHT:
                    self.speed += self.speed_dt
                case pygame.K_LEFT:
                    self.speed -= self.speed_dt

@register_animation("rotating_arcs")
class RotatingArcs(Animation):
    """
    Rotating black and white arcs about the center of the screen.
    Params: num_arcs, speed_deg_s, fg, bg
    """
    def __init__(self, 
                 num_arcs=4, 
                 speed_deg_s=60, 
                 speed_dt=1,
                 fg=(255,255,255), 
                 bg=(0,0,0)
                 ):
        self.num_arcs = max(2, int(num_arcs))
        self.speed = float(speed_deg_s)
        self.speed_dt = float(speed_dt)
        self.fg, self.bg = fg, bg
        self.angle = 0.0  # degrees
        self.w = self.h = 0

    def update(self, dt):
        self.angle = (self.angle + self.speed * dt) % 360

    # Draw filled arcs instead of just outlines
    def create_arcs_image(self):
        arcs_surface = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        arc_angle = 360 / self.num_arcs
        for i in range(self.num_arcs):
            color = self.fg if i % 2 == 0 else self.bg
            start_angle = i * arc_angle
            end_angle = start_angle + arc_angle
            # Draw filled arc using pygame.draw.arc and fill with polygons
            points = [self.center]
            for a in np.linspace(start_angle, end_angle, num=30):
                rad = np.deg2rad(a)
                x = self.center[0] + self.radius * np.cos(rad)
                y = self.center[1] + self.radius * np.sin(rad)
                points.append((x, y))
            pygame.draw.polygon(arcs_surface, color, points)
        return arcs_surface
   
    def on_start(self, surface: pygame.Surface, **kwargs):
        self.w, self.h = surface.get_size()
        self.center = (self.w // 2, self.h // 2)
        self.radius = min(self.w, self.h) // 2
        self.arcs_image = self.create_arcs_image()

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg)
        # Rotate the arcs image and blit to the screen
        rotated = pygame.transform.rotate(self.arcs_image, self.angle)
        rect = rotated.get_rect(center=self.center)
        surface.blit(rotated, rect.topleft)

    def on_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    self.speed += self.speed_dt
                case pygame.K_DOWN:
                    self.speed -= self.speed_dt
                case pygame.K_RIGHT:
                    self.speed += self.speed_dt
                case pygame.K_LEFT:
                    self.speed -= self.speed_dt
                case pygame.K_n:  # Example: change number of arcs
                    self.num_arcs += 1
                    self.arcs_image = self.create_arcs_image()
                case pygame.K_m:  # Example: decrease number of arcs
                    self.num_arcs = max(2, self.num_arcs - 1)
                    self.arcs_image = self.create_arcs_image()
                case pygame.K_1:
                    self.speed = -10
                case pygame.K_2:
                    self.speed = 10