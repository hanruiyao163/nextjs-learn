import cv2
import torch
from torch.cuda.amp import autocast
from threading import Thread
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
device = torch.device("cuda")

processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models", use_fast=True)

model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models")
model.to(device)
model.eval()

# 初始化摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 性能优化参数
frame_skip = 1  # 每n帧处理一次
frame_count = 0
freq = cv2.getTickFrequency()
prev_tick = cv2.getTickCount()

# 全局变量用于存储检测结果
detection_results = None

def detect_objects(frame):
    global detection_results
    inputs = processor(images=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast("cuda", dtype=torch.bfloat16):
            outputs = model(**inputs)
    target_sizes = torch.tensor([frame.shape[:2]]).to(device)
    detection_results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break

    frame_count += 1
    if frame_count % frame_skip == 0:
        # 启动新线程进行目标检测
        detection_thread = Thread(target=detect_objects, args=(frame,))
        detection_thread.start()

    # 绘制检测框
    if detection_results:
        for result in detection_results:
            for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
                score, label = score.item(), label_id.item()
                box = [int(i) for i in box.tolist()]
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                label_text = model.config.id2label[label]
                cv2.putText(
                    frame, f"{label_text}: {score:.2f}", (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1
                )

    # 计算FPS
    curr_tick = cv2.getTickCount()
    fps = freq / (curr_tick - prev_tick)
    prev_tick = curr_tick
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

    cv2.imshow("RT-DETR Object Detection", frame)

    # 按q退出，s/f调整帧率
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("s"):
        frame_skip = max(1, frame_skip - 1)
        print(f"Processing every {frame_skip} frame(s)")
    elif key == ord("f"):
        frame_skip += 1
        print(f"Processing every {frame_skip} frame(s)")

cap.release()
cv2.destroyAllWindows()