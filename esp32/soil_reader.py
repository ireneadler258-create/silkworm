# --- START OF FILE soil_reader.py ---
import machine

def read_soil(ad_pin=5):
    """
    读取土壤湿度（单次采样，快速）
    :return: 湿度百分比 (0.0-100.0), 读取失败返回None
    """
    try:
        adc = machine.ADC(machine.Pin(ad_pin))
        adc.atten(machine.ADC.ATTN_11DB)
        
        # 单次读取
        adc_val = adc.read()
        
        # 校准参数
        dry_value = 4095
        wet_value = 1500
        
        # 计算百分比
        percentage = (dry_value - adc_val) / (dry_value - wet_value) * 100
        
        # 限制在 0-100 之间
        if percentage > 100: percentage = 100.0
        if percentage < 0: percentage = 0.0
        
        return round(float(percentage), 2)
        
    except Exception as e:
        print("[土壤] 读取异常:", e)
        return None
