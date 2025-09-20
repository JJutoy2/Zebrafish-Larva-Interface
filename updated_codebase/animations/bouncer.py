from animations.base import Animation, register_animation
import pygame

@register_animation("bouncer")
class Bouncer(Animation):
    """
    An animation of a bouncing ball within a rectangular surface.
    Args:
        radius (int, optional): The radius of the ball in pixels. Defaults to 40.
        speed (tuple of float, optional): The initial velocity of the ball as (vx, vy) in pixels per second. Defaults to (300, 220).
        color (tuple of int, optional): The RGB color of the ball. Defaults to (255, 255, 255).
        bg (tuple of int, optional): The RGB color of the background. Defaults to (0, 0, 0).
    Attributes:
        r (int): The radius of the ball.
        vx (float): The horizontal velocity of the ball.
        vy (float): The vertical velocity of the ball.
        color (tuple of int): The RGB color of the ball.
        bg (tuple of int): The RGB color of the background.
        x (float): The current x-coordinate of the ball's center.
        y (float): The current y-coordinate of the ball's center.
        w (int): The width of the surface.
        h (int): The height of the surface.
    """
    def __init__(
            self,
            radius: int = 40,
            speed: tuple[float, float] = (300.0, 220.0),
            color: tuple[int, int, int] = (255, 255, 255),
            bg: tuple[int, int, int] = (0, 0, 0)
            ):
        self.r = int(radius)
        self.vx, self.vy = map(float, speed)
        self.color = color
        self.bg = bg
        self.x = self.y = 0
        self.w = self.h = 0

    def on_start(self, surface: pygame.Surface, **kwargs):
        self.w, self.h = surface.get_size()
        self.x, self.y = self.w / 2, self.h / 2

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < self.r or self.x > self.w - self.r:
            self.vx *= -1
            self.x = max(self.r, min(self.x, self.w - self.r))
        if self.y < self.r or self.y > self.h - self.r:
            self.vy *= -1
            self.y = max(self.r, min(self.y, self.h - self.r))

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.r)

