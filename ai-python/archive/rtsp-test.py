import av
import cv2
import numpy as np

# 输入 RTSP 流的 URL
input_rtsp_url = "rtsp://192.168.1.102/live/zoo1"

# 输出 RTSP 流的 URL（推流地址）
output_rtsp_url = "rtsp://192.168.1.102/live/zoo-detect"

# 打开输入 RTSP 流
input_container = av.open(input_rtsp_url)

# 获取输入视频流
input_stream = input_container.streams.video[0]
codec_context = input_stream.codec_context

# 创建输出 RTSP 流
output_container = av.open(output_rtsp_url, mode='w', format="rtsp")
output_stream = output_container.add_stream('h264', rate=input_stream.base_rate)
output_stream.width = codec_context.width
output_stream.height = codec_context.height
output_stream.pix_fmt = 'yuv420p'

# 遍历输入流的帧
for frame in input_container.decode(input_stream):
    # 将帧转换为 numpy 数组（BGR 格式）
    img = frame.to_ndarray(format='bgr24')
    
    # 使用 OpenCV 处理帧
    # 示例：将帧转换为灰度图
    processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)  # 转换回 BGR 格式

    # 将处理后的帧转换回 pyav 的帧格式
    processed_frame = av.VideoFrame.from_ndarray(processed_img, format='bgr24')

    # 将帧编码并写入输出流
    for packet in output_stream.encode(processed_frame):
        output_container.mux(packet)

# 刷新编码器缓冲区
for packet in output_stream.encode():
    output_container.mux(packet)

# 关闭输入和输出流
input_container.close()
output_container.close()