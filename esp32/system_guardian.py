# --- START OF FILE system_guardian.py ---
import machine
import gc
import time

class Guardian:
    """系统守护者 - 看门狗、内存管理、运行监控"""
    
    def __init__(self, timeout_ms=60000):
        self.start_time = time.time()
        self.feed_count = 0
        self.gc_count = 0
        self.last_gc_time = 0
        self.gc_interval = 60  # 每60秒执行一次GC
        
        # 启动硬件看门狗
        self.wdt = machine.WDT(timeout=timeout_ms)
        print(f"[守护者] 硬件看门狗已启动，超时: {timeout_ms}ms")
    
    def feed(self):
        """喂狗，重置计时器"""
        self.wdt.feed()
        self.feed_count += 1
    
    def collect_garbage(self):
        """定期回收内存"""
        current_time = time.time()
        
        # 限制GC频率
        if current_time - self.last_gc_time < self.gc_interval:
            return
        
        before = gc.mem_free()
        gc.collect()
        after = gc.mem_free()
        
        self.gc_count += 1
        self.last_gc_time = current_time
        
        # 仅在内存紧张时打印警告
        if after < 20000:
            print(f"[守护者] 内存警告: {after} 字节可用")
    
    def force_gc(self):
        """强制立即回收内存"""
        gc.collect()
        self.gc_count += 1
        self.last_gc_time = time.time()
    
    def get_uptime(self):
        """获取运行时间（秒）"""
        return time.time() - self.start_time
    
    def get_memory_info(self):
        """获取内存信息"""
        gc.collect()
        return {
            "free": gc.mem_free(),
            "allocated": gc.mem_alloc()
        }
    
    def get_status(self):
        """获取守护者状态"""
        return {
            "uptime_seconds": self.get_uptime(),
            "feed_count": self.feed_count,
            "gc_count": self.gc_count,
            "free_memory": gc.mem_free()
        }
    
    def print_status(self):
        """打印状态信息"""
        uptime = self.get_uptime()
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        
        print(f"[守护者] 运行: {int(hours)}h{int(minutes)}m{int(seconds)}s | "
              f"喂狗: {self.feed_count}次 | "
              f"GC: {self.gc_count}次 | "
              f"空闲内存: {gc.mem_free()}字节")


def get_timestamp():
    """获取格式化时间戳"""
    t = time.localtime()
    return f"{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
