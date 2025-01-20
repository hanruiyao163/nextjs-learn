import cv2
from ultralytics import YOLO
import av

# Load the YOLO model
model = YOLO("yolo11n.pt", verbose=False)


input_container = av.open("rtsp://192.168.1.107/live/zoo2")
input_stream = input_container.streams.video[0]
rate = input_stream.base_rate


freq = cv2.getTickFrequency()
prev_tick = cv2.getTickCount()

width = input_stream.width
height = input_stream.height
fps = input_stream.base_rate

output_container = av.open("rtsp://192.168.1.107/live/zoo-detect", mode="w", format="rtsp")
stream = output_container.add_stream("h264", rate=30)
stream.width = width
stream.height = height
stream.pix_fmt = "yuv420p" 

for frame in input_container.decode(input_stream):

    frame = frame.to_ndarray(format="rgb24")
    results = model(frame, verbose=False)

    annotated_frame = results[0].plot()

    curr_tick = cv2.getTickCount()
    fps = freq / (curr_tick - prev_tick)
    prev_tick = curr_tick

    cv2.putText(annotated_frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

    av_frame = av.VideoFrame.from_ndarray(annotated_frame, format="rgb24")

    # 编码并推送帧
    for packet in stream.encode(av_frame):
        output_container.mux(packet)

input_container.close()
output_container.close()
