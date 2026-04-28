import { reactive } from 'vue';
import '@/utils/ws-polyfill'; // 必须在 mqtt 之前导入！注入全局 WebSocket
import * as mqtt from 'mqtt/dist/mqtt.min.js';
import CryptoJS from 'crypto-js';
import { callAliyunIot } from '@/api/aliyun';

// 阿里云 IoT 设备配置 (请替换为实际值)
const options = {
    productKey: 'your_product_key',
    deviceName: 'your_device_name',
    deviceSecret: 'your_device_secret',
    regionId: 'cn-shanghai',
    hardwareDeviceName: 'your_hardware_device_name',
    iotInstanceId: 'your_iot_instance_id'  // IoT 实例 ID（新版实例必须）
};

export const deviceStore = reactive({
    // 系统状态
    status: {
        mqttConnected: false,
        esp32Online: false,
        lastDataTime: 0,
        lastSeen: 0,
        lastSeenText: 'Waiting...',
        workMode: false,
        controlLocks: {} as Record<string, number>,
    },
    
    // 背景主题配置
    backgroundTheme: {
        current: 'macaron' as 'macaron' | 'mint' | 'sunset' | 'aurora',
        themes: {
            macaron: {
                name: '清新马卡龙',
                nameEn: 'Macaron',
                colors: ['#a8c0d4', '#c4b5d9', '#d4b5c4', '#e0c8b8', '#b8d0e0', '#c8b8d8'],
                duration: 12
            },
            mint: {
                name: '清新薄荷',
                nameEn: 'Mint',
                colors: ['#a8d4c0', '#b0d8d0', '#a8d0c8', '#b8d8c4', '#a0d4d0', '#b0d0c0'],
                duration: 14
            },
            sunset: {
                name: '温暖日落',
                nameEn: 'Sunset',
                colors: ['#d4b8a8', '#d8c0b0', '#d8c8a8', '#d0c0b8', '#d8b8a0', '#d0b8b0'],
                duration: 10
            },
            aurora: {
                name: '梦幻极光',
                nameEn: 'Aurora',
                colors: ['#b8a8d8', '#a8b8d8', '#a8c8d8', '#b8c0d8', '#a0b0d8', '#b0a8d8'],
                duration: 15
            }
        }
    },
    // 传感器数据（字段名需与硬件上报一致）
    sensors: {
        temperature: 0,
        humidity: 0,
        NH3: 0,
        CO2: 0,
        lux: 0,
        soilHumidity: 0,
        IRStatus: 0,
        Longitude: 0,
        Latitude: 0,
        Altitude: 0,
        // 蚕数据
        Silkworm_Total: 0,
        Silkworm_Healthy: 0,
        Silkworm_Sick: 0,
        Silkworm_Sleep: 0,
        // 病蚕图片
        SickImageUrl: ''
    },
    // 执行器状态（字段名需与设备上报一致）
    controls: {
        fanStatus: false,
        heaterStatus: false,
        atomizerStatus: false,
        lightStatus: false,
        IRStatus: false
    },
    // 阈值配置（与阿里云物模型标识符一致）
    thresholds: {
        TempHighTh: 30,
        TempLowTh: 15,
        HumLowTh: 40,
        HumHighTh: 80,
        LuxHighTh: 550,
        LuxLowTh: 1
    },
    // 本地历史记录（最多保留 24h）
    history: [] as Array<{
        ts: number;
        temperature: number;
        humidity: number;
        CO2: number;
        lux: number;
        NH3: number;
        soilHumidity: number;
        Silkworm_Total: number;
        Silkworm_Healthy: number;
        Silkworm_Sick: number;
        Silkworm_Sleep: number;
    }>,
    // 告警事件（环境 + 入侵）
    envAlertEvents: [] as Array<{
        ts: number;
        metric: 'temperature' | 'humidity' | 'lux' | 'infrared';
        level: 'low' | 'high';
        severity: 'light' | 'severe';
        type: 'trigger' | 'recovery' | 'persistent';
        value: number;
        th: number;
    }>,
    // 病蚕图片记录（最多保留 100 条）
    sickImageRecords: [] as Array<{
        id: string;
        url: string;
        localPath: string;
        sickCount: number;
        timestamp: number;
    }>,
    // 当前病蚕图片本地路径（内存缓存）
    _currentSickImagePath: '',
    _lastSickImageUrl: '',
    // 图片下载任务
    _sickImageDownloadTask: null as any,
    _historySaveTimer: null as any,
    _lastEnvState: {
        temperature: 'ok',
        humidity: 'ok',
        lux: 'ok'
    } as Record<'temperature' | 'humidity' | 'lux', 'ok' | 'low' | 'high'>,
    _lastIRStatus: 0,
    // 告警冷却：记录每个指标+方向的上次告警时间
    _lastAlertTime: {} as Record<string, number>,
    // 持续异常：记录每个指标开始异常的时间
    _abnormalStartTime: {} as Record<string, number>,
    _lastRecordTs: 0,

    // 全局报警弹窗状态
    alertPopup: {
        show: false,
        severity: 'light' as 'light' | 'severe',
        title: '',
        suggestion: '',
        isPersistent: false
    },

    client: null as any,
    historySyncing: false,
    historySyncReady: false,
    historySyncError: '',
    
    // 最后同步云端数据的时间
    _lastCloudSyncTime: 0,

    /** 初始化：连接 MQTT、加载本地数据、同步云端历史 */
    async init() {
        this.loadHistory();
        this.loadEnvAlerts();
        this.loadSickImageRecords();
        this.loadBackgroundTheme();  // 加载背景主题
        this.historySyncReady = this.history.length > 0;
        this.historySyncError = '';
        
        // 从云端同步历史数据（测试权限）
        this.fetchCloudHistory().catch(err => {
            this.historySyncError = err instanceof Error ? err.message : String(err);
            this.historySyncReady = true;
            this.historySyncing = false;
            console.warn('[Cloud] Sync history failed:', err);
        });
        
        this.initMqtt();
        setInterval(() => this.updateTimeText(), 10000);
        setInterval(() => this.checkEsp32Online(), 10000);
    },

    /** 加载背景主题 */
    loadBackgroundTheme() {
        try {
            const saved = uni.getStorageSync('background_theme');
            if (saved && this.backgroundTheme.themes[saved]) {
                this.backgroundTheme.current = saved;
            }
        } catch (e) {
            console.warn('Load background theme failed', e);
        }
    },

    /** 切换背景主题 */
    switchBackgroundTheme(theme?: 'macaron' | 'mint' | 'sunset' | 'aurora') {
        const themeKeys = Object.keys(this.backgroundTheme.themes) as Array<'macaron' | 'mint' | 'sunset' | 'aurora'>;
        
        if (theme) {
            this.backgroundTheme.current = theme;
        } else {
            // 循环切换
            const currentIndex = themeKeys.indexOf(this.backgroundTheme.current);
            const nextIndex = (currentIndex + 1) % themeKeys.length;
            this.backgroundTheme.current = themeKeys[nextIndex];
        }
        
        // 保存到本地
        uni.setStorageSync('background_theme', this.backgroundTheme.current);
        
        console.log('[Theme] Switched to:', this.backgroundTheme.current);
    },

    /** 获取当前主题的背景样式 */
    getCurrentBackgroundStyle() {
        const theme = this.backgroundTheme.themes[this.backgroundTheme.current];
        return {
            background: `linear-gradient(-45deg, ${theme.colors.join(', ')})`,
            backgroundSize: '600% 600%',
            animation: `gradientFlow ${theme.duration}s ease infinite`
        };
    },

    /** 从阿里云获取历史属性数据（增量同步） */
    async fetchCloudHistory() {
        if (this.historySyncing) return;
        this.historySyncing = true;
        this.historySyncError = '';
        if (this.history.length === 0) this.historySyncReady = false;

        const now = Date.now();
        let startTime: number;
        
        if (this._lastCloudSyncTime > 0) {
            // 增量同步：从上次同步时间开始（最多查 24 小时）
            startTime = Math.max(this._lastCloudSyncTime, now - 24 * 3600000);
            console.log('[Cloud] Incremental sync from', new Date(startTime).toLocaleTimeString());
        } else {
            // 首次同步：查询最近 12 小时
            startTime = now - 12 * 3600000;
            console.log('[Cloud] First sync (12h)');
        }
        
        const endTime = now;
        
        // 要查询的属性列表
        const properties = ['temperature', 'humidity', 'CO2', 'lux', 'NH3', 'soilHumidity'];
        
        // 使用 Map 临时存储，按时间戳合并
        const dataMap = new Map<number, any>();
        let totalNewPoints = 0;
        
        for (const prop of properties) {
            try {
                let nextTime = startTime;
                let hasNext = true;
                let pageCount = 0;
                const maxPages = 10;  // 每个属性最多 10 页 = 2000 条
                
                while (hasNext && nextTime < endTime && pageCount < maxPages) {
                    pageCount++;
                    
                    const res: any = await callAliyunIot('QueryDevicePropertyData', {
                        IotInstanceId: options.iotInstanceId,
                        ProductKey: options.productKey,
                        DeviceName: options.hardwareDeviceName,
                        Identifier: prop,
                        StartTime: nextTime,
                        EndTime: endTime,
                        PageSize: 200,
                        Asc: 1
                    });
                    
                    if (res.Success && res.Data?.List?.PropertyInfo) {
                        const list = res.Data.List.PropertyInfo;
                        
                        if (list.length === 0) {
                            hasNext = false;
                            break;
                        }
                        
                        for (const item of list) {
                            const ts = item.Time;
                            const val = parseFloat(item.Value);
                            
                            if (!isNaN(val) && !isNaN(ts) && ts > 0) {
                                if (!dataMap.has(ts)) {
                                    dataMap.set(ts, {
                                        ts,
                                        temperature: 0, humidity: 0, CO2: 0, lux: 0, NH3: 0, soilHumidity: 0,
                                        Silkworm_Total: 0, Silkworm_Healthy: 0, Silkworm_Sick: 0, Silkworm_Sleep: 0
                                    });
                                }
                                dataMap.get(ts)![prop] = val;
                            }
                        }
                        
                        hasNext = res.Data.NextValid && res.Data.NextTime > nextTime;
                        if (hasNext) {
                            nextTime = res.Data.NextTime;
                        }
                    } else {
                        hasNext = false;
                    }
                    
                    // 每页等待 80ms
                    await new Promise(resolve => setTimeout(resolve, 80));
                }
                
            } catch (e) {
                console.error(`[Cloud] ${prop} error:`, e);
            }
        }
        
        // 将新数据合并到本地历史
        const newData = Array.from(dataMap.values());
        if (newData.length > 0) {
            const existingTsSet = new Set(this.history.map(p => p.ts));
            let addedCount = 0;
            
            for (const point of newData) {
                if (!existingTsSet.has(point.ts)) {
                    this.history.push(point);
                    addedCount++;
                }
            }
            
            // 按时间排序
            this.history.sort((a, b) => a.ts - b.ts);
            
            // 只保留最近 7 天的数据
            const cutoff = now - 7 * 24 * 3600000;
            this.history = this.history.filter(p => p.ts >= cutoff);
            
            // 保存到本地
            this._scheduleSaveHistory();
            
            totalNewPoints = addedCount;
        }
        
        // 更新最后同步时间
        this._lastCloudSyncTime = now;
        this.historySyncReady = true;
        this.historySyncing = false;
        
        console.log(`[Cloud] Done: +${totalNewPoints} points, ${this.history.length} total`);
    },

    /** 检查 ESP32 是否在线（基于最后数据接收时间） */
    checkEsp32Online() {
        const TIMEOUT = 10 * 1000;  // 10 秒超时（ESP32 每秒发送一次数据）
        const now = Date.now();
        
        if (this.status.lastDataTime > 0) {
            const elapsed = now - this.status.lastDataTime;
            if (elapsed > TIMEOUT) {
                this.status.esp32Online = false;
            }
        }
    },

    /** 从本地存储加载历史数据 */
    loadHistory() {
        try {
            const raw = uni.getStorageSync('sensor_history_v1');
            if (raw) {
                const arr = JSON.parse(raw);
                if (Array.isArray(arr)) this.history = arr;
            }
            this.historySyncReady = this.history.length > 0;
        } catch (e) {
            this.historySyncReady = false;
            console.warn('Load history failed', e);
        }
    },

    /** 从本地存储加载环境告警 */
    loadEnvAlerts() {
        try {
            const raw = uni.getStorageSync('env_alerts_v1');
            if (raw) {
                const arr = JSON.parse(raw);
                if (Array.isArray(arr)) this.envAlertEvents = arr;
            }
        } catch (e) {
            console.warn('Load env alerts failed', e);
        }
    },

    /** 从本地存储加载病蚕图片记录 */
    loadSickImageRecords() {
        try {
            const raw = uni.getStorageSync('sick_image_records_v1');
            if (raw) {
                const arr = JSON.parse(raw);
                if (Array.isArray(arr)) this.sickImageRecords = arr;
            }
        } catch (e) {
            console.warn('Load sick image records failed', e);
        }
    },

    /** 保存病蚕图片记录到本地 */
    saveSickImageRecords() {
        try {
            // 最多保留 100 条
            if (this.sickImageRecords.length > 100) {
                this.sickImageRecords = this.sickImageRecords.slice(-100);
            }
            uni.setStorageSync('sick_image_records_v1', JSON.stringify(this.sickImageRecords));
        } catch (e) {
            console.warn('Save sick image records failed', e);
        }
    },

    /** 防抖保存：500ms 内多次调用只执行一次 */
    _scheduleSaveHistory() {
        if (this._historySaveTimer) return;
        this._historySaveTimer = setTimeout(() => {
            this._historySaveTimer = null;
            try {
                uni.setStorageSync('sensor_history_v1', JSON.stringify(this.history));
                uni.setStorageSync('env_alerts_v1', JSON.stringify(this.envAlertEvents));
            } catch (e) {
                console.warn('Save history failed', e);
            }
        }, 500);
    },

    /** 记录历史数据点，至少间隔 30s，只保留 24h（约 2880 个点） */
    recordHistoryPoint(ts = Date.now()) {
        if (!this.status.lastSeen) return;
        if (Date.now() - this.status.lastSeen > 2 * 60 * 1000) return;
        if (ts - this._lastRecordTs < 30000) return;
        this._lastRecordTs = ts;

        const point = {
            ts,
            temperature: Number(this.sensors.temperature) || 0,
            humidity: Number(this.sensors.humidity) || 0,
            CO2: Number(this.sensors.CO2) || 0,
            lux: Number(this.sensors.lux) || 0,
            NH3: Number(this.sensors.NH3) || 0,
            soilHumidity: Number(this.sensors.soilHumidity) || 0,
            Silkworm_Total: Number(this.sensors.Silkworm_Total) || 0,
            Silkworm_Healthy: Number(this.sensors.Silkworm_Healthy) || 0,
            Silkworm_Sick: Number(this.sensors.Silkworm_Sick) || 0,
            Silkworm_Sleep: Number(this.sensors.Silkworm_Sleep) || 0
        };

        this.history.push(point);

        const cutoff = Date.now() - 24 * 60 * 60 * 1000;
        while (this.history.length && (this.history[0]?.ts ?? 0) < cutoff) this.history.shift();

        this._scheduleSaveHistory();
    },

    _pushEnvAlert(
        metric: 'temperature' | 'humidity' | 'lux' | 'infrared',
        level: 'low' | 'high',
        severity: 'light' | 'severe',
        type: 'trigger' | 'recovery' | 'persistent',
        value: number,
        th: number,
        ts = Date.now()
    ) {
        this.envAlertEvents.push({ ts, metric, level, severity, type, value, th });
        const cutoff = Date.now() - 24 * 60 * 60 * 1000;
        while (this.envAlertEvents.length && (this.envAlertEvents[0]?.ts ?? 0) < cutoff) this.envAlertEvents.shift();
        this._scheduleSaveHistory();

        // 触发和持续异常时显示弹窗
        if (type === 'trigger' || type === 'persistent') {
            this.showAlertPopup(metric, level, severity, value, th);
        }
    },

    /** 判断告警级别：超出阈值 20% 以上为严重 */
    _getSeverity(value: number, th: number, level: 'low' | 'high'): 'light' | 'severe' {
        const deviation = Math.abs(value - th);
        const ratio = th !== 0 ? deviation / Math.abs(th) : deviation;
        return ratio >= 0.2 ? 'severe' : 'light';
    },

    /** 检测环境参数是否越界，改进的报警逻辑 */
    updateEnvAlerts(ts = Date.now()) {
        const metrics = [
            { key: 'temperature' as const, value: Number(this.sensors.temperature) || 0, highTh: this.thresholds.TempHighTh, lowTh: this.thresholds.TempLowTh },
            { key: 'humidity' as const, value: Number(this.sensors.humidity) || 0, highTh: this.thresholds.HumHighTh, lowTh: this.thresholds.HumLowTh },
            { key: 'lux' as const, value: Number(this.sensors.lux) || 0, highTh: Infinity, lowTh: this.thresholds.LuxLowTh }
        ];

        for (const m of metrics) {
            const state = m.value > m.highTh ? 'high' : m.value < m.lowTh ? 'low' : 'ok';
            const prevState = this._lastEnvState[m.key];
            const alertKey = `${m.key}_${state}`;
            const lastAlert = this._lastAlertTime[alertKey] || 0;
            const cooldown = 2 * 60 * 1000; // 2 分钟冷却
            const persistentThreshold = 10 * 60 * 1000; // 10 分钟持续异常

            if (state !== 'ok') {
                const th = state === 'high' ? m.highTh : m.lowTh;
                const severity = this._getSeverity(m.value, th, state as any);

                // 1. 状态变化：从 ok 变为异常，立即触发告警
                if (prevState === 'ok') {
                    this._pushEnvAlert(m.key, state as any, severity, 'trigger', m.value, th, ts);
                    this._lastAlertTime[alertKey] = ts;
                    this._abnormalStartTime[m.key] = ts;
                }
                // 2. 持续异常：超过 15 分钟且冷却已过，发送持续提醒
                else {
                    const abnormalStart = this._abnormalStartTime[m.key] || ts;
                    const abnormalDuration = ts - abnormalStart;
                    if (abnormalDuration >= persistentThreshold && ts - lastAlert >= cooldown) {
                        this._pushEnvAlert(m.key, state as any, severity, 'persistent', m.value, th, ts);
                        this._lastAlertTime[alertKey] = ts;
                    }
                }
            } else if (prevState !== 'ok') {
                // 3. 恢复正常：从异常回到 ok（不记录恢复事件，仅清除异常状态）
                delete this._abnormalStartTime[m.key];
            }

            this._lastEnvState[m.key] = state as any;
        }
    },

    /** 获取指定时间范围内的历史数据 */
    getHistory(rangeHours: 1 | 6 | 24 | 168) {
        const cutoff = Date.now() - rangeHours * 60 * 60 * 1000;
        return this.history.filter(p => p.ts >= cutoff);
    },

    /** 清除所有环境告警 */
    clearEnvAlerts() {
        this.envAlertEvents = [];
        this._scheduleSaveHistory();
    },

    /** 处理新的病蚕图片 URL */
    async handleNewSickImage(url: string) {
        if (!url || url === this._lastSickImageUrl) return;
        this._lastSickImageUrl = url;
        
        console.log('[SickImage] New image URL:', url);
        
        // 下载图片
        const localPath = await this.downloadSickImage(url);
        if (localPath) {
            this._currentSickImagePath = localPath;
            
            // 添加到历史记录
            const record = {
                id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                url,
                localPath,
                sickCount: Number(this.sensors.Silkworm_Sick) || 0,
                timestamp: Date.now()
            };
            this.sickImageRecords.unshift(record);
            this.saveSickImageRecords();
            
            // 显示病蚕告警弹窗
            this.showSickAlertPopup();
            
            // 振动提醒
            try { uni.vibrateShort({}); } catch (e) { }
        }
    },

    /** 下载病蚕图片到本地 */
    downloadSickImage(url: string): Promise<string> {
        return new Promise((resolve) => {
            const timeout = setTimeout(() => {
                console.warn('[SickImage] Download timeout');
                resolve('');
            }, 10000);

            const task = uni.downloadFile({
                url,
                timeout: 10000,
                success: (res) => {
                    clearTimeout(timeout);
                    if (res.statusCode === 200 && res.tempFilePath) {
                        // 保存到本地
                        uni.saveFile({
                            tempFilePath: res.tempFilePath,
                            success: (saveRes) => {
                                console.log('[SickImage] Saved to:', saveRes.savedFilePath);
                                resolve(saveRes.savedFilePath);
                            },
                            fail: (err) => {
                                console.warn('[SickImage] Save failed:', err);
                                resolve(res.tempFilePath); // 使用临时路径
                            }
                        });
                    } else {
                        console.warn('[SickImage] Download failed:', res.statusCode);
                        resolve('');
                    }
                },
                fail: (err) => {
                    clearTimeout(timeout);
                    console.warn('[SickImage] Download error:', err);
                    resolve('');
                }
            });
            
            this._sickImageDownloadTask = task;
        });
    },

    /** 删除病蚕图片记录 */
    deleteSickImageRecord(id: string) {
        const index = this.sickImageRecords.findIndex(r => r.id === id);
        if (index > -1) {
            // 删除本地文件
            const record = this.sickImageRecords[index];
            if (record && record.localPath) {
                uni.removeSavedFile({
                    filePath: record.localPath,
                    fail: () => {} // 忽略删除失败
                });
            }
            this.sickImageRecords.splice(index, 1);
            this.saveSickImageRecords();
        }
    },

    /** 清空所有病蚕图片记录 */
    clearSickImageRecords() {
        // 删除所有本地文件
        for (const record of this.sickImageRecords) {
            if (record.localPath) {
                uni.removeSavedFile({
                    filePath: record.localPath,
                    fail: () => {}
                });
            }
        }
        this.sickImageRecords = [];
        this._currentSickImagePath = '';
        this._lastSickImageUrl = '';
        this.saveSickImageRecords();
    },

    /** 显示全局报警弹窗 */
    showAlertPopup(metric: string, level: string, severity: string, value: number, th: number) {
        const suggestions: Record<string, string> = {
            temperature_high: '检查通风风扇是否开启，降低环境温度',
            temperature_low: '检查加热器是否正常工作，提升环境温度',
            humidity_low: '检查加湿器是否工作正常，增加环境湿度',
            infrared: '检查养殖区域是否有人员进入，确认安全后手动关闭警报灯',
            lux_low: '检查 LED 灯是否正常开启'
        };
        const names: Record<string, string> = {
            temperature: '温度',
            humidity: '湿度',
            lux: '光照',
            infrared: '入侵检测'
        };
        const isIR = metric === 'infrared';
        const key = isIR ? 'infrared' : `${metric}_${level}`;
        const title = isIR ? '检测到有人靠近' : `${names[metric] || metric}${level === 'high' ? '偏高' : '偏低'}（当前 ${value}，阈值 ${th}）`;
        const suggestion = suggestions[key] || '请检查相关设备状态';

        // 振动提醒
        try { uni.vibrateShort({}); } catch (e) { }

        // 设置弹窗状态（AlertPopup 组件会监听并显示）
        this.alertPopup = {
            show: true,
            severity: severity as any,
            title,
            suggestion,
            isPersistent: severity === 'severe'
        };
    },

    /** 关闭全局报警弹窗 */
    hideAlertPopup() {
        this.alertPopup.show = false;
    },

    /** 显示病蚕告警弹窗 */
    showSickAlertPopup() {
        // 振动提醒
        try { uni.vibrateShort({}); } catch (e) { }

        this.alertPopup = {
            show: true,
            severity: 'severe',
            title: '检测到病蚕',
            suggestion: '请及时检查蚕桑状态，确认病蚕数量并采取相应措施',
            isPersistent: true
        };
    },

    /** 查询 ESP32 设备在线状态（调用阿里云 API） */
    async fetchOnlineStatus() {
        try {
            const res: any = await callAliyunIot('QueryDeviceDetail', {
                IotInstanceId: options.iotInstanceId,
                ProductKey: options.productKey,
                DeviceName: options.hardwareDeviceName
            });
            if (res.Success) {
                this.status.esp32Online = res.Data.Status === 'ONLINE';
                console.log('[ESP32] Status:', this.status.esp32Online ? 'ONLINE' : 'OFFLINE');
            }
        } catch (e) {
            console.error('[ESP32] Fetch status failed', e);
        }
    },

    /** 更新"上次看到"时间显示 */
    updateTimeText() {
        if (this.status.lastSeen === 0) return;
        const diff = Math.floor((Date.now() - this.status.lastSeen) / 1000);
        if (diff < 60) this.status.lastSeenText = `${diff}s ago`;
        else this.status.lastSeenText = `${Math.floor(diff / 60)}m ago`;
    },

    /** 初始化 MQTT 连接 */
    initMqtt() {
        const timestamp = Date.now();
        const clientId = options.deviceName;
        const content = `clientId${clientId}deviceName${options.deviceName}productKey${options.productKey}timestamp${timestamp}`;
        const password = CryptoJS.HmacSHA1(content, options.deviceSecret).toString();

        // 平台检测：原生 App 用 wss://，小程序/H5 用 wxs://
        const platform = uni.getSystemInfoSync().platform;
        const isApp = platform === 'android' || platform === 'ios';
        const host = isApp
            ? `wss://${options.productKey}.iot-as-mqtt.${options.regionId}.aliyuncs.com:443`
            : `wxs://${options.productKey}.iot-as-mqtt.${options.regionId}.aliyuncs.com:443`;

        const mqttOptions: any = {
            clientId: `${clientId}|securemode=2,signmethod=hmacsha1,timestamp=${timestamp}|`,
            username: `${options.deviceName}&${options.productKey}`,
            password: password,
            keepalive: 60,
            clean: true,
            connectTimeout: 4000
        };

        console.log('[MQTT] Platform:', platform, 'Host:', host);
        this.client = mqtt.connect(host, mqttOptions);

        this.client.on('connect', () => {
            console.log('[MQTT] Connected');
            this.status.mqttConnected = true;
            const subTopic = `/${options.productKey}/${options.deviceName}/user/get`;
            this.client.subscribe(subTopic);
        });

        this.client.on('error', (err: any) => {
            console.error('[MQTT] Error:', err);
            this.status.mqttConnected = false;
        });

        this.client.on('reconnect', () => {
            console.log('[MQTT] Reconnecting...');
        });

        this.client.on('close', () => {
            console.log('[MQTT] Connection closed');
            this.status.mqttConnected = false;
        });

        this.client.on('offline', () => {
            console.log('[MQTT] Offline');
            this.status.mqttConnected = false;
        });

        // 处理云端下发的消息
        this.client.on('message', (topic: string, message: any) => {
            try {
                const res = JSON.parse(message.toString());
                const payload = res.items || res.params || res;
                const now = Date.now();
                this.status.lastSeen = now;
                this.status.lastDataTime = now;
                this.status.esp32Online = true;  // 收到数据 = ESP32 在线
                this.updateTimeText();

                for (let key in payload) {
                    let val = payload[key];
                    // 阿里云 items 嵌套结构 { value: x }
                    if (val && typeof val === 'object' && 'value' in val) val = val.value;

                    // 2.5s 内手动操作过的字段，忽略云端旧状态（匹配 ESP32 避让期 2s + 余量 0.5s）
                    const lastLockTime = this.status.controlLocks[key] || 0;
                    if (Date.now() - lastLockTime < 2500) continue;

                    // 更新传感器数据
                    if (key in this.sensors) {
                        (this.sensors as any)[key] = val;
                        // 病蚕图片 URL 特殊处理（兼容http和https）
                        if (key === 'SickImageUrl' && val && typeof val === 'string' && (val.startsWith('http://') || val.startsWith('https://'))) {
                            this.handleNewSickImage(val);
                        }
                    }
                    // 处理地理位置嵌套
                    else if (key === 'GeoLocation') {
                        this.sensors.Longitude = val.Longitude;
                        this.sensors.Latitude = val.Latitude;
                        this.sensors.Altitude = val.Altitude || 0;
                    }
                    // 更新控制状态（转布尔值）
                    if (key in this.controls) {
                        (this.controls as any)[key] = (val == 1 || val === true);
                    }
                    // 更新阈值（数值型）
                    if (key in this.thresholds) {
                        const n = Number(val);
                        if (!Number.isNaN(n)) (this.thresholds as any)[key] = n;
                    }
                    // 工作模式联动
                    if (key === 'ManualMode') {
                        this.status.workMode = (val == 1 || val === true);
                    }
                }

                // 记录历史和检测告警
                this.recordHistoryPoint(Date.now());
                this.updateEnvAlerts(Date.now());

                // 红外入侵检测
                const prevIR = this._lastIRStatus;
                const curIR = Number(this.sensors.IRStatus) || 0;
                if (curIR === 1 && prevIR === 0) {
                    // 检测到入侵，冷却 5 秒内不重复记录
                    const lastIRAlert = this._lastAlertTime['infrared'] || 0;
                    if (Date.now() - lastIRAlert > 5000) {
                        this.envAlertEvents.push({
                            ts: Date.now(),
                            metric: 'infrared',
                            level: 'high',
                            severity: 'severe',
                            type: 'trigger',
                            value: 1,
                            th: 0
                        });
                        this._lastAlertTime['infrared'] = Date.now();
                        this._scheduleSaveHistory();
                        this.showAlertPopup('infrared', 'high', 'severe', 1, 0);
                    }
                }
                this._lastIRStatus = curIR;
            } catch (e) {
                console.error('[MQTT] Message process error', e);
            }
        });
    },

    /** 发送执行器控制命令 */
    sendControl(key: string, value: any) {
        if (!this.client?.connected) {
            uni.showToast({ title: 'Device Offline', icon: 'none' });
            return;
        }
        this.status.controlLocks[key] = Date.now();

        const pubTopic = `/${options.productKey}/${options.deviceName}/user/update`;
        const payload = JSON.stringify({ [key]: value ? 1 : 0 });

        // 记录旧值，发送失败时回滚
        const oldValue = (this.controls as any)[key];
        this.client.publish(pubTopic, payload, (err: any) => {
            if (err) {
                console.error('[MQTT] Publish failed:', err);
                // 发送失败，回滚本地状态
                if (key in this.controls) {
                    (this.controls as any)[key] = oldValue;
                }
                delete this.status.controlLocks[key];
                uni.showToast({ title: 'Send Failed', icon: 'none' });
            }
        });

        // 本地先行更新，避免 UI 延迟
        if (key in this.controls) {
            (this.controls as any)[key] = value;
        }

        // 3 秒后主动刷新一次状态，确保与设备同步
        setTimeout(() => this.fetchOnlineStatus(), 3000);
    },

    /** 下发阈值配置 */
    sendThreshold(key: string, value: number) {
        if (!this.client?.connected) {
            uni.showToast({ title: 'Device Offline', icon: 'none' });
            return;
        }
        this.status.controlLocks[key] = Date.now();

        const pubTopic = `/${options.productKey}/${options.deviceName}/user/update`;
        const payload = JSON.stringify({ [key]: value });
        this.client.publish(pubTopic, payload);

        if (key in this.thresholds) {
            (this.thresholds as any)[key] = value;
        }
    },

    /** 切换工作模式（false=自动, true=手动） */
    setWorkMode(mode: boolean) {
        if (!this.client?.connected) {
            uni.showToast({ title: 'Device Offline', icon: 'none' });
            return;
        }
        this.status.controlLocks['ManualMode'] = Date.now();
        const pubTopic = `/${options.productKey}/${options.deviceName}/user/update`;
        const payload = JSON.stringify({ ManualMode: mode });
        this.client.publish(pubTopic, payload);
        this.status.workMode = mode;
    }
});