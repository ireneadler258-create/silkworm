# --- K230 病蚕识别 + 稳定上传 + 串口数据同步 (最终稳定版) ---
from libs.PipeLine import PipeLine
from libs.AIBase import AIBase
from libs.AI2D import Ai2d
from libs.Utils import *
import os, sys, gc, math, time
import nncase_runtime as nn
import ulab.numpy as np
from machine import UART
import network
import requests
import ujson
import ubinascii

from media.sensor import *
from media.display import *
from media.media import *

# ============ 1. 配置 (请替换为实际值) ============
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"
IMG_BB_KEY = "YOUR_IMGBB_API_KEY"
UPLOAD_COOLDOWN = 60 # 上传冷却时间(秒)

# 初始化串口 (TX=3, RX=4)
uart = UART(UART.UART1, baudrate=115200, tx=3, rx=4)

# ============ 2. WiFi连接 ============
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected(): return True
    print("[WiFi] Connecting...")
    wlan.connect(WIFI_SSID, WIFI_PASS)
    for i in range(15):
        if wlan.isconnected():
            print("[WiFi] Connected, IP:", wlan.ifconfig()[0])
            return True
        time.sleep(1)
    return False

wifi_ok = connect_wifi()

# ============ 3. ImgBB 上传函数 (内存优化版) ============
def upload_to_imgbb(img_path):
    gc.collect() # 预先清理内存
    try:
        # 1. 编码图片 (尽量减少变量生存期)
        with open(img_path, 'rb') as f:
            img_data = f.read()

        # 立即将图片转为 Base64 字符串
        img_b64 = ubinascii.b2a_base64(img_data).decode().strip()
        del img_data # 释放二进制数据
        gc.collect()

        # 2. 准备请求负载 (使用字符串替换处理特殊字符)
        api_url = "https://api.imgbb.com/1/upload?key=" + IMG_BB_KEY
        payload = "image=" + img_b64.replace('+', '%2B').replace('=', '%3D')
        del img_b64
        gc.collect()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "close"
        }

        print("[ImgBB] Starting Upload...")
        # 3. 发送 POST 请求
        resp = requests.post(api_url, data=payload, headers=headers, timeout=30)

        # 4. 解析结果
        if resp.status_code == 200:
            res_json = resp.json()
            resp.close()
            url = res_json["data"]["url"]
            return url
        else:
            print("[ImgBB] Server Error Code:", resp.status_code)
            resp.close()
            return None

    except Exception as e:
        print("[ImgBB] Runtime Error:", e)
        return None
    finally:
        gc.collect()

# ============ 4. AI 逻辑类 ============
class SilkwormMonitor(AIBase):
    def __init__(self, kmodel_path, labels, model_input_size, rgb888p_size=[1920, 1080]):
        super().__init__(kmodel_path, model_input_size, rgb888p_size)
        self.labels = labels
        self.tracker_db = {}
        self.next_id = 0
        self.sleep_limit = 50 # 50帧不动判定为睡眠
        self.last_send_time = time.ticks_ms()
        self.last_upload_time = 0
        self.current_url = "" # 待发送的 URL

        self.ai2d = Ai2d(0)
        self.ai2d.set_ai2d_dtype(nn.ai2d_format.NCHW_FMT, nn.ai2d_format.NCHW_FMT, np.uint8, np.uint8)

    def config_preprocess(self, input_image_size=None):
        ai2d_input_size = input_image_size if input_image_size else [1920, 1080]
        self.top, self.bottom, self.left, self.right, self.scale = letterbox_pad_param(ai2d_input_size, [640,640])
        self.ai2d.pad([0, 0, 0, 0, self.top, self.bottom, self.left, self.right], 0, [114, 114, 114])
        self.ai2d.resize(nn.interp_method.tf_bilinear, nn.interp_mode.half_pixel)
        self.ai2d.build([1, 3, 1080, 1920], [1, 3, 640, 640])

    def postprocess(self, results):
        data = results[0][0].transpose()
        valid_boxes = []
        for i in range(data.shape[0]):
            row = data[i]
            score = max(row[4], row[5])
            if score > 0.45:
                cls_id = 0 if row[4] > row[5] else 1
                cx, cy, w, h = row[0], row[1], row[2], row[3]
                x1 = int((cx - w/2 - self.left) / self.scale)
                y1 = int((cy - h/2 - self.top) / self.scale)
                valid_boxes.append([x1, y1, int(w/self.scale), int(h/self.scale), score, cls_id])
        return self.simple_nms(valid_boxes, 0.4)

    def process_logic(self, pl, sensor, dets):
        pl.osd_img.clear()
        h_cnt, u_cnt, s_cnt = 0, 0, 0
        current_time = time.time()

        if dets:
            for x, y, w, h, score, cls_id in dets:
                cx, cy = x + w//2, y + h//2
                if cls_id == 0: h_cnt += 1
                else: u_cnt += 1

                # 简单目标追踪
                matched_id = None
                for tid, obj in self.tracker_db.items():
                    if math.sqrt((cx-obj['x'])**2 + (cy-obj['y'])**2) < 120:
                        matched_id = tid; break

                if matched_id is not None:
                    obj = self.tracker_db[matched_id]
                    move = math.sqrt((cx-obj['x'])**2 + (cy-obj['y'])**2)
                    obj['sc'] = obj['sc'] + 1 if move < 10 else 0
                    obj['x'], obj['y'], obj['age'] = cx, cy, 0
                    if obj['sc'] > self.sleep_limit: obj['is_s'] = True
                else:
                    self.tracker_db[self.next_id] = {'x':cx, 'y':cy, 'sc':0, 'is_s':False, 'age':0}
                    matched_id = self.next_id
                    self.next_id += 1

                is_s = self.tracker_db[matched_id]['is_s']
                if is_s: s_cnt += 1

                # 绘制
                color = (255,255,0) if is_s else ((0,255,0) if cls_id==0 else (255,0,0))
                pl.osd_img.draw_rectangle(x, y, w, h, color=color, thickness=4)
                tag = "Sleep" if is_s else self.labels[cls_id]
                pl.osd_img.draw_string_advanced(x, y-40, 32, "ID%d:%s"%(matched_id, tag), color=color)

        # --- 抓拍上传逻辑 ---
        if u_cnt > 0 and wifi_ok and (current_time - self.last_upload_time > UPLOAD_COOLDOWN):
            self.last_upload_time = current_time # 立即更新冷却
            print("[Action] Sick silkworm detected! Capturing...")

            img_path = "/sdcard/alert.jpg"
            # 使用通道 1 (320x240) 拍照，节省网络缓冲区内存
            sensor.snapshot(chn=1).save(img_path)

            new_url = upload_to_imgbb(img_path)
            if new_url:
                self.current_url = new_url # 暂存 URL 等待下个串口周期发送

        # --- 串口数据发送逻辑 (1秒/次) ---
        if time.ticks_diff(time.ticks_ms(), self.last_send_time) > 1000:
            total = h_cnt + u_cnt
            msg = "DATA:T%d,H%d,U%d,S%d" % (total, h_cnt, u_cnt, s_cnt)

            # 如果有待发送的 URL
            if self.current_url:
                msg += "|URL:" + self.current_url
                self.current_url = "" # 发送后清空，防止重复发送长字符串

            uart.write(msg + "\n")
            print("UART Out:", msg)
            self.last_send_time = time.ticks_ms()

        # 顶部状态栏
        pl.osd_img.draw_rectangle(0, 0, 1920, 80, color=(0,0,0), fill=True)
        pl.osd_img.draw_string_advanced(40, 10, 50, "TOTAL:%d HEALTHY:%d SICK:%d SLEEP:%d"%(h_cnt+u_cnt, h_cnt, u_cnt, s_cnt), color=(255,255,255))

    def simple_nms(self, boxes, threshold):
        if not boxes: return []
        boxes.sort(key=lambda x: x[4], reverse=True)
        keep = []
        while boxes:
            curr = boxes.pop(0)
            keep.append(curr)
            boxes = [b for b in boxes if self.iou(curr, b) < threshold]
        return keep

    def iou(self, b1, b2):
        x1, y1, w1, h1 = b1[0], b1[1], b1[2], b1[3]
        x2, y2, w2, h2 = b2[0], b2[1], b2[2], b2[3]
        inter_w = min(x1+w1, x2+w2) - max(x1,x2)
        inter_h = min(y1+h1, y2+h2) - max(y1,y2)
        if inter_w <= 0 or inter_h <= 0: return 0
        return inter_w*inter_h / (w1*h1 + w2*h2 - inter_w*inter_h)

# ============ 5. 主程序入口 ============
if __name__ == "__main__":
    # 初始化 Pipeline (OSD渲染在 HDMI/屏幕)
    pl = PipeLine(rgb888p_size=[1920, 1080], display_mode="hdmi")
    pl.create()

    sensor = pl.sensor
    sensor.stop()
    sensor.reset()

    # 通道 2: 用于 AI 识别 (1080P)
    sensor.set_framesize(width=1920, height=1080, chn=2)
    sensor.set_pixformat(Sensor.RGBP888, chn=2)

    # 通道 1: 用于拍照上传 (320x240, 极大减少内存开销)
    sensor.set_framesize(width=160, height=120, chn=1)
    sensor.set_pixformat(Sensor.RGB565, chn=1)

    sensor.run()

    # 加载模型 (请确认路径正确)
    monitor = SilkwormMonitor("/sdcard/best.kmodel", ["Healthy", "Sick"], [640, 640])
    monitor.config_preprocess()

    try:
        while True:
            gc.collect() # 循环开始处清理
            img = pl.get_frame() # 获取通道2的帧
            res = monitor.run(img)
            monitor.process_logic(pl, sensor, res)
            pl.show_image()
    except KeyboardInterrupt:
        print("Exit by user")
    except Exception as e:
        print("Loop Error:", e)
    finally:
        pl.destroy()
