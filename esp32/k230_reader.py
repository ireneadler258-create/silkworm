from machine import UART
import time

# 独立占用 UART 2，引脚 14, 13
# timeout=50ms，快速返回避免卡住
k230_uart = UART(2, baudrate=115200, tx=14, rx=13, timeout=50)

last_ai_data = {"total": 0, "healthy": 0, "sick": 0, "sleep": 0, "sick_image_url": ""}

def read_k230():
    global last_ai_data
    
    # 检查是否有足够数据（至少要有 "DATA:T1,H1,U0,S0\n" 约15字节）
    available = k230_uart.any()
    if available < 10:  # 数据太少，可能是噪声，直接返回
        return last_ai_data
    
    try:
        # 一次性读完缓冲区
        all_data = k230_uart.read()
        if not all_data:
            return last_ai_data
        
        # 尝试解码
        text = all_data.decode('utf-8', 'ignore')
        if 'DATA:' not in text:
            # 没有有效数据，可能是噪声
            return last_ai_data
        
        # 按行分割，找最后一个有效的DATA行
        lines = text.strip().split('\n')
        
        for line in reversed(lines):  # 从后往前找，取最新数据
            line = line.strip()
            if line.startswith("DATA:"):
                # 分离数据部分和URL部分
                # 格式1: DATA:T50,H45,U2,S3
                # 格式2: DATA:T50,H45,U2,S3|URL:https://i.ibb.co/xxx.jpg
                parts = line.split("|URL:")
                data_part = parts[0]
                url_part = parts[1] if len(parts) > 1 else ""
                
                # 解析数据字段
                fields = data_part[5:].split(",")
                new_data = {}
                for p in fields:
                    if len(p) >= 2:
                        tag, val = p[0], int(p[1:])
                        if tag == 'T': new_data["total"] = val
                        if tag == 'H': new_data["healthy"] = val
                        if tag == 'U': new_data["sick"] = val
                        if tag == 'S': new_data["sleep"] = val
                
                if len(new_data) == 4:  # 确保4个字段都解析成功
                    new_data["sick_image_url"] = url_part
                    last_ai_data.update(new_data)
                    if url_part:
                        print(f"[K230] 病蚕图片: {url_part}")
                    print(f"[K230] 更新: total={new_data['total']}, healthy={new_data['healthy']}, sick={new_data['sick']}, sleep={new_data['sleep']}")
                    break
        
    except Exception as e:
        print(f"[K230] 解析异常: {e}")
    
    return last_ai_data
