"""
ESP32 配置模板
复制此文件为 config.py 并填入实际配置
config.py 已被 gitignore，不会提交到仓库
"""

# WiFi 配置
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# 阿里云 IoT 配置
PRODUCT_KEY = 'your_product_key'
DEVICE_NAME = 'your_device_name'
DEVICE_SECRET = 'your_device_secret'

# 阈值配置（可根据需要调整）
THRESHOLDS = {
    'TEMP_HIGH': 30.0,
    'TEMP_LOW': 15.0,
    'HUM_LOW': 40.0,
    'HUM_HIGH': 80.0,
    'LUX_LOW': 1.0,
    'LUX_HIGH': 550.0
}

# 时序配置
STARTUP_DELAY = 5           # 启动延迟（秒）
MANUAL_ACTION_COOLDOWN = 2  # 手动操作后避让时间（秒）
REPORT_INTERVAL = 1         # 数据上报周期（秒）
