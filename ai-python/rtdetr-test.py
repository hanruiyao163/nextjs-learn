import cv2
import torch

from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast

device = torch.device("cuda")


processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models", use_fast=True)

model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models")
model.to(device)
model.eval()

cap = cv2.VideoCapture("rtsp://192.168.1.102/live/zoo1")
cap = cv2.VideoCapture("rtsp://192.168.1.102/live/zoo1")
if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

# 性能优化参数
freq = cv2.getTickFrequency()
prev_tick = cv2.getTickCount()
frame_count = 0
frame_skip = 1


def read_frame():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
    return frame


def detect_objects(frame):
    global prev_tick
    prev_tick = cv2.getTickCount()

    inputs = processor(images=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast("cuda", dtype=torch.bfloat16):
            outputs = model(**inputs)
    target_sizes = torch.tensor([frame.shape[:2]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)
    return results

def draw_results(frame, results):
    if not results:
        return
    
    if not results:
        return
    
    global prev_tick

    for result in results:
        for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
            score, label = score.item(), label_id.item()
            box = [int(i) for i in box.tolist()]
            x1, y1, x2, y2 = box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label_text = model.config.id2label[label]
            cv2.putText(
                frame, f"{label_text}: {score:.2f}", (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )
    curr_tick = cv2.getTickCount()
    fps = freq / (curr_tick - prev_tick)
    prev_tick = curr_tick
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1 , (0, 255, 0), 1)

    cv2.imshow("RT-DETR Object Detection", frame)


def detect_video():
    while True:
        frame = read_frame()
        frame_count = 0
        results = detect_objects(frame)
        draw_results(frame, results)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    while True:
        frame = read_frame()

        # 跳帧
        frame_count += 1
        if (frame_count % frame_skip) != 0:
            cv2.imshow("RT-DETR Object Detection", frame)
            print("Frame skipped:", frame_count)
        else:
            frame_count = 0
            results = detect_objects(frame)
            draw_results(frame, results)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
