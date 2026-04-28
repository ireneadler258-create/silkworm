from ultralytics import YOLO

# 加载你训练好的 best.pt
model = YOLO("silkworm_project/health_detect_optimized_v2/weights/best.pt")

# 导出为 ONNX (K230 对 ONNX 版本有要求，通常建议使用固定尺寸)
model.export(format="onnx", imgsz=640, opset=11, simplify=True)