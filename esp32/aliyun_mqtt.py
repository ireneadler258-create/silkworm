# --- START OF FILE aliyun_mqtt.py ---
from umqtt.simple import MQTTClient
import hashlib
import ubinascii
import time
import ujson

def hmac_sha1(key, msg):
    blocksize = 64
    if len(key) > blocksize:
        key = hashlib.sha1(key).digest()
    key = key + b'\x00' * (blocksize - len(key))
    o_key_pad = bytes([b ^ 0x5c for b in key])
    i_key_pad = bytes([b ^ 0x36 for b in key])
    inner = hashlib.sha1(i_key_pad + msg).digest()
    return ubinascii.hexlify(hashlib.sha1(o_key_pad + inner).digest()).decode()


class MQTTManager:
    """MQTT连接管理器 - 支持自动重连和状态监控"""
    
    def __init__(self, product_key, device_name, device_secret, callback=None):
        self.product_key = product_key
        self.device_name = device_name
        self.device_secret = device_secret
        self.callback = callback
        self.client = None
        self.connected = False
        self.connect_time = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_backoff = 1  # 重连退避基数（秒）
        
        # 主题定义
        self.topic_property_post = f'/sys/{product_key}/{device_name}/thing/event/property/post'
        self.topic_property_set = f'/sys/{product_key}/{device_name}/thing/service/property/set'
        self.topic_custom = f'/{product_key}/{device_name}/user/get'
    
    def connect(self):
        """连接到阿里云MQTT"""
        try:
            # 构建连接参数
            mqtt_server = f'{self.product_key}.iot-as-mqtt.cn-shanghai.aliyuncs.com'
            timestamp = str(int(time.time()))
            client_id = f'{self.device_name}|securemode=3,signmethod=hmacsha1,timestamp={timestamp}|'
            username = f'{self.device_name}&{self.product_key}'
            msg = f'clientId{self.device_name}deviceName{self.device_name}productKey{self.product_key}timestamp{timestamp}'
            password = hmac_sha1(self.device_secret.encode(), msg.encode())
            
            # 创建客户端
            self.client = MQTTClient(
                client_id, 
                mqtt_server, 
                user=username, 
                password=password, 
                port=1883, 
                keepalive=60
            )
            
            # 绑定回调
            if self.callback:
                self.client.set_callback(self.callback)
            
            # 连接
            self.client.connect()
            
            # 订阅主题
            self.client.subscribe(self.topic_property_set)
            self.client.subscribe(self.topic_custom)
            
            self.connected = True
            self.connect_time = time.time()
            self.reconnect_attempts = 0  # 重置重连计数
            
            print(f"[MQTT] 已连接并订阅控制主题")
            return True
            
        except Exception as e:
            print(f"[MQTT] 连接失败: {e}")
            self.connected = False
            return False
    
    def reconnect(self, wifi_connected=True):
        """重连MQTT"""
        if not wifi_connected:
            print("[MQTT] WiFi未连接，跳过MQTT重连")
            return False
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"[MQTT] 已达最大重连次数({self.max_reconnect_attempts})，等待下次机会")
            self.reconnect_attempts = 0  # 重置，给下次机会
            return False
        
        # 指数退避
        wait_time = self.reconnect_backoff * (2 ** self.reconnect_attempts)
        print(f"[MQTT] 尝试重连 (第{self.reconnect_attempts + 1}次，等待{wait_time}秒)...")
        time.sleep(wait_time)
        
        self.reconnect_attempts += 1
        
        try:
            # 先清理旧连接
            self.disconnect()
        except:
            pass
        
        return self.connect()
    
    def is_connected(self):
        """检查MQTT连接状态"""
        if not self.connected or self.client is None:
            return False
        
        # umqtt.simple 没有直接的连接状态检查
        # 通过检查是否能成功ping（通过check_msg间接判断）
        return self.connected
    
    def check_msg(self):
        """检查消息，如果连接断开会抛异常"""
        if not self.connected or self.client is None:
            raise Exception("MQTT未连接")
        
        try:
            self.client.check_msg()
        except Exception as e:
            self.connected = False
            raise e
    
    def publish(self, data_dict):
        """发布数据，带自动重连"""
        if not self.connected or self.client is None:
            print("[MQTT] 未连接，无法发布数据")
            return False
        
        params = {k: v for k, v in data_dict.items() if v is not None}
        if not params:
            return True
        
        payload_dict = {"params": params, "method": "thing.event.property.post"}
        
        try:
            payload = ujson.dumps(payload_dict)
            self.client.publish(self.topic_property_post, payload)
            # print(f"[MQTT] 发布成功: {list(params.keys())}")
            return True
            
        except Exception as e:
            print(f"[MQTT] 发布失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开MQTT连接"""
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
        self.connected = False
        print("[MQTT] 已断开连接")
    
    def get_status(self):
        """获取MQTT状态信息"""
        return {
            "connected": self.connected,
            "uptime": time.time() - self.connect_time if self.connected else 0,
            "server": f"{self.product_key}.iot-as-mqtt.cn-shanghai.aliyuncs.com"
        }


# 兼容旧接口
def connect_mqtt(product_key, device_name, device_secret, callback=None):
    """旧版连接函数，返回MQTTManager实例"""
    manager = MQTTManager(product_key, device_name, device_secret, callback)
    manager.connect()
    return manager


def publish_data(client, product_key, device_name, data_dict):
    """旧版发布函数，兼容新旧接口"""
    # 如果传入的是MQTTManager实例
    if isinstance(client, MQTTManager):
        return client.publish(data_dict)
    
    # 兼容旧的直接MQTTClient调用
    params = {k: v for k, v in data_dict.items() if v is not None}
    if not params:
        return
    payload_dict = {"params": params, "method": "thing.event.property.post"}
    try:
        payload = ujson.dumps(payload_dict)
        client.publish(f'/sys/{product_key}/{device_name}/thing/event/property/post', payload)
        print(f"[MQTT] 发布成功: {list(params.keys())}")
        return True
    except Exception as e:
        print(f"[MQTT] 发布失败: {e}")
        return False
