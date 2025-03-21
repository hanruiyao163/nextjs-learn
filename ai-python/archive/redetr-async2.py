import cv2
import torch
import asyncio
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast

device = torch.device("cuda")

processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r101vd", cache_dir="./hf-models", use_fast=True)
model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r101vd", cache_dir="./hf-models")
model.to(device)
model.eval()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

# 性能优化参数
freq = cv2.getTickFrequency()
prev_tick = cv2.getTickCount()

stop_event = asyncio.Event()

async def read_frame():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame.")
    return frame

async def detect_objects():
    frame = await read_frame()
    inputs = processor(images=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast("cuda", dtype=torch.bfloat16):
            outputs = model(**inputs)
    return (frame, outputs)

# async def draw_results():
#     global prev_tick
#     while not stop_event.is_set():
#         if not result_queue.empty():
#             frame, outputs = result_queue.get_nowait()
#             target_sizes = torch.tensor([frame.shape[:2]])
#             results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)

#             for result in results:
#                 for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
#                     score, label = score.item(), label_id.item()
#                     box = [int(i) for i in box.tolist()]
#                     x1, y1, x2, y2 = box
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
#                     label_text = model.config.id2label[label]
#                     cv2.putText(
#                         frame, f"{label_text}: {score:.2f}", (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1
#                     )

#             curr_tick = cv2.getTickCount()
#             fps = freq / (curr_tick - prev_tick)
#             prev_tick = curr_tick
#             cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 1)

#             cv2.imshow("RT-DETR Object Detection", frame)
#             if cv2.waitKey(1) == ord("q"):
#                 stop_event.set()


# frame_queue = asyncio.Queue()
# result_queue = asyncio.Queue()

async def main():
    global prev_tick

    while not stop_event.is_set():
        frame, outputs = await detect_objects()
        target_sizes = torch.tensor([frame.shape[:2]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)

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

        cv2.imshow("RT-DETR Object Detection", frame)
        if cv2.waitKey(1) == ord("q"):
            stop_event.set()

asyncio.run(main())

cap.release()
cv2.destroyAllWindows()