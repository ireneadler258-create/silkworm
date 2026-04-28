# --- START OF FILE smart_control.py ---

class SmartController:
    def __init__(self, fan, heater, atomizer, alert_led, l_r, l_g, l_b, thresholds):
        # 初始化执行器对象
        self.fan = fan
        self.heater = heater
        self.atomizer = atomizer
        self.alert_led = alert_led
        self.l_r = l_r
        self.l_g = l_g
        self.l_b = l_b
        
        # 阈值配置
        self.th = thresholds
        
        # 核心状态：ManualMode (布尔型)
        # False: 自动模式 (传感器控制)
        # True : 手动模式 (用户控制)
        self.manual_mode = 0 
        self.light_status = 0

    def handle_command(self, prop, value):
        """
        统一处理来自云端的指令（包括开关和阈值）
        """
        # 1. 模式切换
        if prop == "ManualMode":
            self.manual_mode = 1 if value else 0
            print(f"[大脑] 模式切换: {self.manual_mode}")
            return

        # 2. 阈值调整 (核心新增)
        # 对应阿里云标识符：TempHighTh, TempLowTh, HumLowTh, HumHighTh，LuxHighTh, LuxLowTh
        threshold_map = {
            "TempHighTh": "TEMP_HIGH",
            "TempLowTh": "TEMP_LOW",
            "HumLowTh": "HUM_LOW",
            "HumHighTh": "HUM_HIGH",
            "LuxHighTh": "LUX_HIGH",
            "LuxLowTh": "LUX_LOW"
        }
        
        if prop in threshold_map:
            th_key = threshold_map[prop]
            self.th[th_key] = float(value) # 确保是浮点数
            print(f"[大脑] 阈值更新: {th_key} -> {value}")
            return

        # 3. 手动控制执行器 (仅在 manual_mode 为 1 时有效)
        if self.manual_mode == 1:
            if prop == "fanStatus": self.fan.on() if value else self.fan.off()
            elif prop == "heaterStatus": self.heater.on() if value else self.heater.off()
            elif prop == "atomizerStatus": self.atomizer.on() if value else self.atomizer.off()
            elif prop == "IRStatus": self.alert_led.on() if value else self.alert_led.off()
            elif prop == "lightStatus":
                self.light_status = 1 if value else 0
                if value: self.l_r.on(); self.l_g.on(); self.l_b.on()
                else: self.l_r.off(); self.l_g.off(); self.l_b.off()
            print(f"[控制] 手动设置: {prop} -> {value}")

    def update(self, sensors, ai_data):
        # 如果是手动模式，跳过逻辑计算
        if self.manual_mode == 1:
            return {'temp_msg': "手动", 'hum_msg': "手动", 'light_msg': "手动", 'alert_msg': "手动"}

        results = {}
        # 温度控制 (使用动态阈值)
        temp = sensors.get('temp')
        if temp is not None:
            if temp > self.th['TEMP_HIGH']:
                self.fan.on(); self.heater.off(); results['temp_msg'] = "排风"
            elif temp < self.th['TEMP_LOW']:
                self.fan.off(); self.heater.on(); results['temp_msg'] = "加热"
            else:
                self.fan.off(); self.heater.off(); results['temp_msg'] = "正常"
        
        # 湿度逻辑 (使用动态阈值)
        hum = sensors.get('hum')
        if hum is not None:
            if hum < self.th['HUM_LOW']:
                # 低于最低值，开启加湿
                self.atomizer.on()
                results['hum_msg'] = "加湿中"
            elif hum > self.th['HUM_HIGH']:
                # 高于最高值，强制停止
                self.atomizer.off()
                results['hum_msg'] = "过湿停止"
            else:
                # 处于中间地带，维持关闭状态（或根据需要设计回差逻辑）
                self.atomizer.off()
                results['hum_msg'] = "正常"
                
        # 补光逻辑 (使用动态阈值)
        lux = sensors.get('lux')
        if lux is not None:
            if self.light_status == 0 and lux < self.th['LUX_LOW']:
                self.l_r.on(); self.l_g.on(); self.l_b.on(); self.light_status = 1
            elif self.light_status == 1 and lux > self.th['LUX_HIGH']:
                self.l_r.off(); self.l_g.off(); self.l_b.off(); self.light_status = 0
            results['light_msg'] = "开灯" if self.light_status else "关灯"

        # 报警控制
        if sensors.get('ir') == 1 or ai_data.get('sick', 0) > 0:
            self.alert_led.on(); results['alert_msg'] = "报警"
        else:
            self.alert_led.off(); results['alert_msg'] = "安全"
        return results

    def get_all_status(self):
        """
        同步状态，包括所有当前阈值
        """
        status = {
            "ManualMode": 1 if self.manual_mode else 0,
            "fanStatus": 1 if self.fan.get_status() else 0,
            "heaterStatus": 1 if self.heater.get_status() else 0,
            "atomizerStatus": 1 if self.atomizer.get_status() else 0,
            "lightStatus": 1 if self.light_status else 0,
            "IRStatus": 1 if self.alert_led.get_status() else 0,
            # 将当前内存中的阈值上报给云端，供 APP 显示
            "TempHighTh": self.th['TEMP_HIGH'],
            "TempLowTh": self.th['TEMP_LOW'],
            "HumLowTh": self.th['HUM_LOW'],
            "HumHighTh": self.th['HUM_HIGH'],
            "LuxHighTh": self.th['LUX_HIGH'],
            "LuxLowTh": self.th['LUX_LOW']
        }
        return status