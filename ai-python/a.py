import cv2
import numpy
import torch
import time
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from PIL import Image, ImageDraw

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()

    cv2.imshow("Network Camera", frame)

    if cv2.waitKey(1)==ord('q'):
        break


cap.release()
cv2.destroyAllWindows()