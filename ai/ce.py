from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO("silkworm_project/health_detect_optimized_v2/weights/best.pt")
    metrics = model.val()  # 在验证集上评估
    print(metrics)