
import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
import time
import av
from utils import generate_random_color, draw_boxes
import queue
import uuid
from concurrent.futures import ThreadPoolExecutor

device = torch.device("cuda")


processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models", use_fast=True)

model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models")
model.to(device)
model.eval()

prev_tick = time.perf_counter()


def detect_objects(idx, frame):
    inputs = processor(images=frame, return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast("cuda", dtype=torch.bfloat16):
            outputs = model(**inputs)
    target_sizes = torch.tensor([frame.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.35)
    output_queue.put((idx, results))


CLASS_COLOR_MAP = {}
def draw_results(frame, results):
    global prev_tick
    draw = ImageDraw.Draw(frame)

    for result in results:
        for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
            score, label = score.item(), label_id.item()
            box = [int(i) for i in box]
            label_text = model.config.id2label[label]

            if label not in CLASS_COLOR_MAP:
                CLASS_COLOR_MAP[label] = generate_random_color()

            draw_boxes(draw, box, label_text, score, CLASS_COLOR_MAP[label], size=25)

    curr_tick = time.perf_counter()
    fps = 1 / (curr_tick - prev_tick)
    prev_tick = curr_tick
    draw.text((0, 0), f"FPS: {fps:.2f}", fill="green", font_size=30)



input_url = 'rtmp://localhost/live/zoo'
output_url = 'rtmp://localhost/live/zoo-detect'

input_container = av.open(input_url)
output_container = av.open(output_url, 'w', format='flv')
input_stream = input_container.streams.video[0]
output_stream = output_container.add_stream('h264', rate=input_stream.base_rate)
output_stream.width = input_stream.width
output_stream.height = input_stream.height
output_stream.pix_fmt = 'yuv420p'


# input_queue = queue.Queue(maxsize=100)
output_queue = queue.PriorityQueue(100)

# def detect_callback(future):
#     frame_id, frame, results = future.result()
#     output_queue.put((frame_id, frame, results))

if __name__ == "__main__":
    future2frame = {}
    frame_idx = 0
    futures = []
    with ThreadPoolExecutor(3) as executor:
        for frame in input_container.decode(input_stream):
            image = frame.to_image()
            future = executor.submit(detect_objects, frame_idx, image)
            future2frame[future] = (frame_idx, image)
            frame_idx += 1

            while not output_queue.empty():
                idx, results = output_queue.get()
                frame_idx, image  = future2frame[future]
                draw_results(image, results)

                new_frame = av.VideoFrame.from_image(image)
                new_frame.pts = frame.pts
                new_frame.time_base = frame.time_base

                for packet in output_stream.encode(new_frame):
                    output_container.mux(packet)

    for packet in output_stream.encode():
        output_container.mux(packet)

input_container.close()
output_container.close()        


        
