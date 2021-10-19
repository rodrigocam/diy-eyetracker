import pygame
from scipy.optimize import least_squares

SCREEN_SIZE = (1280, 1024)
BLACK = (0, 0, 0)
POR_INTERVAL = 3000
pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

running = True

def linear_model(x, points):
    return [x[0] * p[0] + x[1] * p[1] + x[2] for p in points]


class Calibration:

    def __init__(self, scene_size):
        self.started = False
        self.start_time = None
        self.w, self.h = scene_size
        self.visible_point = None
        self.por = iter(self._por)
        self.xes = dict(zip(self._por, [None] * len(self._por))) 

    def start(self):
        if not self.started:    
            self.started = True
            self.start_time = pygame.time.get_ticks()
            self.visible_point = next(self.por)

    def update(self, eye_img):
        if self.started:
            if pygame.time.get_ticks() - self.start_time >= POR_INTERVAL:
                self.visible_point = next(self.por)
                self.start_time = pygame.time.get_ticks()
                
            if self.visible_point is not None:
                pygame.draw.circle(screen, (255, 0, 0), self.visible_point, 35)
                xe = detector.detect(eye_img)["ellipse"]
                self.xes[self.visible_point] = xe["center"]

    def write(self, out):
        x0 = [1.0, 1.2, 3.0]
        res = least_squares(linear_model, x0, self.xes.values())
        with open(out, "w") as file:
            file.write(res.x)

    @property
    def _por(self): 
        # points of regard
        return [
                (self.w * 0.05, self.h * 0.05), (self.w * 0.5, self.h * 0.05), (self.w * 0.95, self.h * 0.05),
                (self.w * 0.25, self.h * 0.25), (self.w * 0.75, self.h * 0.25),
                (self.w * 0.05, self.h * 0.5), (self.w * 0.5, self.h * 0.5), (self.w * 0.95, self.h * 0.5),
                (self.w * 0.25, self.h * 0.75), (self.w * 0.75, self.h * 0.75),
                (self.w * 0.05, self.h * 0.95), (self.w * 0.5, self.h * 0.95), (self.w * 0.95, self.h * 0.95),
                ]

calibration = Calibration(SCREEN_SIZE)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN and event.key == ord("s"):
            calibration.start()

    screen.fill(BLACK)
    try:
        eye_img = cv2.
        calibration.update(eye_img)
    except StopIteration:
        calibration.write("calibration.txt")
        running = False

    pygame.display.flip()
    clock.tick(24)

pygame.quit()
