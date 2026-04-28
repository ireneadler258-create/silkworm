# --- START OF FILE main.py ---
import time
import ujson
from machine import Pin
from wifi_conn import WiFiManager
from dht_reader import read_dht22
from mq137_reader import read_mq137
from bh1750_reader import read_bh1750
from soil_reader import read_soil
from gps_reader import read_gps
from co2_reader import read_co2
from ir_reader import init_ir, read_ir
from k230_reader import read_k230
from actuator_controller import Actuator
from aliyun_mqtt import MQTTManager, publish_data
from system_guardian import Guardian, get_timestamp
from smart_control import SmartController
from voice_alert import VoiceAlert


# ============ 配置区域 ============

# 阈值配置
THRESHOLDS = {
    'TEMP_HIGH': 30.0, 'TEMP_LOW': 15.0,
    'HUM_LOW': 40.0, 'HUM_HIGH': 80.0,
    'LUX_LOW': 1.0, 'LUX_HIGH': 550.0
}

# 网络配置 (请替换为实际WiFi信息)
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

# 阿里云配置 (请替换为实际阿里云IoT设备信息)
PRODUCT_KEY = 'your_product_key'
DEVICE_NAME = 'your_device_name'
DEVICE_SECRET = 'your_device_secret'

# 时序配置
STARTUP_DELAY = 5           # 启动延迟（秒）
MANUAL_ACTION_COOLDOWN = 2  # 手动操作后避让时间（秒）
REPORT_INTERVAL = 1         # 数据上报周期（秒）


# ============ 全局状态 ============

last_action_time = 0  # 最后手动操作时间
last_report_time = 0  # 最后上报时间


# ============ MQTT回调 ============

def mqtt_callback(topic, msg):
    """处理云端下发的指令"""
    global last_action_time
    try:
        t = topic.decode()
        m = msg.decode()
        print(f"[指令] 收到: {t}")
        
        last_action_time = time.time()
        data = ujson.loads(m)
        
        # 兼容物模型params和自定义数据包
        params = data.get("params", data)
        
        if isinstance(params, dict):
            for prop, value in params.items():
                brain.handle_command(prop, value)
            
            # 回发当前状态给云端
            current_status = brain.get_all_status()
            mqtt_client.publish(current_status)
            
    except Exception as e:
        print(f"[回调] 解析失败: {e}")


# ============ 系统初始化 ============

print(f"系统将在{STARTUP_DELAY}秒后启动...")
time.sleep(STARTUP_DELAY)

# 初始化守护者（看门狗）
guardian = Guardian(timeout_ms=300000)

# 初始化WiFi管理器
wifi_manager = WiFiManager(SSID, PASSWORD)
wifi_connected = wifi_manager.connect()

# 初始化MQTT管理器
mqtt_client = MQTTManager(PRODUCT_KEY, DEVICE_NAME, DEVICE_SECRET, callback=mqtt_callback)

if wifi_connected:
    mqtt_connected = mqtt_client.connect()
    if not mqtt_connected:
        print("[警告] MQTT初始连接失败，将在主循环中重试")
else:
    print("[警告] WiFi初始连接失败，将在主循环中重试")

# 硬件对象初始化
fan = Actuator(7, "风扇", active_high=False)
heater = Actuator(10, "加热器", active_high=False)
atomizer = Actuator(11, "雾化器", active_high=True)
alert_led = Actuator(2, "报警灯", active_high=True)
l_r = Actuator(42, "红", active_high=True)
l_g = Actuator(41, "绿", active_high=True)
l_b = Actuator(40, "蓝", active_high=True)

# 传感器引脚
ir_sensor_pin = init_ir(1)

# 创建智能控制器
brain = SmartController(fan, heater, atomizer, alert_led, l_r, l_g, l_b, THRESHOLDS)

# 初始化语音报警模块（与CO2/GPS共用UART1控制器，使用不同引脚）
voice = VoiceAlert(brain, uart_id=1, tx_pin=12, rx_pin=19)

print("--- 智慧蚕箱系统：双向控制模式启动 ---")


# ============ 连接管理函数 ============

def ensure_connections():
    """确保WiFi和MQTT连接，断开时自动重连"""
    # 检查WiFi
    if not wifi_manager.ensure_connected():
        return False
    
    # 检查MQTT
    if not mqtt_client.is_connected():
        print("[系统] MQTT断连，尝试重连...")
        mqtt_client.reconnect(wifi_connected=True)
    
    return mqtt_client.is_connected()


def publish_sensor_data(data):
    """发布传感器数据，带连接检查"""
    if not mqtt_client.is_connected():
        print("[系统] MQTT未连接，跳过数据发布")
        return False
    
    success = mqtt_client.publish(data)
    if not success:
        # 发布失败，标记为断连，下次循环会重连
        print("[系统] 数据发布失败，将尝试重连")
    return success


def read_sensors():
    """读取所有传感器（快速）"""
    ai_data = read_k230()
    temp, hum = read_dht22(4)
    lux = read_bh1750(8, 9)
    nh3 = read_mq137(6)
    soil_hum = read_soil(5)
    ir_val = ir_sensor_pin.value()
    
    return ai_data, temp, hum, lux, nh3, soil_hum, ir_val


def read_slow_sensors():
    """读取慢速传感器（定时调用）"""
    co2_ppm = read_co2(guardian, mqtt_client)
    lon, lat, alt = read_gps(guardian, mqtt_client)
    return co2_ppm, lon, lat, alt


def build_data_packet(ai_data, temp, hum, lux, nh3, soil_hum, co2_ppm, lon, lat, alt, device_status):
    """构建上报数据包"""
    sensor_data = {
        "temperature": round(temp, 1) if temp is not None else None,
        "humidity": round(hum, 1) if hum is not None else None,
        "CO2": co2_ppm,
        "NH3": round(nh3, 2) if nh3 is not None else None,
        "lux": round(lux, 1) if lux is not None else None,
        "soilHumidity": round(soil_hum, 1) if soil_hum is not None else None,
        "Silkworm_Total": ai_data['total'],
        "Silkworm_Healthy": ai_data['healthy'],
        "Silkworm_Sick": ai_data['sick'],
        "Silkworm_Sleep": ai_data['sleep'],
        "SickImageUrl": ai_data.get('sick_image_url', '')  # 病蚕图片URL
    }
    sensor_data.update(device_status)
    
    if lon is not None:
        sensor_data["GeoLocation"] = {
            "Longitude": lon,
            "Latitude": lat,
            "Altitude": alt,
            "CoordinateSystem": 1
        }
    
    return sensor_data


# ============ 主循环 ============

print("[系统] 进入主循环")

# 初始化CO2和GPS缓存值
cached_co2 = None
cached_lon, cached_lat, cached_alt = None, None, None

while True:
    try:
        loop_start = time.time()
        
        # 1. 喂狗
        guardian.feed()
        
        # 2. 确保连接
        connections_ok = ensure_connections()
        
        # 3. 检查云端指令（仅在连接正常时）
        if connections_ok:
            try:
                mqtt_client.check_msg()
            except Exception as e:
                print(f"[MQTT] 检查消息异常: {e}")
                mqtt_client.connected = False
        
        # 4. 读取快速传感器（每次都读）
        ai_data, temp, hum, lux, nh3, soil_hum, ir_val = read_sensors()
        
        # 5. 智能控制决策
        sensor_dict = {'temp': temp, 'hum': hum, 'lux': lux, 'ir': ir_val}
        control_logs = brain.update(sensor_dict, ai_data)
        device_status = brain.get_all_status()
        
        # 6. 打印状态
        mode_name = "手动" if device_status.get("ManualMode") == 1 else "自动"
        temp_msg = control_logs.get('temp_msg', '')
        hum_msg = control_logs.get('hum_msg', '')
        print(f"[{get_timestamp()}] 模式:{mode_name} | 温[{temp_msg}] 湿[{hum_msg}]")
        
        # 7. 语音报警检查
        voice.check_and_alert(temp, hum, lux, ir_val)
        
        # 8. 检查是否需要上报
        current_time = time.time()
        time_since_last_report = current_time - last_report_time
        time_since_last_action = current_time - last_action_time
        
        should_report = (
            time_since_last_report >= REPORT_INTERVAL and
            time_since_last_action > MANUAL_ACTION_COOLDOWN
        )
        
        if should_report:
            # 读取慢速传感器（定时读取）
            cached_co2, cached_lon, cached_lat, cached_alt = read_slow_sensors()
            
            # 构建并发布数据
            sensor_data = build_data_packet(
                ai_data, temp, hum, lux, nh3, soil_hum,
                cached_co2, cached_lon, cached_lat, cached_alt,
                device_status
            )
            
            publish_sensor_data(sensor_data)
            last_report_time = current_time
            
            print(f"[上报] 周期: {REPORT_INTERVAL}s")
        
        # 9. 内存清理
        guardian.collect_garbage()
        
        # 10. 计算循环耗时，调整sleep时间以保持稳定周期
        loop_elapsed = time.time() - loop_start
        sleep_time = max(0.1, 1.0 - loop_elapsed)  # 每秒一个循环周期
        time.sleep(sleep_time)
        
    except KeyboardInterrupt:
        print("\n[系统] 用户中断，正在关闭...")
        mqtt_client.disconnect()
        wifi_manager.disconnect()
        break
        
    except Exception as e:
        print(f"[系统] 主循环异常: {e}")
        time.sleep(1)
