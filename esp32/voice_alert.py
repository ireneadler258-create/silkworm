# --- START OF FILE voice_alert.py ---
"""
语音报警模块
- 通过UART发送指令给ASR Pro语音模块
- 读取brain.th获取实时阈值（APP改阈值后自动同步）
- 带冷却机制防止重复播报
"""

from machine import UART
import time


class VoiceAlert:
    """语音报警控制器"""
    
    # 指令定义
    CMD_IR = 0x01          # 有人靠近
    CMD_TEMP_HIGH = 0x02   # 温度过高
    CMD_TEMP_LOW = 0x03    # 温度过低
    CMD_LUX_LOW = 0x04     # 光照不足
    CMD_HUM_HIGH = 0x05    # 湿度过高
    CMD_HUM_LOW = 0x06     # 湿度过低
    
    def __init__(self, brain, uart_id=1, tx_pin=12, rx_pin=19, baudrate=9600):
        """
        初始化语音模块
        
        Args:
            brain: SmartController对象，用于读取实时阈值
            uart_id: UART编号（与CO2/GPS共用UART1控制器）
            tx_pin: TX引脚（默认GPIO 12）
            rx_pin: RX引脚（默认GPIO 19）
            baudrate: 波特率
        """
        self.brain = brain
        self.uart_id = uart_id
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.baudrate = baudrate
        
        # 冷却时间配置（秒）
        self.cooldown_config = {
            self.CMD_IR: 5,           # 有人靠近：5秒
            self.CMD_TEMP_HIGH: 30,   # 温度过高：30秒
            self.CMD_TEMP_LOW: 30,    # 温度过低：30秒
            self.CMD_LUX_LOW: 60,     # 光照不足：60秒
            self.CMD_HUM_HIGH: 30,    # 湿度过高：30秒
            self.CMD_HUM_LOW: 30,     # 湿度过低：30秒
        }
        
        # 记录每种报警的最后触发时间
        self.last_alert_time = {
            self.CMD_IR: 0,
            self.CMD_TEMP_HIGH: 0,
            self.CMD_TEMP_LOW: 0,
            self.CMD_LUX_LOW: 0,
            self.CMD_HUM_HIGH: 0,
            self.CMD_HUM_LOW: 0,
        }
        
        print("[语音] 模块初始化完成")
    
    def _send_command(self, cmd):
        """
        发送指令给ASR Pro
        使用临时UART实例，避免与CO2/GPS长期冲突
        """
        try:
            # 创建临时UART对象
            uart = UART(self.uart_id, 
                       baudrate=self.baudrate,
                       tx=self.tx_pin, 
                       rx=self.rx_pin,
                       timeout=10)
            
            # 等待UART稳定
            time.sleep_ms(100)
            
            # 发送单字节指令
            uart.write(bytes([cmd]))
            print(f"[语音] 发送指令: 0x{cmd:02X}")
            
            # 等待ASR Pro接收处理
            time.sleep_ms(200)
            
            # 释放UART（让给CO2/GPS使用）
            uart.deinit()
            
            # 销毁后再等待，确保UART1完全释放
            time.sleep_ms(100)
            
            return True
            
        except Exception as e:
            print(f"[语音] 发送失败: {e}")
            return False
    
    def _can_alert(self, cmd):
        """检查是否可以触发播报（冷却检测）"""
        current_time = time.time()
        last_time = self.last_alert_time.get(cmd, 0)
        cooldown = self.cooldown_config.get(cmd, 30)
        
        if current_time - last_time >= cooldown:
            return True
        return False
    
    def _record_alert(self, cmd):
        """记录报警时间"""
        self.last_alert_time[cmd] = time.time()
    
    def check_and_alert(self, temp, hum, lux, ir):
        """
        检查传感器状态并触发语音播报
        阈值从brain.th实时读取，APP改了阈值这里自动同步
        
        Args:
            temp: 温度值
            hum: 湿度值
            lux: 光照值
            ir: 红外传感器值（1=有人）
        """
        # 获取实时阈值
        th = self.brain.th
        
        # 1. 检测有人靠近
        if ir == 1 and self._can_alert(self.CMD_IR):
            self._send_command(self.CMD_IR)
            self._record_alert(self.CMD_IR)
            return  # 优先播报，不检查其他条件
        
        # 2. 温度检测
        if temp is not None:
            if temp > th['TEMP_HIGH'] and self._can_alert(self.CMD_TEMP_HIGH):
                self._send_command(self.CMD_TEMP_HIGH)
                self._record_alert(self.CMD_TEMP_HIGH)
            elif temp < th['TEMP_LOW'] and self._can_alert(self.CMD_TEMP_LOW):
                self._send_command(self.CMD_TEMP_LOW)
                self._record_alert(self.CMD_TEMP_LOW)
        
        # 3. 光照检测
        if lux is not None:
            if lux < th['LUX_LOW'] and self._can_alert(self.CMD_LUX_LOW):
                self._send_command(self.CMD_LUX_LOW)
                self._record_alert(self.CMD_LUX_LOW)
        
        # 4. 湿度检测
        if hum is not None:
            if hum > th['HUM_HIGH'] and self._can_alert(self.CMD_HUM_HIGH):
                self._send_command(self.CMD_HUM_HIGH)
                self._record_alert(self.CMD_HUM_HIGH)
            elif hum < th['HUM_LOW'] and self._can_alert(self.CMD_HUM_LOW):
                self._send_command(self.CMD_HUM_LOW)
                self._record_alert(self.CMD_HUM_LOW)
    
    def get_status(self):
        """获取语音模块状态"""
        current_time = time.time()
        status = {}
        for cmd, cooldown in self.cooldown_config.items():
            last_time = self.last_alert_time.get(cmd, 0)
            remaining = max(0, cooldown - (current_time - last_time))
            status[f"0x{cmd:02X}_remaining"] = remaining
        return status
