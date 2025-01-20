import cv2
import torch

from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
import av

device = torch.device("cuda")
processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models", use_fast=True)
model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models")
model.to(device)
model.eval()

input_container = av.open("rtsp://192.168.1.107/live/zoo1")
# input_container = av.open("0")
input_stream = input_container.streams.video[0]

rate = input_stream.base_rate


output_container = av.open("rtsp://192.168.1.107/live/zoo-detect", mode="w", format="rtsp")
output_stream = output_container.add_stream("h264", rate=30) 
output_stream.width = input_stream.width
output_stream.height = input_stream.height
output_stream.pix_fmt = "yuv420p"
output_stream.options = {
    "preset": "ultrafast",
    "tune": "zerolatency",
    "rtsp_transport": "tcp",
    "err_detect": "ignore_err",
    "maxrate": "800k",
    "bufsize": "3200k"
}

freq = cv2.getTickFrequency()
prev_tick = cv2.getTickCount()


def detect_objects(frame):
    inputs = processor(images=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast("cuda", dtype=torch.bfloat16):
            outputs = model(**inputs)
    target_sizes = torch.tensor([frame.shape[:2]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.3)
    return results


def draw_results(frame, results):
    global prev_tick
    for result in results:
        for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
            score, label = score.item(), label_id.item()
            box = [int(i) for i in box.tolist()]
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label_text = model.config.id2label[label]
            cv2.putText(
                frame, f"{label_text}: {score:.2f}", (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1
            )
    curr_tick = cv2.getTickCount()
    fps = freq / (curr_tick - prev_tick)
    prev_tick = curr_tick
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)
    return frame


def detect_video():
    for frame in input_container.decode(input_stream):
        frame = frame.to_ndarray(format="rgb24")

        results = detect_objects(frame)
        frame = draw_results(frame, results)

        av_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")

        for packet in output_stream.encode(av_frame):
            output_container.mux(packet)

    for packet in output_stream.encode():
        output_container.mux(packet)


if __name__ == "__main__":
    detect_video()
