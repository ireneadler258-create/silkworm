import os
from ultralytics import YOLO

def train_silkworm_optimized():
    model = YOLO("yolo11n.pt")  # 或 yolo11m.pt

    results = model.train(
        data="datasets/data.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        device=0,
        project="silkworm_project",
        name="health_detect_optimized_v2",  # 换个新名字避免混淆
        pretrained=True,
        optimizer="AdamW",
        lr0=0.001,
        # 损失权重调整（有效参数）
        box=10.0,      # 提高回归损失，让框更准
        cls=0.8,       # 提高分类损失，关注分类正确性
        dfl=2.0,       # 提高DFL损失
        # 数据增强（有效参数）
        mixup=0.2,     # 开启mixup
        copy_paste=0.3, # 开启copy-paste
        mosaic=1.0,    # 保持mosaic
        # 其他参数...
        verbose=True,
    )

    print("优化训练完成，模型保存在 silkworm_project/health_detect_optimized_v2/weights/best.pt")

if __name__ == "__main__":
    train_silkworm_optimized()