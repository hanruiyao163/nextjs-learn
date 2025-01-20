from fastapi import FastAPI, WebSocket
from aiortc import RTCPeerConnection, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder
import cv2
import asyncio
import numpy as np
import uvicorn

app = FastAPI()

class OpenCVVideoStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open video device")
        
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Failed to capture frame")
            
        # Convert frame to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to aiortc compatible format
        frame = np.ascontiguousarray(frame)
        return frame

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    pc = RTCPeerConnection()
    
    # Add video track
    video_track = OpenCVVideoStreamTrack()
    pc.addTrack(video_track)
    
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == "failed":
            await pc.close()
    
    try:
        while True:
            data = await websocket.receive_text()
            
            if data.startswith("offer"):
                # Handle offer
                offer = data[len("offer:"):]
                await pc.setRemoteDescription(offer)
                
                # Create answer
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                
                await websocket.send_text(f"answer:{answer.sdp}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await pc.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
