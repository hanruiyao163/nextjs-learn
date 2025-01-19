
import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
import time
import av
import cv2

device = torch.device("cuda")


processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models", use_fast=True)

model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models")
model.to(device)
model.eval()

font = ImageFont.truetype(r"C:\Users\hanma\AppData\Local\Microsoft\Windows\Fonts\MapleMono-NF-CN-Regular.ttf", 24)
prev_tick = time.perf_counter()


def read_frame():
    pass


def detect_objects(frame):
    inputs = processor(images=frame, return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast("cuda", dtype=torch.bfloat16):
            outputs = model(**inputs)
    target_sizes = torch.tensor([frame.shape[:2]])

    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.35)
    return results


def draw_results(frame, results):
    global prev_tick

    for result in results:
        for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
            score, label = score.item(), label_id.item()
            box = [int(i) for i in box.tolist()]
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0,0,255), 2)
            label_text = model.config.id2label[label]
            cv2.putText(frame, label_text, (box[0], box[1]-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)


    curr_tick = time.perf_counter()
    fps = 1 / (curr_tick - prev_tick)
    prev_tick = curr_tick
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    return frame


input_url = 'rtmp://localhost/live/zoo'
output_url = 'rtmp://localhost/live/zoo-detect'

input_container = av.open(input_url)
output_container = av.open(output_url, 'w', format='flv')
input_stream = input_container.streams.video[0]
output_stream = output_container.add_stream('h264', rate=20)
output_stream.width = input_stream.width
output_stream.height = input_stream.height
output_stream.pix_fmt = 'yuv420p'


if __name__ == "__main__":
    for frame in input_container.decode(input_stream):
        img = frame.to_ndarray(format="rgb24")
        results = detect_objects(img)
        img = draw_results(img, results)


        new_frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        

        for packet in output_stream.encode(new_frame):
            output_container.mux(packet)

    for packet in output_stream.encode():
        output_container.mux(packet)

input_container.close()
output_container.close()        


        
