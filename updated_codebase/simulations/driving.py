import pygame
import sys
import queue
import threading

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ROAD_WIDTH = 300
ROAD_COLOR = (50, 50, 50)
GRASS_COLOR = (34, 139, 34)
CAR_COLOR = (255, 0, 0)
CAR_WIDTH, CAR_HEIGHT = 40, 60
FPS = 60
DEFAULT_SPEED = 5

# Communication Queues
command_queue = queue.Queue()
status_queue = queue.Queue()

# Car class
class Car:
    def __init__(self, x, y, speed=DEFAULT_SPEED):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = 0  # -1: left, 0: straight, 1: right
        self.on_road = True

    def move(self):
        self.x += self.direction * self.speed
        self.y -= self.speed  # Move up the screen (simulate forward)

    def rect(self):
        return pygame.Rect(self.x, self.y, CAR_WIDTH, CAR_HEIGHT)

    def check_on_road(self):
        left_road = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        right_road = left_road + ROAD_WIDTH
        car_rect = self.rect()
        # Check if car is fully within the road bounds
        if car_rect.left < left_road or car_rect.right > right_road:
            self.on_road = False
        else:
            self.on_road = True

    def status(self):
        return {
            'x': self.x,
            'y': self.y,
            'speed': self.speed,
            'on_road': self.on_road
        }

def handle_input(car, event):
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_LEFT, pygame.K_a):
            car.direction = -1
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            car.direction = 1
        elif event.key in (pygame.K_UP, pygame.K_w):
            car.speed += 1
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            car.speed = max(1, car.speed - 1)
    elif event.type == pygame.KEYUP:
        if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
            car.direction = 0

def process_command_queue(car):
    try:
        while True:
            cmd = command_queue.get_nowait()
            if cmd['type'] == 'move':
                car.direction = cmd.get('direction', 0)
                car.speed = cmd.get('speed', car.speed)
            elif cmd['type'] == 'set_speed':
                car.speed = cmd['speed']
            elif cmd['type'] == 'set_direction':
                car.direction = cmd['direction']
    except queue.Empty:
        pass

def send_status(car):
    status_queue.put(car.status())

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Driving Simulation")
    clock = pygame.time.Clock()

    # Initial car position: center of road, near bottom
    car = Car(
        x=(SCREEN_WIDTH - CAR_WIDTH) // 2,
        y=SCREEN_HEIGHT - CAR_HEIGHT - 20
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            handle_input(car, event)

        process_command_queue(car)
        car.move()
        car.check_on_road()
        send_status(car)

        # Drawing
        screen.fill(GRASS_COLOR)
        road_rect = pygame.Rect(
            (SCREEN_WIDTH - ROAD_WIDTH) // 2, 0, ROAD_WIDTH, SCREEN_HEIGHT
        )
        pygame.draw.rect(screen, ROAD_COLOR, road_rect)
        pygame.draw.rect(screen, CAR_COLOR, car.rect())

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# Example: Thread to print car status from status_queue
def status_printer():
    while True:
        status = status_queue.get()
        print("Car status:", status)

if __name__ == "__main__":
    # Start status printer thread (optional)
    threading.Thread(target=status_printer, daemon=False).start()
    main()