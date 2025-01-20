import cv2
from ultralytics import YOLO
import av

# Load the YOLO model
model = YOLO("yolo11n.pt", verbose=False)

# Open webcam (0 is usually the default camera)
cap = cv2.VideoCapture("rtsp://192.168.1.107/live/zoo2")

# Initialize FPS calculation
freq = cv2.getTickFrequency()
prev_tick = cv2.getTickCount()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

output_container = av.open("rtsp://192.168.1.107/live/zoo-detect", mode="w", format="rtsp")
stream = output_container.add_stream("h264", rate=fps)  # 使用 H.264 编码
stream.width = width
stream.height = height
stream.pix_fmt = "yuv420p"  # 设置像素格式
stream.options = {"preset": "ultrafast", "tune": "zerolatency", "rtsp_transport": "tcp",}

while cap.isOpened():
    # Read a frame from the webcam
    success, frame = cap.read()
    
    if not success:
        print("Error reading frame from webcam")
        break

    # Run YOLO inference
    results = model(frame, verbose=False)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Calculate FPS
    curr_tick = cv2.getTickCount()
    fps = freq / (curr_tick - prev_tick)
    prev_tick = curr_tick

    # Display FPS on frame
    cv2.putText(annotated_frame, f"FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

    av_frame = av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")

        # 编码并推送帧
    for packet in stream.encode(av_frame):
        output_container.mux(packet)
    
# Release the video capture object and close the display window
cap.release()

