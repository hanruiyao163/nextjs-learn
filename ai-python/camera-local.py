from PIL import Image, ImageDraw, ImageFont
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
import time
import subprocess
import av
from utils import generate_random_color, draw_boxes
from ultralytics import YOLO, RTDETR

import cv2

model = YOLO("yolo11n.pt", verbose=False)
prev_tick = time.perf_counter()




input_container = av.open(
    "video=Iriun Webcam",
    format="dshow",
    options={
        "rtbufsize": "1024M",  
        "framerate": "30",  
        "thread_queue_size": "1024",  
        "fflags": "nobuffer",  
        "flags": "low_delay",  
    },
)

input_stream = input_container.streams.video[0]


frame_skip = 2
frame_count = 0
if __name__ == "__main__":
    print("Starting detection")
    for frame in input_container.decode(input_stream):
        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        prev_tick = time.perf_counter()

        img = frame.to_ndarray(format="rgb24")
        results = model(img, verbose=False)
        new_img = results[0].plot()


        cv2.imshow('Frame', cv2.cvtColor(new_img, cv2.COLOR_RGB2BGR))
        
        frame_count = 1
    
  
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 释放资源
cv2.destroyAllWindows()

input_container.close()
