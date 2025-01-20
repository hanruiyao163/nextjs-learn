import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid

import cv2
from aiohttp import web
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from av import VideoFrame
import numpy as np

ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
pcs = set()


class OpenCVVideoStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)  # 打开摄像头
        if not self.cap.isOpened():
            raise RuntimeError("Could not open video device")

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Could not read video frame")

        # 将 OpenCV 的 BGR 格式转换为 RGB 格式
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 将帧转换为 aiortc 所需的格式
        frame = np.ascontiguousarray(frame)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame

    def stop(self):
        self.cap.release()
        super().stop()

async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print(f"ICE connection state is {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # 添加视频流
    video_track = OpenCVVideoStreamTrack()
    pc.addTrack(video_track)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer)

    web.run_app(app,  port=8080)
