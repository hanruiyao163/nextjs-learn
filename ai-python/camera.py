from PIL import Image, ImageDraw, ImageFont
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
import time
import av
from utils import generate_random_color, draw_boxes
from ultralytics import YOLO, RTDETR

model = YOLO("yolo11n.pt", verbose=False)
prev_tick = time.perf_counter()


# input_url = "rtsp://localhost/live/zoo"
# output_url = " rtp://127.0.0.1:10000/live/camera"
output_url = "srt://127.0.0.1:10080?streamid=#!::r=live/livestream,m=publish"

# input_container = av.open(input_url)
input_container = av.open(
    "video=Iriun Webcam",
    format="dshow",
    options={
        "rtbufsize": "1024M",  # 增加缓冲区大小
        "framerate": "30",  # 设置帧率
        "thread_queue_size": "1024",  # 增加输入队列大小
        "fflags": "nobuffer",  # 减少输入缓冲
        "flags": "low_delay",  # 设置低延迟
    },
)
output_container = av.open(
    output_url,
    "w",
    format="mpegts",
    options={
        "fflags": "+genpts",
        "preset": "ultrafast",
        "tune":"zerolatency"
    }
)
input_stream = input_container.streams.video[0]
output_stream = output_container.add_stream("h264", rate=input_stream.base_rate)
# output_stream.width = input_stream.width
# output_stream.height = input_stream.height
output_stream.pix_fmt = "yuv420p"


frame_skip = 1
frame_count = 0
if __name__ == "__main__":
    print("Starting detection")
    for frame in input_container.decode(input_stream):
        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        prev_tick = time.perf_counter()

        img = frame.to_ndarray(format="rgb24")
        # results = model(img, verbose=False)
        # new_img = results[0].plot()

        new_frame = av.VideoFrame.from_ndarray(img, format="rgb24")
        # new_frame.pts = frame.pts
        # new_frame.time_base = frame.time_base

        for packet in output_stream.encode(new_frame):
            output_container.mux(packet)

    for packet in output_stream.encode():
        output_container.mux(packet)

input_container.close()
output_container.close()
