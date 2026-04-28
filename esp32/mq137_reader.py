# --- START OF FILE mq137_reader.py ---
import machine
import math

def read_mq137(ad_pin=6):
    """读取MQ137氨气传感器（单次采样，快速）"""
    try:
        adc = machine.ADC(machine.Pin(ad_pin))
        adc.atten(machine.ADC.ATTN_11DB)
        
        # 单次读取
        adc_val = adc.read()
        v_rl = (adc_val * 3.3) / 4095
        
        term = (314.01 * v_rl / 23.5) - (7.12 * v_rl)
        if term <= 0:
            ammonia_ppm = 0.0
        else:
            ammonia_ppm = math.pow(term, 1 / 0.8394)
        
        return round(ammonia_ppm, 2)
        
    except Exception as e:
        print("[MQ137] 读取异常:", e)
        return None
