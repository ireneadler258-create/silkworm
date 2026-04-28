import network
import time

class WiFiManager:
    """WiFi连接管理器 - 支持自动重连和状态监控"""
    
    def __init__(self, ssid, password, timeout=20, retry_interval=1):
        self.ssid = ssid
        self.password = password
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.wlan = network.WLAN(network.STA_IF)
        self.last_check_time = 0
        self.check_interval = 5  # 每5秒检查一次连接状态
        
    def connect(self):
        """初始连接WiFi"""
        self.wlan.active(True)
        
        if self.wlan.isconnected():
            print("[WiFi] 已连接:", self.wlan.ifconfig())
            return True
            
        print(f"[WiFi] 正在连接 {self.ssid}...")
        self.wlan.connect(self.ssid, self.password)
        
        for i in range(self.timeout):
            if self.wlan.isconnected():
                print("[WiFi] 连接成功:", self.wlan.ifconfig())
                return True
            time.sleep(self.retry_interval)
            print(".", end="")
        
        print("\n[WiFi] 连接失败!")
        return False
    
    def is_connected(self):
        """检查WiFi是否连接"""
        return self.wlan.isconnected()
    
    def ensure_connected(self):
        """确保WiFi连接，如果断开则自动重连"""
        current_time = time.time()
        
        # 限制检查频率，避免过于频繁
        if current_time - self.last_check_time < self.check_interval:
            return self.wlan.isconnected()
        
        self.last_check_time = current_time
        
        if self.wlan.isconnected():
            return True
        
        print("[WiFi] 检测到断连，尝试重连...")
        return self._reconnect()
    
    def _reconnect(self):
        """内部重连方法"""
        try:
            # 先断开再重连，清理可能的残留状态
            self.wlan.disconnect()
            time.sleep(1)
            
            self.wlan.connect(self.ssid, self.password)
            
            for i in range(self.timeout):
                if self.wlan.isconnected():
                    print("[WiFi] 重连成功:", self.wlan.ifconfig())
                    return True
                time.sleep(self.retry_interval)
            
            print("[WiFi] 重连失败，将在下次循环重试")
            return False
            
        except Exception as e:
            print(f"[WiFi] 重连异常: {e}")
            return False
    
    def get_status(self):
        """获取WiFi状态信息"""
        if not self.wlan.isconnected():
            return {"connected": False, "ip": None}
        
        ifconfig = self.wlan.ifconfig()
        return {
            "connected": True,
            "ip": ifconfig[0],
            "subnet": ifconfig[1],
            "gateway": ifconfig[2],
            "dns": ifconfig[3]
        }
    
    def disconnect(self):
        """断开WiFi连接"""
        if self.wlan.isconnected():
            self.wlan.disconnect()
        self.wlan.active(False)


# 兼容旧接口
def connect_wifi(ssid, password):
    """旧版连接函数，返回WiFiManager实例"""
    manager = WiFiManager(ssid, password)
    manager.connect()
    return manager