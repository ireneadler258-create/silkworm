# --- START OF FILE gps_reader.py ---
from machine import UART
import time

# 缓存GPS值和读取时间
_cached_lon = None
_cached_lat = None
_cached_alt = None
_last_read_time = 0
_read_interval = 30  # 每30秒读取一次

def convert_to_degrees(raw_val, direction):
    """将 NMEA 格式 ddmm.mmmm 转换为十进制度数"""
    if not raw_val or not direction:
        return 0.0
    try:
        dot_idx = raw_val.find('.')
        if dot_idx < 2: return 0.0
        minutes_raw = float(raw_val[dot_idx - 2:])
        degrees_raw = float(raw_val[:dot_idx - 2])
        decimal_degrees = degrees_raw + (minutes_raw / 60)
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return round(decimal_degrees, 6)
    except:
        return 0.0

def read_gps(guardian_obj=None, mqtt_client=None, force=False):
    """
    读取 GPS 数据（带缓存）
    
    Args:
        guardian_obj: 看门狗对象
        mqtt_client: MQTT客户端
        force: 强制读取（忽略缓存）
    """
    global _cached_lon, _cached_lat, _cached_alt, _last_read_time
    
    current_time = time.time()
    
    # 如果不需要强制读取，且缓存未过期，直接返回缓存
    if not force and (current_time - _last_read_time) < _read_interval:
        return _cached_lon, _cached_lat, _cached_alt
    
    print("[GPS] 开始读取...")
    
    # 执行读取
    try:
        gps_uart = UART(1, baudrate=9600, tx=18, rx=17, timeout=10)
        buffer = ""
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < 2200:
            if guardian_obj: 
                guardian_obj.feed()
            if mqtt_client:
                try:
                    mqtt_client.check_msg()
                except:
                    pass
            
            if gps_uart.any():
                try:
                    chunk = gps_uart.read().decode('ascii', 'ignore')
                    buffer += chunk
                    
                    if len(buffer) > 2048:
                        buffer = buffer[-1024:]
                    
                    if '\n' in buffer:
                        lines = buffer.split('\n')
                        buffer = lines.pop()
                        
                        for line in reversed(lines):
                            parts = line.split(',')
                            
                            if '$GPGGA' in line and len(parts) > 9:
                                if parts[2] and parts[4]:
                                    lat = convert_to_degrees(parts[2], parts[3])
                                    lon = convert_to_degrees(parts[4], parts[5])
                                    alt = float(parts[9]) if parts[9] else 0.0
                                    _cached_lon, _cached_lat, _cached_alt = lon, lat, alt
                                    _last_read_time = current_time
                                    gps_uart.deinit()
                                    return lon, lat, alt
                            
                            elif '$GPRMC' in line and len(parts) > 7:
                                if parts[2] == 'A' and parts[3] and parts[5]:
                                    lat = convert_to_degrees(parts[3], parts[4])
                                    lon = convert_to_degrees(parts[5], parts[6])
                                    _cached_lon, _cached_lat, _cached_alt = lon, lat, 0.0
                                    _last_read_time = current_time
                                    gps_uart.deinit()
                                    return lon, lat, 0.0
                except:
                    pass
            
            time.sleep(0.05)
        
        gps_uart.deinit()
        return _cached_lon, _cached_lat, _cached_alt  # 超时返回缓存值
        
    except Exception as e:
        print(f"[GPS] 读取异常: {e}")
        return _cached_lon, _cached_lat, _cached_alt
