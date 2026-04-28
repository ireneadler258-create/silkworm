# --- START OF FILE bh1750_reader.py ---
import machine
import time

# 缓存I2C地址
_cached_addr = None

def read_bh1750(sda_pin=8, scl_pin=9):
    global _cached_addr
    
    try:
        i2c = machine.I2C(0, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=100000)
        
        # 如果还没有缓存地址，扫描一次
        if _cached_addr is None:
            devices = i2c.scan()
            if 0x23 in devices:
                _cached_addr = 0x23
            elif 0x5c in devices:
                _cached_addr = 0x5c
            else:
                print("[BH1750] 未发现传感器")
                return None
        
        i2c.writeto(_cached_addr, b'\x01')  # Power on
        i2c.writeto(_cached_addr, b'\x10')  # High Res Mode
        time.sleep(0.2)
        data = i2c.readfrom(_cached_addr, 2)
        lux = (data[0] << 8 | data[1]) / 1.2
        return round(lux, 2)
        
    except Exception as e:
        print("[BH1750] 读取异常:", e)
        return None
