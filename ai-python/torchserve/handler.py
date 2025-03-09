import logging
import os
from collections import Counter

import torch
from torchvision import transforms
from ultralytics import YOLO

from ts.torch_handler.object_detector import ObjectDetector

logger = logging.getLogger(__name__)


class Yolov8Handler(ObjectDetector):
    def __init__(self):
        super(Yolov8Handler, self).__init__()

    def initialize(self, context):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        properties = context.system_properties
        self.manifest = context.manifest
        logger.debug(f"manifest: {self.manifest}")

        model_dir = properties.get("model_dir")
        self.model_pt_path = None
        if "serializedFile" in self.manifest["model"]:
            serialized_file = self.manifest["model"]["serializedFile"]
            self.model_pt_path = os.path.join(model_dir, serialized_file)
        self.model = self._load_torchscript_model(self.model_pt_path)
        logger.debug("Model file %s loaded successfully", self.model_pt_path)

        self.initialized = True

    def _load_torchscript_model(self, model_pt_path):
        model = YOLO(model_pt_path)
        model.to(self.device)
        return model

    def postprocess(self, res):
        output = []
        for data in res:
            output.append(data.tojson())
