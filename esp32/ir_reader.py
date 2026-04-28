# --- START OF FILE ir_reader.py ---
from machine import Pin

# 修改点：将引脚对象作为全局/静态变量，方便主程序绑定中断
def init_ir(pin_num=1):
    # 使用 PULL_DOWN 确保无信号时为稳定低电平
    return Pin(pin_num, Pin.IN, Pin.PULL_DOWN)

def read_ir(pin_obj):
    # 1 代表检测到人体/障碍物，0 代表正常
    return pin_obj.value()