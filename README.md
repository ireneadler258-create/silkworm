# Silkworm Smart Farming IoT System

> 铓曞吇娈栨櫤鑳界洃鎺х郴缁?鈥?ESP32-S3 杈圭紭缃戝叧 路 K230 AI 瑙嗚璇嗗埆 路 璺ㄥ钩鍙?App

涓€涓鍒扮鐨勭墿鑱旂綉鏅鸿兘铓曞吇娈栬В鍐虫柟妗堬紝闆?**杈圭紭 AI 鎺ㄧ悊銆佸浼犳劅鍣ㄧ幆澧冪洃娴嬨€佽嚜鍔ㄧ幆澧冭皟鎺с€佷簯绔仴娴嬨€佺Щ鍔ㄧ App 鎺у埗** 浜庝竴浣撱€備笓涓哄皬瑙勬ā铓曞吇娈栨埛璁捐锛屼綆鎴愭湰銆侀珮闆嗘垚搴︺€佸彲绂荤嚎杩愯銆?
---

## 绯荤粺鏋舵瀯鍏ㄦ櫙

```mermaid
flowchart TB
    subgraph "AI 璁粌 Pipeline (PC)"
        YOLO[YOLO11n/YOLO26n<br/>璁粌 + 瓒呭弬鏁拌皟浼榏 --> ONNX[ONNX 瀵煎嚭<br/>opset=11, simplify]
        ONNX --> KMODEL[K230 kmodel<br/>nncase 缂栬瘧] -.->|SD 鍗￠儴缃瞸 K230
    end

    subgraph "ESP32-S3 杈圭紭缃戝叧"
        direction TB
        K230[K230 AI 瑙嗚妯″潡<br/>YOLO 鎺ㄧ悊 路 鐩爣杩借釜<br/>鐥呰殨鎶撴媿 路 ImgBB 涓婁紶] -->|UART 涓插彛| ESP32[ESP32-S3 涓绘帶<br/>MicroPython 路 1s 涓诲惊鐜痌
        
        SENSORS[浼犳劅鍣ㄩ樀鍒梋 --> ESP32
        SENSORS --- DHT22["馃尅 娓╂箍搴?DHT22"]
        SENSORS --- BH1750["鈽€ 鍏夌収 BH1750"]
        SENSORS --- MQ137["馃И 姘ㄦ皵 MQ137"]
        SENSORS --- MHZ19["馃挩 CO鈧?MH-Z19"]
        SENSORS --- SOIL["馃尡 鍦熷￥婀垮害"]
        SENSORS --- IR["馃憗 绾㈠鍏ヤ镜"]
        SENSORS --- GPS["馃搷 GPS 瀹氫綅"]
        
        ESP32 --> ACTUATORS[鎵ц鍣╙
        ACTUATORS --- FAN["椋庢墖 (鏁ｇ儹鎺掗)"]
        ACTUATORS --- HEATER["鍔犵儹鍣?(淇濇俯)"]
        ACTUATORS --- ATOMIZER["闆惧寲鍣?(鍔犳箍)"]
        ACTUATORS --- RGB["RGB 琛ュ厜鐏?]
        ACTUATORS --- ALERT["鎶ヨ鐏?]
        
        ESP32 --> VOICE["璇煶鎾姤 ASR Pro<br/>UART 鍒嗘椂澶嶇敤"]
    end

    subgraph "闃块噷浜?IoT 骞冲彴"
        MQTT["MQTT Broker<br/>cn-shanghai"] --> RULES[瑙勫垯寮曟搸]
        RULES --> TSDB[鏃跺簭鏁版嵁搴?br/>璁惧灞炴€
    end

    subgraph "HBuilderX + uni-app App"
        APP[App<br/>Android / iOS / 灏忕▼搴廬 -->|WebSocket MQTT| MQTT
        APP -->|HTTP API<br/>鏌ヨ鍘嗗彶鏁版嵁| TSDB
    end

    ESP32 -->|MQTT 鐗╂ā鍨媩 MQTT
    USER[鍏绘畺鎴穄 --> APP
```

---

## 椤圭洰缁撴瀯

```
silkworm/
鈹溾攢鈹€ ai/                              # 馃 YOLO 铓曚綋妫€娴嬫ā鍨嬭缁?鈹?  鈹溾攢鈹€ train.py                     #    璁粌鑴氭湰 (鑷畾涔夎秴鍙傛暟)
鈹?  鈹溾攢鈹€ ce.py                        #    楠岃瘉璇勪及
鈹?  鈹溾攢鈹€ export_onnx.py               #    ONNX 瀵煎嚭 鈫?K230 閮ㄧ讲
鈹?  鈹溾攢鈹€ visualize_samples.py         #    鏁版嵁闆嗗彲瑙嗗寲
鈹?  鈹溾攢鈹€ yolo11n.pt                   #    棰勮缁冩潈閲?(宸?gitignore)
鈹?  鈹溾攢鈹€ yolo26n.pt                   #    棰勮缁冩潈閲?(宸?gitignore)
鈹?  鈹斺攢鈹€ datasets/                    #    璁粌鏁版嵁闆?(宸?gitignore)
鈹?      鈹溾攢鈹€ data.yaml                #    鏁版嵁闆嗛厤缃?(2 绫? healthy/unhealthy)
鈹?      鈹溾攢鈹€ train/                   #    璁粌闆?(images + labels)
鈹?      鈹斺攢鈹€ val/                     #    楠岃瘉闆?(images + labels)
鈹?鈹溾攢鈹€ esp32/                           # 馃敡 ESP32-S3 鍥轰欢 (MicroPython)
鈹?  鈹溾攢鈹€ main.py                      #    涓荤▼搴?(1 绉掓帶鍒跺惊鐜?
鈹?  鈹溾攢鈹€ K230/                        #    K230 AI 瑙嗚妯″潡鍥轰欢
鈹?  鈹?  鈹溾攢鈹€ main.py                  #        YOLO 鎺ㄧ悊 + 鐩爣杩借釜 + 鎶撴媿涓婁紶
鈹?  鈹?  鈹斺攢鈹€ best.kmodel              #        缂栬瘧鍚庣殑妯″瀷 (宸?gitignore)
鈹?  鈹溾攢鈹€ smart_control.py             #    鏅鸿兘鍐崇瓥寮曟搸 (闃堝€?妯″紡/鎵ц鍣?
鈹?  鈹溾攢鈹€ aliyun_mqtt.py               #    闃块噷浜?MQTT (HMAC-SHA1 璁よ瘉)
鈹?  鈹溾攢鈹€ wifi_conn.py                 #    WiFi 绠＄悊鍣?(鎸囨暟閫€閬块噸杩?
鈹?  鈹溾攢鈹€ system_guardian.py           #    鐪嬮棬鐙?+ GC + 杩愯鐩戞帶
鈹?  鈹溾攢鈹€ voice_alert.py               #    ASR Pro 璇煶鎶ヨ (UART 鍒嗘椂)
鈹?  鈹溾攢鈹€ dht_reader.py                #    DHT22 娓╂箍搴﹂┍鍔?鈹?  鈹溾攢鈹€ bh1750_reader.py             #    BH1750 鍏夌収椹卞姩
鈹?  鈹溾攢鈹€ mq137_reader.py              #    MQ137 姘ㄦ皵椹卞姩
鈹?  鈹溾攢鈹€ co2_reader.py                #    MH-Z19 CO鈧傞┍鍔?鈹?  鈹溾攢鈹€ soil_reader.py               #    鍦熷￥婀垮害浼犳劅鍣ㄩ┍鍔?鈹?  鈹溾攢鈹€ gps_reader.py                #    GPS (NMEA 瑙ｆ瀽 + 30s 缂撳瓨)
鈹?  鈹溾攢鈹€ ir_reader.py                 #    绾㈠鍏ヤ镜妫€娴?鈹?  鈹溾攢鈹€ k230_reader.py               #    K230 涓插彛鏁版嵁璇诲彇
鈹?  鈹溾攢鈹€ actuator_controller.py       #    鎵ц鍣?GPIO 鎶借薄
鈹?  鈹溾攢鈹€ boot.py                      #    鍚姩鑴氭湰
鈹?  鈹溾攢鈹€ REPL.py                      #    璋冭瘯 REPL
鈹?  鈹斺攢鈹€ docs/                        #    鏋舵瀯鏂囨。涓庢祦绋嬪浘
鈹?鈹斺攢鈹€ miniprogram/                     # 馃摫 HBuilderX + uni-app (Vue3 + TypeScript)
    鈹溾攢鈹€ src/
    鈹?  鈹溾攢鈹€ api/aliyun.ts            #    闃块噷浜?IoT HTTP API 灏佽
    鈹?  鈹溾攢鈹€ utils/ws-polyfill.ts     #    馃攽 WebSocket Polyfill 閫傞厤灞?    鈹?  鈹溾攢鈹€ store/
    鈹?  鈹?  鈹溾攢鈹€ device.ts            #    鍝嶅簲寮忕姸鎬佺鐞嗕腑蹇?    鈹?  鈹?  鈹斺攢鈹€ lang.ts              #    鍥介檯鍖?(涓?鑻?
    鈹?  鈹溾攢鈹€ pages/
    鈹?  鈹?  鈹溾攢鈹€ dashboard/index.vue  #    鎬昏椤?(6 浼犳劅鍣ㄥ崱鐗?
    鈹?  鈹?  鈹溾攢鈹€ control/index.vue    #    鎺у埗椤?(鎵ц鍣?+ 妯″紡鍒囨崲)
    鈹?  鈹?  鈹溾攢鈹€ alarm/index.vue      #    鎶ヨ涓績 (鍏ヤ镜/鐥呰殨/鐜鍛婅)
    鈹?  鈹?  鈹溾攢鈹€ history/index.vue    #    鍘嗗彶鏁版嵁瓒嬪娍鍥?(1h/6h/24h/7d)
    鈹?  鈹?  鈹斺攢鈹€ sick-history/        #    鐥呰殨妫€娴嬪巻鍙茶褰?    鈹?  鈹溾攢鈹€ components/
    鈹?  鈹?  鈹溾攢鈹€ SensorCard.vue       #    Liquid Glass 浼犳劅鍣ㄥ崱鐗?    鈹?  鈹?  鈹溾攢鈹€ LineChart.vue        #    瓒嬪娍鎶樼嚎鍥?    鈹?  鈹?  鈹溾攢鈹€ AlertPopup.vue       #    鍏ㄥ眬鍛婅寮圭獥
    鈹?  鈹?  鈹溾攢鈹€ SickAlertCard.vue    #    鐥呰殨鍛婅鍗＄墖
    鈹?  鈹?  鈹溾攢鈹€ Cube3D.vue           #    3D 瑁呴グ缁勪欢
    鈹?  鈹?  鈹斺攢鈹€ NeonToggle3D.vue     #    Neon 寮€鍏崇粍浠?    鈹?  鈹溾攢鈹€ static/                  #    鍥炬爣璧勬簮
    鈹?  鈹溾攢鈹€ manifest.json            #    uni-app 閰嶇疆鏂囦欢
    鈹?  鈹溾攢鈹€ pages.json               #    璺敱閰嶇疆
    鈹?  鈹斺攢鈹€ uni.scss                 #    鍏ㄥ眬鏍峰紡鍙橀噺
    鈹溾攢鈹€ docs/                        #    璁捐鏂囨。涓庤鏍?    鈹溾攢鈹€ index.html
    鈹溾攢鈹€ vite.config.ts
    鈹溾攢鈹€ tsconfig.json
    鈹斺攢鈹€ package.json
```

---

## 涓夊ぇ瀛愮郴缁熻瑙?
### 馃 AI 妯″瀷璁粌 (`ai/`)

**鐥涚偣锛?* 浼犵粺铓曞吇娈栦緷璧栦汉宸ヨ倝鐪煎贰妫€鐥呰殨锛屾晥鐜囦綆銆佷富瑙傛€у己銆佹棤娉曟寔缁€?
鍒╃敤 **Ultralytics YOLO11n** 鏋勫缓铓曚綋鍋ュ悍妫€娴嬫ā鍨嬶紝缁忚繃瓒呭弬鏁拌皟浼樸€丱NNX 瀵煎嚭銆乶ncase 缂栬瘧涓夋閮ㄧ讲鍒?K230 杈圭紭鑺墖锛?
- **鑷畾涔夋崯澶辨潈閲嶏細** `box=10.0`, `cls=0.8`, `dfl=2.0` 鈥?鎻愬崌妫€娴嬫绮惧害涓庡仴搴?鐥呰殨鍒嗙被鑳藉姏
- **鏁版嵁澧炲己绛栫暐锛?* `mixup=0.2`, `copy_paste=0.3`, `mosaic=1.0` 鈥?瑙ｅ喅灏忔牱鏈繃鎷熷悎
- **浼樺寲鍣細** `AdamW`, `lr0=0.001`
- **閮ㄧ讲閾捐矾锛?* `YOLO 璁粌 鈫?.pt 鈫?ONNX (opset=11, simplify) 鈫?.kmodel (nncase) 鈫?K230`

```
璁粌閾捐矾:
  鏁版嵁闆?data.yaml: 2 classes) 鈫?YOLO.train(epochs=100, imgsz=640, batch=8)
  鈫?best.pt 鈫?export_onnx.py 鈫?best.onnx 鈫?nncase 缂栬瘧 鈫?best.kmodel 鈫?SD 鍗?鈫?K230
```

---

### 馃敡 ESP32-S3 杈圭紭缃戝叧 (`esp32/`)

**鐥涚偣锛?* 7脳24 灏忔椂澶氱淮搴︾洃鎺?+ AI 瑙嗚 + 鑷姩璋冩帶锛屼紶缁?PLC 鎴愭湰楂樸€佸崟浼犳劅鍣ㄦ柟妗堝姛鑳藉崟涓€銆?
#### K230 AI 瑙嗚鎺ㄧ悊 (杈圭紭閮ㄧ讲)

K230 鏄竴棰?RISC-V AI 鑺墖锛屾湰鍦拌繍琛?YOLO 妯″瀷锛?*鏃犻渶鑱旂綉鍗冲彲瀹炴椂妫€娴?*锛?
```
鎽勫儚澶?1080P 甯?鈫?letterbox 棰勫鐞?鈫?YOLO 鎺ㄧ悊 鈫?NMS 鍘婚噸(0.4 IoU)
鈫?鐩爣杩借釜(娆ф皬璺濈 < 120px 鍖归厤) 鈫?闈欐璁℃暟(50 甯?鐫＄湢)
鈫?鐥呰殨妫€娴?鈫?鎶撴媿(160脳120) 鈫?Base64 鈫?ImgBB 涓婁紶 鈫?URL 涓插彛鍥炰紶 ESP32
```

鍏抽敭浼樺寲锛?- **鍙岄€氶亾鎽勫儚澶达細** 閫氶亾 2 (1080P) 鐢ㄤ簬 AI 璇嗗埆锛岄€氶亾 1 (160脳120) 鐢ㄤ簬鎶撴媿涓婁紶锛屽ぇ骞呴檷浣庡唴瀛樺崰鐢?- **閫愬抚 GC锛?* 姣忓惊鐜紑濮嬪 `gc.collect()`锛岄槻姝㈠唴瀛樼鐗?- **ImgBB 鍐峰嵈锛?* 60 绉掑唴閲嶅鐥呰殨涓嶉噸澶嶄笂浼狅紝閬垮厤 API 闄愭祦
- **涓插彛鏁版嵁甯у崗璁細** `DATA:T%d,H%d,U%d,S%d|URL:%s\n`

#### 澶?Agent 绾ц仈鍗忎綔

```
姣?1 绉掍富寰幆:
  Guardian.鍠傜嫍()
  鈫?WiFiManager.淇濇椿() 鈫?MQTTManager.淇濇椿() 鈫?MQTTManager.妫€鏌ユ寚浠?)
  鈫?read_k230() + read_dht22() + read_bh1750() + read_mq137() + read_soil() + read_ir()
  鈫?SmartController.update(浼犳劅鍣?+ AI 鏁版嵁)
  鈫?voice_alert.check_and_alert()
  鈫?CO2/GPS 鎱㈤€熻鍙?30s 缂撳瓨)
  鈫?鏋勫缓鐗╂ā鍨嬫暟鎹寘 鈫?MQTT 鍙戝竷
  鈫?Guardian.GC() 鈫? sleep(鏍″噯鍒?1s)
```

#### 鏅鸿兘鍐崇瓥寮曟搸 (`SmartController`)

| 妯″紡 | 鏉′欢 | 鍔ㄤ綔 |
|---|---|---|
| **娓╁害鎺у埗** | `temp > TEMP_HIGH(30鈩?` | 椋庢墖寮€锛屽姞鐑櫒鍏?|
| | `temp < TEMP_LOW(15鈩?` | 椋庢墖鍏筹紝鍔犵儹鍣ㄥ紑 |
| **婀垮害鎺у埗** | `hum < HUM_LOW(40%)` | 闆惧寲鍣ㄥ紑 |
| | `hum > HUM_HIGH(80%)` | 闆惧寲鍣ㄥ叧 |
| **琛ュ厜鎺у埗** | `lux < LUX_LOW(1 Lux)` | RGB 鐏紑 |
| | `lux > LUX_HIGH(550 Lux)` | RGB 鐏叧 |
| **鎶ヨ鎺у埗** | `ir=1(鍏ヤ镜) 鎴?AI 鐥呰殨>0` | 鎶ヨ鐏紑 + 璇煶鎾姤 |

闃堝€煎彲閫氳繃 App **杩滅▼鍔ㄦ€佽皟鏁?*锛岃皟鏁村悗 ESP32 鑷姩鍚屾銆?
#### 閫氫俊鍙潬鎬?
- **MQTT 鎸囨暟閫€閬块噸杩烇細** `wait = 1 脳 2^attempt`锛屾渶闀?5 娆″皾璇?- **WiFi 鑷姩淇濇椿锛?* 姣?5 绉掓鏌ヨ繛鎺ョ姸鎬侊紝鏂紑鑷姩閲嶈繛
- **UART 鍒嗘椂澶嶇敤锛?* CO鈧傘€丟PS銆乂oiceAlert 鍏变韩 UART1锛岄€氳繃涓存椂鍒涘缓/閿€姣佸疄渚嬮伩鍏嶅啿绐?- **鎵嬪姩鎿嶄綔閬胯锛?* 鐢ㄦ埛鎿嶄綔鍚?2 绉掑唴璺宠繃鑷姩鎺у埗锛岄槻姝簤鎶?- **纭欢鐪嬮棬鐙楋細** 300 绉掕秴鏃讹紝姝绘満鑷姩閲嶅惎

---

### 馃摫 HBuilderX + uni-app App (`miniprogram/`)

**鐥涚偣锛?* 鍏绘畺鎴烽渶瑕侀殢鏃舵煡鐪嬬姸鎬併€佹帴鏀跺憡璀︺€佽繙绋嬫帶鍒躲€侫pp 闇€鍚屾椂鏀寔 Android銆乮OS銆佸皬绋嬪簭锛屼笁濂楀師鐢熶唬鐮佺淮鎶ゆ垚鏈繃楂樸€?
閲囩敤 **HBuilderX + uni-app (Vue3 + TypeScript)**锛屼竴濂椾唬鐮佸悓鏃剁紪璇戝埌 Android銆乮OS銆丠5 鍜屽井淇″皬绋嬪簭銆傛牳蹇冮€氫俊灞傞€氳繃 **WebSocket Polyfill** 閫傞厤 uni-app 鍘熺敓鐜銆?
#### 閫氫俊鏋舵瀯

```mermaid
flowchart LR
    subgraph "App (HBuilderX)"
        WS[UniWebSocket Polyfill<br/>uni.connectSocket 鈫?鏍囧噯 WebSocket]
        MQTT[mqtt.js<br/>WSS 鍗忚]
        API[callAliyunIot<br/>HTTP 绛惧悕 API]
    end

    WS -->|娉ㄥ叆 globalThis| MQTT
    MQTT -->|wss:// 鎴?wxs://| ALIYUN[闃块噷浜?IoT]
    API -->|GET + HMAC-SHA1| ALIYUN

    ALIYUN -->|鐗╂ā鍨嬫帹閫亅 MQTT
    ALIYUN -->|QueryDevicePropertyData| API
```

**UniWebSocket Polyfill 鈥?鍏抽敭宸ョ▼鍐崇瓥锛?*

mqtt.js v4.x 渚濊禆娴忚鍣ㄥ師鐢?`WebSocket`锛屼絾 uni-app 鍘熺敓 App 娌℃湁姝ゅ叏灞€瀵硅薄銆傛柟妗堜笉鏄浛鎹?mqtt 搴擄紝鑰屾槸鍒涘缓**閫傞厤灞?*锛?
```typescript
class UniWebSocket implements WebSocket {
    // 鍖呰 uni.connectSocket 鈫?鏍囧噯 WebSocket 鎺ュ彛
    // 瀹炵幇: onopen, onmessage, onerror, onclose, send(), close()
    // readyState 甯搁噺, binaryType, bufferedAmount 绛?}
// 娉ㄥ叆鍒?globalThis锛岃 mqtt.js 鏃犳劅鐭ヨ繍琛?(globalThis as any).WebSocket = UniWebSocket;
```

#### App 鍔熻兘妯″潡

| 椤甸潰 | 鍔熻兘 |
|---|---|
| **鎬昏** (Dashboard) | 6 浼犳劅鍣ㄥ疄鏃舵暟鎹崱鐗?(娓?婀?CO鈧?鍏夌収/NH鈧?鍦熷￥婀垮害) + ESP32 鍦ㄧ嚎鐘舵€?+ 鑳屾櫙涓婚鍒囨崲 |
| **鎺у埗** (Control) | 鎵ц鍣ㄥ紑鍏?(椋庢墖/鍔犵儹/闆惧寲/RGB鐏?鎶ヨ鐏? + 鑷姩/鎵嬪姩妯″紡鍒囨崲 + 闃堝€艰繙绋嬭缃?|
| **鎶ヨ涓績** (Alarm) | 鍏ヤ镜妫€娴?+ 鐥呰殨鍛婅 + 鐜鍛婅璁板綍 + 浠婃棩鍛婅缁熻 |
| **鍘嗗彶鏁版嵁** (History) | 1h/6h/24h/7d 瓒嬪娍鎶樼嚎鍥?+ 浜戠鍘嗗彶澧為噺鍚屾 + 瓒嬪娍鍒嗘瀽 |
| **鐥呰殨鍘嗗彶** (Sick History) | 鐥呰殨鎶撴媿鍥剧墖鍒楄〃 + 绱鐥呰殨鏁?+ 鏈湴鍥剧墖缂撳瓨 |

#### 鍛婅寮曟搸 (澶氱骇鐘舵€佹満)

```
浼犳劅鍣ㄦ暟鎹祦 鈫?闃堝€兼瘮杈?鈫?鐘舵€佸彉鏇存娴?
  trigger:      姝ｅ父 鈫?寮傚父 (绔嬪嵆鍛婅 + 鎸姩 + 寮圭獥)
  persistent:   寮傚父鎸佺画 鈮?0 鍒嗛挓 (浜屾鎻愰啋)
  recovery:     寮傚父 鈫?姝ｅ父 (娓呴櫎寮傚父鏍囪)

鍐峰嵈瑙勫垯: 2 鍒嗛挓/鐩稿悓鎸囨爣+鏂瑰悜锛岄槻姝㈠埛灞?寮圭獥琛屼负: 杞诲井鍛婅 5s 鑷姩鍏抽棴锛屼弗閲嶅憡璀﹂渶鎵嬪姩纭
```

#### 鎺у埗閿佹満鍒?
```
鐢ㄦ埛鎿嶄綔鎵ц鍣?鈫?controlLocks[key] = 褰撳墠鏃堕棿鎴?MQTT 浜戠娑堟伅鍒拌揪 鈫?妫€鏌?lock 鈫?< 2.5s 璺宠繃璇ュ瓧娈?鈫?绮剧‘闃插啿绐侊紝閬垮厤浜戠鏃х姸鎬佽鐩栧疄鏃舵搷浣?```

#### 鏁版嵁鍚屾

- **瀹炴椂閫氶亾锛?* WebSocket MQTT 璁㈤槄 `/${pk}/${dn}/user/get`锛屾帴鏀惰澶囨帹閫?- **鍘嗗彶閫氶亾锛?* HTTP API 鏌ヨ `QueryDevicePropertyData`锛屽閲忔媺鍙?(棣栨 12h锛屼箣鍚庡閲?
- **鏈湴鎸佷箙鍖栵細** `uni.setStorageSync` 缂撳瓨鍘嗗彶鏁版嵁銆佸憡璀︿簨浠躲€佺梾铓曞浘鐗囪褰?
#### App 浣撻獙鐗规€?
- **Liquid Glass UI锛?* `backdrop-filter: blur(20px)` 姣涚幓鐠冩晥鏋?+ 寰氦浜掑姩鐢?- **4 濂楁笎鍙樹富棰橈細** 椹崱榫?钖勮嵎/鏃ヨ惤/鏋佸厜锛孲VG 棰滆壊鎻掑€?- **涓嫳鏂囧浗闄呭寲锛?* 涓€閿垏鎹紝鍏ㄩ〉闈㈠疄鏃跺搷搴?- **鐥呰殨鍥剧墖绠＄悊锛?* 鑷姩涓嬭浇 鈫?鏈湴缂撳瓨 鈫?缂╃暐鍥惧垪琛?鈫?鍒犻櫎/娓呯┖

---

## 鏁版嵁娴佸叏鏅?
```
浼犳劅鍣?鈫?ESP32 GPIO(1绉掑懆鏈? 鈹€鈹?K230 AI 鈫?UART 涓插彛(1绉掑懆鏈? 鈹€鈹尖攢鈫?SmartController(闃堝€煎喅绛?
浜戞寚浠?鈫?MQTT 璁㈤槄鍥炶皟 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?       鈹?                                         鈹溾攢鈫?GPIO 鎵ц鍣?(椋庢墖/鍔犵儹/闆惧寲/鐏厜)
                                         鈹溾攢鈫?UART 璇煶 (ASR Pro)
                                         鈹斺攢鈫?MQTT 鍙戝竷 (闃块噷浜戠墿妯″瀷)
                                                      鈹?                                              鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                                              鈹?  闃块噷浜?IoT    鈹?                                              鈹? MQTT Broker   鈹?                                              鈹? + 鏃跺簭鏁版嵁搴?  鈹?                                              鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                                                      鈹?                                              鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                                              鈹?App (uni-app)   鈹?                                              鈹?瀹炴椂 MQTT 璁㈤槄  鈹?                                              鈹?HTTP 鍘嗗彶鏌ヨ   鈹?                                              鈹?UI 娓叉煋 + 鍛婅  鈹?                                              鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

---

## 鎶€鏈爤

| 灞傜骇 | 鎶€鏈?| 鐢ㄩ€?|
|---|---|---|
| **AI 璁粌** | Ultralytics YOLO11n/YOLO26n, PyTorch | 铓曚綋鍋ュ悍妫€娴嬫ā鍨?|
| **妯″瀷瀵煎嚭** | ONNX (opset=11), nncase | 杈圭紭绔帹鐞嗛儴缃?|
| **AI 鎺ㄧ悊** | K230 (Kendryte RISC-V), nncase_runtime | 瀹炴椂瑙嗛娴?YOLO 鎺ㄧ悊 |
| **宓屽叆寮?* | ESP32-S3, MicroPython | 杈圭紭缃戝叧涓绘帶 |
| **浼犳劅鍣?* | DHT22, BH1750, MQ137, MH-Z19, 鍦熷￥婀垮害, GPS, 绾㈠ | 鐜鐩戞祴 |
| **鎵ц鍣?* | 缁х數鍣?(椋庢墖/鍔犵儹鍣?闆惧寲鍣?, RGB LED, 铚傞福鍣?| 鐜璋冩帶 |
| **璇煶** | ASR Pro (UART 涓插彛鍗忚) | 璇煶鎶ヨ |
| **浜戝钩鍙?* | 闃块噷浜?IoT (MQTT + HTTP API) | 璁惧鎺ュ叆涓庨仴娴?|
| **App 妗嗘灦** | HBuilderX + uni-app (Vue3 + TypeScript) | 璺ㄥ钩鍙扮Щ鍔ㄧ |
| **閫氫俊** | MQTT over WebSocket, HMAC-SHA1 绛惧悕 | 瀹炴椂鍙屽悜閫氫俊 |
| **UI** | Liquid Glass (姣涚幓鐠?, 娓愬彉涓婚 | 鐢ㄦ埛鐣岄潰 |

---

## 蹇€熼儴缃?
### 1. ESP32 鍥轰欢

```bash
# 1. 灏?esp32/ 鐩綍涓嬫墍鏈?.py 鏂囦欢涓婁紶鍒?ESP32 鏂囦欢绯荤粺
# 2. 淇敼 main.py 涓殑閰嶇疆:
```

```python
# esp32/main.py
SSID = "浣犵殑WiFi鍚嶇О"
PASSWORD = "浣犵殑WiFi瀵嗙爜"
PRODUCT_KEY = '浣犵殑闃块噷浜戜骇鍝並ey'
DEVICE_NAME = '浣犵殑璁惧鍚嶇О'
DEVICE_SECRET = '浣犵殑璁惧瀵嗛挜'
```

### 2. K230 妯″潡

```bash
# 1. 灏?best.kmodel 鏀惧叆 K230 SD 鍗?/sdcard/ 鐩綍
# 2. 灏?K230/main.py 涓婁紶鍒?K230
# 3. 淇敼 WIFI_SSID / WIFI_PASS / IMG_BB_KEY
```

### 3. 闃块噷浜?IoT 閰嶇疆

1. 鍒涘缓鐗╄仈缃戝钩鍙颁骇鍝侊紝瀹氫箟鐗╂ā鍨?(灞炴€? temperature, humidity, CO鈧? NH鈧? lux, soilHumidity, Silkworm_Total 绛?
2. 娉ㄥ唽璁惧锛岃幏鍙?ProductKey / DeviceName / DeviceSecret
3. 閰嶇疆璁惧绔?MQTT 鍙傛暟

### 4. App

```bash
# 浣跨敤 HBuilderX 鎵撳紑 miniprogram/ 鐩綍
# 淇敼 src/store/device.ts 涓殑闃块噷浜戦厤缃?# 杩愯鍒?Android/iOS 鐪熸満鎴栧井淇″皬绋嬪簭
```

---

## 娉ㄦ剰浜嬮」

- 鏈粨搴撲笂浼犳椂宸叉浛鎹㈡晱鎰熷嚟鎹负鍗犱綅绗︼紝**鏈湴鏂囦欢鍙︿繚鐣欑湡瀹炲€?*
- `ai/datasets/` 涓鸿缁冩暟鎹泦锛屾湭绾冲叆鐗堟湰鎺у埗
- `*.pt`, `*.kmodel` 涓烘ā鍨嬫潈閲嶆枃浠讹紝浣撶Н杈冨ぇ宸?gitignore
- K230 鍥轰欢闇€瑕佸崟鐙€氳繃涓插彛鎴?SD 鍗＄儳褰?- 闃块噷浜?IoT 闇€璐拱鎴栧紑閫氬厤璐硅瘯鐢紝閰嶇疆璁惧鍚庢墠鍙€氫俊

---

## License

MIT License 鈥?浠呬緵瀛︿範鍜屽弬鑰?