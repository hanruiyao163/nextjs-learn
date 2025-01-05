import cv2
import numpy as np
import torch
import time
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast

device = torch.device("cuda")


# 加载RT-DETR模型
processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r101vd", cache_dir="./hf-models")

model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r101vd", cache_dir="./hf-models")
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
frame_skip = 5  # 每n帧处理一次
frame_count = 0
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        cv2.imshow("RT-DETR Object Detection", frame)
        continue

    # 目标检测
    inputs = processor(images=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast('cuda', dtype=torch.bfloat16):
            outputs = model(**inputs)   

    # outputs = [i.to("cpu") for i in outputs]  # 将输出移回CPU用于后续处理
    
    # 处理检测结果
    target_sizes = torch.tensor([frame.shape[:2]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)
    
    # 绘制检测框
    result_frame = frame.copy()
    for result in results:
        for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
            score, label = score.item(), label_id.item()
            box = [int(i) for i in box.tolist()]
            x1, y1, x2, y2 = box
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            label_text = model.config.id2label[label]
            cv2.putText(result_frame, f"{label_text}: {score:.2f}", 
                       (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (0, 0, 255), 1)

    # 计算FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    cv2.putText(result_frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

    cv2.imshow("RT-DETR Object Detection", result_frame)

    # 按q退出，s/f调整帧率
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        frame_skip = max(1, frame_skip - 1)
        print(f"Processing every {frame_skip} frame(s)")
    elif key == ord('f'):
        frame_skip += 1
        print(f"Processing every {frame_skip} frame(s)")

cap.release()
cv2.destroyAllWindows()
