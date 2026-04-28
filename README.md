# Silkworm Project

蚕养殖智能监控系统 - 一个基于 ESP32、K230 AI 模块和微信小程序的物联网项目。

## 项目结构

```
silkworm/
├── ai/                 # YOLO 蚕体检测模型训练
│   ├── train.py        # 训练脚本
│   ├── yolo*.pt        # 预训练模型
│   └── datasets/        # 训练数据集（不含）
│
├── esp32/              # ESP32-S3 固件
│   ├── main.py         # 主程序
│   ├── K230/           # K230 视觉识别模块
│   └── *.py            # 各传感器驱动
│
└── miniprogram/        # 微信小程序
    ├── src/            # 源代码
    └── pages/          # 页面组件
```

## 主要功能

- **环境监测**: 温度、湿度、光照、CO2、NH3、土壤湿度
- **AI 视觉**: K230 模块病蚕识别
- **双向控制**: 风扇/加热器/雾化器/灯光
- **云端通信**: 阿里云 IoT MQTT
- **小程序**: 实时监控与控制

## 配置说明

首次使用请替换以下占位符为实际值：

### ESP32 固件 (`esp32/main.py`)
```python
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PRODUCT_KEY = 'your_product_key'
DEVICE_NAME = 'your_device_name'
DEVICE_SECRET = 'your_device_secret'
```

### K230 模块 (`esp32/K230/main.py`)
```python
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
IMG_BB_KEY = "YOUR_IMGBB_API_KEY"
```

### 微信小程序 (`miniprogram/src/store/device.ts`)
```typescript
const options = {
    productKey: 'your_product_key',
    deviceName: 'your_device_name',
    deviceSecret: 'your_device_secret',
    // ...
};
```

## 注意事项

- `datasets/` 训练数据集未包含（按要求排除）
- 使用前请配置阿里云 IoT 设备信息
- K230 模块需要单独的固件烧录

## 技术栈

- ESP32-S3 (MicroPython)
- K230 AI Module (Kendryte)
- YOLO11n/YOLO26n
- 微信小程序 (uni-app + Vue3 + TypeScript)
- 阿里云 IoT Platform