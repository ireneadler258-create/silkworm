"""
数据集样本可视化脚本
生成带有标注框的样本图片，用于论文插图
"""
import os
import cv2
import random

# 配置路径
DATASET_DIR = "datasets"
TRAIN_IMG_DIR = os.path.join(DATASET_DIR, "train", "images")
TRAIN_LABEL_DIR = os.path.join(DATASET_DIR, "train", "labels")
OUTPUT_DIR = "sample_visualizations"

# 类别配置
CLASS_NAMES = {0: "Unhealthy", 1: "Healthy"}
CLASS_COLORS = {0: (0, 0, 255), 1: (0, 255, 0)}  # 红色=生病，绿色=健康


def draw_bbox(img, label_path, class_names, colors):
    """在图片上绘制标注框"""
    h, w = img.shape[:2]
    
    if not os.path.exists(label_path):
        return img
    
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        
        cls_id = int(parts[0])
        cx, cy, bw, bh = map(float, parts[1:])
        
        # 转换为像素坐标
        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)
        
        # 绘制边界框
        color = colors.get(cls_id, (255, 255, 255))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # 绘制标签
        label = class_names.get(cls_id, str(cls_id))
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return img


def get_sample_images(img_dir, label_dir, n_per_class=3):
    """从每个类别中选取样本图片"""
    samples = {0: [], 1: []}
    
    for fname in os.listdir(img_dir):
        if not fname.endswith(('.jpg', '.jpeg', '.png')):
            continue
        
        label_path = os.path.join(label_dir, os.path.splitext(fname)[0] + '.txt')
        if not os.path.exists(label_path):
            continue
        
        with open(label_path, 'r') as f:
            first_line = f.readline().strip()
        
        if not first_line:
            continue
        
        cls_id = int(first_line.split()[0])
        if cls_id in samples and len(samples[cls_id]) < n_per_class:
            samples[cls_id].append(fname)
        
        # 检查是否收集够了
        if all(len(v) >= n_per_class for v in samples.values()):
            break
    
    return samples


def main():
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("正在选取样本图片...")
    samples = get_sample_images(TRAIN_IMG_DIR, TRAIN_LABEL_DIR, n_per_class=3)
    
    print(f"选取到 Unhealthy 样本: {len(samples[0])} 张")
    print(f"选取到 Healthy 样本: {len(samples[1])} 张")
    
    # 生成单独的样本图片
    for cls_id, filenames in samples.items():
        for i, fname in enumerate(filenames):
            img_path = os.path.join(TRAIN_IMG_DIR, fname)
            label_path = os.path.join(TRAIN_LABEL_DIR, os.path.splitext(fname)[0] + '.txt')
            
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            img = draw_bbox(img, label_path, CLASS_NAMES, CLASS_COLORS)
            
            out_name = f"sample_{CLASS_NAMES[cls_id].lower()}_{i+1}.jpg"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            cv2.imwrite(out_path, img)
            print(f"已保存: {out_path}")
    
    # 生成拼接图（用于论文）
    all_samples = []
    for cls_id in [0, 1]:
        for fname in samples[cls_id][:2]:  # 每类取2张
            img_path = os.path.join(TRAIN_IMG_DIR, fname)
            label_path = os.path.join(TRAIN_LABEL_DIR, os.path.splitext(fname)[0] + '.txt')
            
            img = cv2.imread(img_path)
            if img is None:
                continue
            
            img = draw_bbox(img, label_path, CLASS_NAMES, CLASS_COLORS)
            img = cv2.resize(img, (320, 320))
            all_samples.append(img)
    
    if len(all_samples) >= 4:
        # 2x2 拼接
        top_row = cv2.hconcat(all_samples[:2])
        bottom_row = cv2.hconcat(all_samples[2:4])
        grid = cv2.vconcat([top_row, bottom_row])
        
        grid_path = os.path.join(OUTPUT_DIR, "dataset_samples_grid.jpg")
        cv2.imwrite(grid_path, grid)
        print(f"已保存拼接图: {grid_path}")
    
    print("\n完成！图片保存在:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
