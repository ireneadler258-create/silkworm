# --- START OF FILE co2_reader.py ---
from machine import UART
import time

# 缓存CO2值和读取时间
_cached_co2 = None
_last_read_time = 0
_read_interval = 10  # 每10秒读取一次

def read_co2(guardian_obj=None, mqtt_client=None, force=False):
    """
    读取CO2值（带缓存）
    
    Args:
        guardian_obj: 看门狗对象
        mqtt_client: MQTT客户端
        force: 强制读取（忽略缓存）
    """
    global _cached_co2, _last_read_time
    
    current_time = time.time()
    
    # 如果不需要强制读取，且缓存未过期，直接返回缓存
    if not force and (current_time - _last_read_time) < _read_interval:
        return _cached_co2
    
    # 执行读取
    try:
        uart = UART(1, baudrate=9600, tx=15, rx=16, timeout=10)
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < 1500:
            if guardian_obj: 
                guardian_obj.feed()
            if mqtt_client:
                try:
                    mqtt_client.check_msg()
                except:
                    pass
            
            if uart.any():
                raw = uart.read()
                index = raw.rfind(b'\x2c')
                if index != -1 and len(raw) >= index + 6:
                    packet = raw[index : index + 6]
                    if (sum(packet[0:5]) & 0xFF) == packet[5]:
                        ppm = (packet[1] << 8) | packet[2]
                        _cached_co2 = ppm
                        _last_read_time = current_time
                        uart.deinit()
                        return ppm
            time.sleep(0.1)
        
        uart.deinit()
        return _cached_co2  # 超时返回缓存值
        
    except Exception as e:
        print(f"[CO2] 读取异常: {e}")
        return _cached_co2
