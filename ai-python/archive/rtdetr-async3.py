import cv2
import torch
import asyncio
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
from concurrent.futures import ThreadPoolExecutor

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
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame.")
            break
        await frame_queue.put(frame)
        print("Frame added to queue")
        await asyncio.sleep(0.01)

async def detect_objects():
    while not stop_event.is_set():
        frame = await frame_queue.get()
        inputs = processor(images=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), return_tensors="pt").to(device)
        with torch.no_grad():
            with autocast("cuda", dtype=torch.bfloat16):
                outputs = model(**inputs)
        await result_queue.put((frame, outputs))


async def draw_results():
    global prev_tick
    while not stop_event.is_set():
        frame, outputs = await result_queue.get()
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

        await display_frame(frame)
        # await asyncio.sleep(0.01)

async def display_frame(frame):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, show_frame, frame)

def show_frame(frame):
    cv2.imshow("RT-DETR Object Detection", frame)
    if cv2.waitKey(1) == ord("q"):
        stop_event.set()
    print("Frame displayed")

frame_queue = asyncio.Queue()
result_queue = asyncio.Queue()

async def main():
    # 启动异步任务
    await asyncio.gather(read_frame(), detect_objects(), draw_results())

asyncio.run(main())

cap.release()
cv2.destroyAllWindows()