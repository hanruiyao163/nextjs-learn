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

cap = cv2.VideoCapture(0)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

output_container = av.open("rtsp://192.168.1.107/live/zoo-detect", mode="w", format="rtsp")
output_stream = output_container.add_stream("h264", rate=fps)  # 使用 H.264 编码
output_stream.width = width
output_stream.height = height
output_stream.pix_fmt = "yuv420p"  # 设置像素格式
output_stream.options = {"preset": "ultrafast", "tune": "zerolatency", "rtsp_transport": "tcp",}

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
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Error reading frame from webcam")
            break
    

        results = detect_objects(frame)
        frame = draw_results(frame, results)

        av_frame = av.VideoFrame.from_ndarray(frame, format="bgr24")

        for packet in output_stream.encode(av_frame):
            output_container.mux(packet)

    for packet in output_stream.encode():
        output_container.mux(packet)


if __name__ == "__main__":
    detect_video()
