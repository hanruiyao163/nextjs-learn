from ultralytics import YOLO

from onnx import __version__, IR_VERSION
from onnx.defs import onnx_opset_version
print(f"onnx.__version__={__version__!r}, opset={onnx_opset_version()}, IR_VERSION={IR_VERSION}")       