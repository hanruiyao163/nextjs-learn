torch-model-archiver --model-name yolo11n --version 1.0 --serialized-file yolo11n.pt --handler handler.py --export-path model_store -f


docker run --rm -it --gpus all -p 127.0.0.1:8080:8080 -p 127.0.0.1:8081:8081 -p 127.0.0.1:8082:8082 -p 127.0.0.1:7070:7070 -p 127.0.0.1:7071:7071 -v /D/Programming/nextjs-learn/ai-python/torchserve/model_store:/home/model-server/model-store pytorch/torchserve:latest-gpu  bash -c "pip install opencv-python-headless ultralytics && torchserve --start --model-store /home/model-server/model-store --ncs --disable-token-auth  --enable-model-api"


torchserve --start --model-store D:\Programming\nextjs-learn\ai-python\torchserve\model_store --ncs --disable-token-auth  --enable-model-api


curl "localhost:8080/ping"
curl "localhost:8081/models"
curl -X POST "localhost:8081/models?model_name=yolo11n&url=yolo11n.mar&initial_workers=4&batch_size=2"
curl -vX PUT "http://localhost:8081/models/yolo11n?min_worker=1"

curl http://127.0.0.1:8080/predictions/yolov8n -T image.png

curl -X POST "localhost:8081/models?model_name=yolo11n&url=yolo11n.mar&initial_workers=1&batch_size=2&runtime=python&device=cpu"