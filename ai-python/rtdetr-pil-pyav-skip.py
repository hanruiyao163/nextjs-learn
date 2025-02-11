import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoImageProcessor, AutoModelForObjectDetection
from torch.amp import autocast
import time

# ffmpeg python binding
import av

# 随机颜色 锚框绘制（文字间隔等细节）
from utils import generate_random_color, draw_boxes  

device = torch.device("cuda")

processor = AutoImageProcessor.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models", use_fast=True)

model = AutoModelForObjectDetection.from_pretrained("PekingU/rtdetr_r18vd", cache_dir="./hf-models")
model.to(device)
model.eval()



# 混合精度 （context manager）
def detect_objects(frame):
    inputs = processor(images=frame, return_tensors="pt").to(device)
    with torch.no_grad():
        with autocast("cuda", dtype=torch.bfloat16):
            outputs = model(**inputs)
    target_sizes = torch.tensor([frame.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.35)
    return results

# 需要记录每种分类的颜色 保证所有帧分类颜色统一
CLASS_COLOR_MAP = {}

def draw_results(frame, results):
    global prev_tick
    draw = ImageDraw.Draw(frame)

    for result in results:
        for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
            score, label = score.item(), label_id.item()
            box = [int(i) for i in box]
            label_text = model.config.id2label[label]

            if label not in CLASS_COLOR_MAP:
                CLASS_COLOR_MAP[label] = generate_random_color()

            draw_boxes(draw, box, label_text, score, CLASS_COLOR_MAP[label], size=25)

    curr_tick = time.perf_counter()
    fps = 1 / (curr_tick - prev_tick)
    prev_tick = curr_tick
    draw.text((0, 0), f"RT-DETR FPS: {fps:05.2f}", fill="black", font_size=30)

input_url = "rtmp://localhost/live/zoo"
output_url = "rtmp://localhost/live/zoo-detect"

# 容器 音频视频等流的封装 （mkv...)
input_container = av.open(input_url)

# rtmp协议使用flv视频编码格式
# I B P GOP 64
output_container = av.open(output_url, "w", format="flv", options={
# 没啥用
})

# 视频流 视频流编码（h264 vp9 av1...）
input_stream = input_container.streams.video[0]

# property 与field不同 可以直接ffmpeg解码时转换宽高 比用python处理效率高
# input_stream.width = 640
# input_stream.height = 480

output_stream = output_container.add_stream("h264", rate=input_stream.base_rate)
output_stream.width = input_stream.width
output_stream.height = input_stream.height
print(input_stream.width, input_stream.height, input_stream.base_rate)

# 像素格式 y-亮度分量 u v-色度分量 4:2:0 的色度子采样格式 比未压缩的 RGB 格式要小得多
output_stream.pix_fmt = "yuv420p"

frame_skip = 2
frame_count = 0

if __name__ == "__main__":
    # 帧解码
    for frame in input_container.decode(input_stream):
        if frame_count % frame_skip != 0:
            frame_count += 1
            continue

        prev_tick = time.perf_counter()
        # 使用pillow来处理图像 pytorch直接支持pillow输入 比opencv好看 fps要慢3帧左右
        img = frame.to_image()
        results = detect_objects(img)
        draw_results(img, results)

        new_frame = av.VideoFrame.from_image(img)
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        frame_count = 1

        for packet in output_stream.encode(new_frame):
            # 编码后的帧通过多路复用合并至容器
            output_container.mux(packet)

    # 缓冲区剩余帧
    for packet in output_stream.encode():
        output_container.mux(packet)

input_container.close()
output_container.close()
