import pygame
import cv2
import picamera
import io
import numpy as np

from scipy.optimize import least_squares
from scipy.optimize import curve_fit
from pupil_detectors import Detector2D

SCREEN_SIZE = (800, 600)
BLACK = (0, 0, 0)
POR_INTERVAL = 3000
pygame.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

running = True

picamera = picamera.PiCamera()
picamera.rotation = -90

detector = Detector2D()

def model(xs, a, b, c):
    return [x[0] * a + x[1] * b + c for x in xs]

def model2(xs, a, b, c, d, e):
    return [x[0]**2 * a + x[1]**2 * b + c*x[0] + d*x[1] + e for x in xs]


class Calibration:

    def __init__(self, scene_size):
        self.started = False
        self.start_time = None
        self.w, self.h = scene_size
        self.visible_point = None
        self.por = iter(self._por)
        self.xes = dict(zip(self._por, [(0,0)] * len(self._por))) 

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
                pygame.draw.circle(screen, (255, 0, 0), (int(self.visible_point[0]), int(self.visible_point[1])), 35)
                result = detector.detect(eye_img)
                if result["confidence"] >= 0.6:
                    xe = result["ellipse"]
                    self.xes[self.visible_point] = xe["center"]

    def write(self, out):
        print(self.xes)
        resx = curve_fit(model2, list(self.xes.values()), list(map(lambda p: p[0], self.xes.values())), method="lm")[0]
        resy = curve_fit(model2, list(self.xes.values()), list(map(lambda p: p[1], self.xes.values())), method="lm")[0]
        with open(out, "w") as file:
            file.writelines(map(lambda x: str(x) + "\n", resx))
            file.writelines(map(lambda x: str(x) + "\n", resy))


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
        stream = io.BytesIO() 
        picamera.capture(stream, resize=(320, 240), format="jpeg")
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        frame = cv2.imdecode(data, 1)
        eye_img = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        cv2.imshow("eye", eye_img)
        calibration.update(eye_img)
    except StopIteration:
        calibration.write("calibration.txt")
        running = False

    pygame.display.flip()
    clock.tick(24)

pygame.quit()
