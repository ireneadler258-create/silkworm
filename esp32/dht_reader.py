import machine
import dht

# 修改 dht_reader.py 
def read_dht22(pin_number=4):
    sensor = dht.DHT22(machine.Pin(pin_number))
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        # ✅ 使用 round(x, 1) 保留一位小数
        return round(temp, 1), round(hum, 1) 
    except Exception as e:
        print("DHT22读取失败:", e)
        return None, None
