import cv2
import picamera
import io
import numpy as np

from pupil_detectors import Detector2D

detector = Detector2D()

eye_cam = picamera.PiCamera()
eye_cam.rotation = -90

scene_cam = cv2.VideoCapture(0)

def get_eye_img():
    stream = io.BytesIO()
    eye_cam.capture(stream, resize=(320, 240), format="jpeg")
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    frame = cv2.imdecode(data, 1)
    frame = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    return frame

def _params():
    with open("calibration.txt", "r") as f:
        lines = f.readlines()
        paramsx = list(map(lambda x: float(x), lines[:5]))
        paramsy = list(map(lambda y: float(y), lines[5:]))
        return (paramsx, paramsy)


params_x, params_y = _params()

model_x = lambda x, y: params_x[0] * x**2 + params_x[1] * y**2 + params_x[2] * x + params_x[3] * y + params_x[4]
model_y = lambda x, y: params_y[0] * x**2 + params_y[1] * y**2 + params_y[2] * x + params_y[3] * y + params_y[4]
#model_y = lambda x, y: params_y[0] * x + params_y[1] * y + params_y[2]

while True:
    _, scene = scene_cam.read()
    scene = cv2.resize(scene, (800, 600))
    
    eye = get_eye_img()
    result = detector.detect(eye)
    center = result["ellipse"]["center"]

    Sx = model_x(*center)
    Sy = model_y(*center)

    cv2.circle(scene, (int(Sx), int(Sy)), 35, (255, 0, 0), 2)

    cv2.imshow("Image", scene)
    cv2.waitKey(1)
