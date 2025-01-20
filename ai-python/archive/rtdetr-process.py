import cv2
import numpy as np
import torch
from multiprocessing import Process, Queue, Event
 
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast

processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models", use_fast=True)
model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models")
model.to("cuda")
model.eval()

frame_queue = Queue(maxsize=20)
processed_queue = Queue(maxsize=20)
stop_event = Event()

def read_frame(frame_queue, stop_event):
    cap = cv2.VideoCapture(0)
    while not stop_event.is_set():
        ret, frame = cap.read()
        if frame_queue.full():
            frame_queue.get()
        frame_queue.put(frame)
    cap.release()
    print("Read process exited.")


def process_frame(model, processor, frame_queue, processed_queue, stop_event):
    while not stop_event.is_set():
        if (frame_queue.empty()):
            continue
        frame = frame_queue.get()
        inputs = processor(images=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), return_tensors="pt").to("cuda")
        with torch.no_grad():
            with autocast("cuda", dtype=torch.bfloat16):
                outputs = model(**inputs)
        target_sizes = torch.tensor([frame.shape[:2]]).to("cuda")
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)
        processed_queue.put((frame, results))
    

    print("Process process exited.")


def draw_frame(model, processed_queue, stop_event):
    freq = cv2.getTickFrequency()
    while not stop_event.is_set():
        if (processed_queue.empty()):
            continue
        frame, results = processed_queue.get()
        prev_tick = cv2.getTickCount()

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
        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_event.set()
            break
    cv2.destroyAllWindows()
    print("Draw process exited.")

        
if __name__ == "__main__":
    read_process = Process(target=read_frame, args=(frame_queue,stop_event))
    process_process = Process(target=process_frame, args=(model, processor, frame_queue, processed_queue, stop_event))
    draw_process = Process(target=draw_frame, args=(model, processed_queue,stop_event))

    read_process.start()
    process_process.start()
    draw_process.start()

    # 等待绘制进程结束
    draw_process.join()

    # 确保其他进程也能正确终止
    read_process.terminate()
    process_process.terminate()

    read_process.join()
    process_process.join()

    # 确保队列被正确关闭和释放
    frame_queue.close()
    frame_queue.join_thread()
    processed_queue.close()
    processed_queue.join_thread()

    print("Main process exited.")
