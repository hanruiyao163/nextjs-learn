import cv2
from ultralytics import YOLO

# Load the YOLO model
model = YOLO("yolo11n.pt", verbose=False)

# Open webcam (0 is usually the default camera)
cap = cv2.VideoCapture("rtsp://192.168.1.102/live/zoo1")

# Initialize FPS calculation
freq = cv2.getTickFrequency()
prev_tick = cv2.getTickCount()

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

    # Display the annotated frame
    cv2.imshow("YOLO Webcam Inference", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
