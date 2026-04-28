from machine import Pin

class Actuator:
    def __init__(self, pin_num, name="设备", active_high=False):
        # ⚠️ 注意：默认值设为 False，适配低电平触发模块
        self.pin = Pin(pin_num, Pin.OUT)
        self.name = name
        self.active_high = active_high
        self.off() # 初始化为关闭

    def on(self):
        # 如果是低电平触发(active_high=False)，开启时送 0
        val = 1 if self.active_high else 0
        self.pin.value(val)

    def off(self):
        # 如果是低电平触发(active_high=False)，关闭时送 1
        val = 0 if self.active_high else 1
        self.pin.value(val)

    def get_status(self):
        # 返回逻辑状态：1代表正在工作，0代表停止
        curr = self.pin.value()
        return curr if self.active_high else (1 - curr)