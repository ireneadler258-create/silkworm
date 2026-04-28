<template>
	<view class="page-container" :style="backgroundStyle">
		<view class="header-section" :style="{ paddingTop: statusBarHeight + 'px' }">
			<text class="main-title">{{ lang.isEnglish ? 'Alarm Center' : '报警中心' }}</text>
			<text class="sub-title">{{ lang.isEnglish ? 'Real-time alerts and device status' : '实时告警与设备状态监控' }}</text>
		</view>

		<!-- 1. 状态概览 -->
		<view class="overview-row">
			<view class="overview-card">
				<view class="ov-dot" :class="store.status.esp32Online ? 'online' : 'offline'"></view>
				<text class="ov-label">{{ lang.isEnglish ? 'ESP32' : 'ESP32' }}</text>
				<text class="ov-value" :class="store.status.esp32Online ? 'green' : 'gray'">
					{{ store.status.esp32Online ? (lang.isEnglish ? 'Online' : '在线') : (lang.isEnglish ? 'Offline' : '离线') }}
				</text>
			</view>
			<view class="overview-card">
				<view class="ov-dot" :class="todayAlerts > 0 ? 'warning' : 'ok'"></view>
				<text class="ov-label">{{ lang.isEnglish ? 'Alerts Today' : '今日告警' }}</text>
				<text class="ov-value" :class="todayAlerts > 0 ? 'red' : 'gray'">{{ todayAlerts }} {{ lang.isEnglish ? 'events' : '条' }}</text>
			</view>
		</view>

		<!-- 2. 入侵检测 -->
		<view class="section-card" :class="{ alert: store.sensors.IRStatus }">
			<view class="section-header">
				<image src="/static/icons/alert.png" mode="aspectFit" class="section-icon" />
				<text class="section-title">{{ lang.isEnglish ? 'Intrusion Detection' : '入侵检测' }}</text>
			</view>
			<view class="ir-status">
				<view class="ir-dot" :class="{ active: store.sensors.IRStatus }"></view>
				<text class="ir-text" :class="{ danger: store.sensors.IRStatus }">
					{{ store.sensors.IRStatus
						? (lang.isEnglish ? 'Motion Detected!' : '检测到有人靠近！')
						: (lang.isEnglish ? 'No Motion' : '无异常') }}
				</text>
			</view>
		</view>

		<!-- 3. 病蚕警报 -->
		<SickAlertCard />

		<!-- 4. 最近告警记录 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">{{ lang.isEnglish ? 'Recent Alerts' : '最近告警' }}</text>
				<text v-if="recentAlerts.length > 0" class="section-badge">{{ recentAlerts.length }}</text>
			</view>
			<view v-if="recentAlerts.length === 0" class="empty-row">
				<text class="empty-text">{{ lang.isEnglish ? 'No recent alerts' : '暂无告警记录' }}</text>
			</view>
			<view v-for="(a, i) in recentAlerts" :key="i" class="alert-row">
				<view class="alert-dot" :class="a.severityClass"></view>
				<view class="alert-info">
					<text class="alert-title">{{ a.title }}</text>
					<text class="alert-meta">{{ a.meta }}</text>
				</view>
				<text class="alert-time">{{ a.time }}</text>
			</view>
		</view>

		<!-- 4. 蚕健康监控 -->
		<view class="section-card">
			<view class="section-header">
				<image src="/static/icons/silk.png" mode="aspectFit" class="section-icon" />
				<text class="section-title">{{ lang.isEnglish ? 'Silkworm Health' : '蚕健康监控' }}</text>
			</view>
			<view class="sw-stats">
				<view class="sw-stat">
					<text class="sw-stat-label">{{ lang.isEnglish ? 'Total' : '总数' }}</text>
					<text class="sw-stat-value dark">{{ store.sensors.Silkworm_Total }}</text>
				</view>
				<view class="sw-stat">
					<text class="sw-stat-label">{{ lang.isEnglish ? 'Healthy' : '健康' }}</text>
					<text class="sw-stat-value green">{{ store.sensors.Silkworm_Healthy }}</text>
				</view>
				<view class="sw-stat">
					<text class="sw-stat-label">{{ lang.isEnglish ? 'Sick' : '病蚕' }}</text>
					<text class="sw-stat-value red">{{ store.sensors.Silkworm_Sick }}</text>
				</view>
				<view class="sw-stat">
					<text class="sw-stat-label">{{ lang.isEnglish ? 'Dormant' : '眠期' }}</text>
					<text class="sw-stat-value yellow">{{ store.sensors.Silkworm_Sleep }}</text>
				</view>
			</view>
			<view class="sw-bar-wrap">
				<text class="sw-bar-label">{{ lang.isEnglish ? 'Health Rate' : '健康率' }}: {{ healthRate }}%</text>
				<view class="sw-bar-bg">
					<view class="sw-bar-fill" :style="{ width: healthRate + '%' }"></view>
				</view>
			</view>
		</view>

		<!-- 5. GPS + 系统健康 -->
		<view class="section-card">
			<view class="section-header">
				<image src="/static/icons/gps-location.png" mode="aspectFit" class="section-icon" />
				<text class="section-title">{{ lang.isEnglish ? 'Location & System' : '位置与系统' }}</text>
			</view>
			<view class="gps-info">
				<view class="gps-row" @tap="copyCoordinate('longitude')">
					<text class="gps-label">{{ lang.isEnglish ? 'Longitude' : '经度' }}</text>
					<text class="gps-value">{{ store.sensors.Longitude || '--' }}</text>
					<text v-if="hasGpsData" class="gps-copy">{{ lang.isEnglish ? 'Copy' : '复制' }}</text>
				</view>
				<view class="gps-row" @tap="copyCoordinate('latitude')">
					<text class="gps-label">{{ lang.isEnglish ? 'Latitude' : '纬度' }}</text>
					<text class="gps-value">{{ store.sensors.Latitude || '--' }}</text>
					<text v-if="hasGpsData" class="gps-copy">{{ lang.isEnglish ? 'Copy' : '复制' }}</text>
				</view>
				<view class="gps-row">
					<text class="gps-label">{{ lang.isEnglish ? 'Altitude' : '海拔' }}</text>
					<text class="gps-value">{{ store.sensors.Altitude ? store.sensors.Altitude + (lang.isEnglish ? ' m' : ' 米') : '--' }}</text>
				</view>
				<!-- 地图按钮 -->
				<view class="gps-actions">
					<view 
						class="gps-btn" 
						:class="{ disabled: !hasGpsData }"
						@tap="openMap"
					>
						<text class="gps-btn-text">📍 {{ lang.isEnglish ? 'View on Map' : '查看地图' }}</text>
					</view>
					<view v-if="!hasGpsData" class="gps-hint">
						<text class="gps-hint-text">{{ lang.isEnglish ? 'GPS data unavailable' : 'GPS 数据不可用' }}</text>
					</view>
				</view>
			</view>
			<view class="sys-info">
				<view class="sys-row">
					<text class="sys-label">{{ lang.isEnglish ? 'Last Communication' : '最后通信' }}</text>
					<text class="sys-value">{{ store.status.lastSeenText }}</text>
				</view>
				<view class="sys-row">
					<text class="sys-label">MQTT {{ lang.isEnglish ? 'Connection' : '连接' }}</text>
					<text class="sys-value" :class="store.status.mqttConnected ? 'green' : 'gray'">
						{{ store.status.mqttConnected ? (lang.isEnglish ? 'Connected' : '已连接') : (lang.isEnglish ? 'Disconnected' : '已断开') }}
					</text>
				</view>
				<view class="sys-row">
					<text class="sys-label">ESP32 {{ lang.isEnglish ? 'Device' : '设备' }}</text>
					<text class="sys-value" :class="store.status.esp32Online ? 'green' : 'gray'">
						{{ store.status.esp32Online ? (lang.isEnglish ? 'Online' : '在线') : (lang.isEnglish ? 'Offline' : '离线') }}
					</text>
				</view>
			</view>
		</view>
		<AlertPopup />
	</view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { deviceStore as store } from '@/store/device';
import { langStore as lang } from '@/store/lang';
import AlertPopup from '@/components/AlertPopup.vue';
import SickAlertCard from '@/components/SickAlertCard.vue';

const statusBarHeight = ref(20);
const sysInfo = uni.getSystemInfoSync();
statusBarHeight.value = sysInfo.statusBarHeight || 20;

// 动态背景样式
const backgroundStyle = computed(() => store.getCurrentBackgroundStyle());

// 今日告警数
const todayAlerts = computed(() => {
	const todayStart = new Date();
	todayStart.setHours(0, 0, 0, 0);
	return store.envAlertEvents.filter(e => e.ts >= todayStart.getTime()).length;
});

// 最近告警（最多 5 条）
const recentAlerts = computed(() => {
	const metricName = (m: string) => {
		if (lang.isEnglish) {
			if (m === 'infrared') return 'Intrusion';
			return m;
		}
		if (m === 'temperature') return '温度';
		if (m === 'humidity') return '湿度';
		if (m === 'lux') return '光照';
		if (m === 'infrared') return '入侵检测';
		return m;
	};
	const typeLabel = (t: string, sev: string) => {
		if (lang.isEnglish) {
			if (t === 'trigger') return sev === 'severe' ? 'Severe' : 'Warning';
			if (t === 'persistent') return 'Persistent';
			return t;
		}
		if (t === 'trigger') return sev === 'severe' ? '严重' : '轻微';
		if (t === 'persistent') return '持续异常';
		return t;
	};

	return store.envAlertEvents
		.slice()
		.sort((a, b) => b.ts - a.ts)
		.slice(0, 3)
		.map(e => {
			const d = new Date(e.ts);
			const time = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
			const isIR = e.metric === 'infrared';
			const title = isIR
				? `${metricName(e.metric)} - ${lang.isEnglish ? 'Motion Detected' : '检测到有人靠近'}`
				: `${metricName(e.metric)} ${e.level === 'high' ? '>' : '<'} ${e.th}`;
			return {
				title,
				meta: `${typeLabel(e.type, e.severity)} · ${e.value}`,
				time,
				severityClass: e.severity === 'severe' ? 'severe' : 'light'
			};
		});
});

// 蚕健康率
const healthRate = computed(() => {
	const total = store.sensors.Silkworm_Total;
	if (!total) return 0;
	return Math.round((store.sensors.Silkworm_Healthy / total) * 100);
});

// GPS 数据是否有效
const hasGpsData = computed(() => {
	return store.sensors.Longitude && store.sensors.Latitude;
});

// 复制坐标到剪贴板
const copyCoordinate = (type: 'longitude' | 'latitude') => {
	if (!hasGpsData.value) return;
	
	const value = type === 'longitude' 
		? store.sensors.Longitude 
		: store.sensors.Latitude;
	
	uni.setClipboardData({
		data: String(value),
		success: () => {
			uni.showToast({
				title: lang.isEnglish ? 'Copied' : '已复制',
				icon: 'success',
				duration: 1500
			});
		}
	});
};

// 打开系统地图
const openMap = () => {
	if (!hasGpsData.value) {
		uni.showToast({
			title: lang.isEnglish ? 'GPS data unavailable' : 'GPS 数据不可用',
			icon: 'none'
		});
		return;
	}
	
	uni.openLocation({
		longitude: Number(store.sensors.Longitude),
		latitude: Number(store.sensors.Latitude),
		name: lang.isEnglish ? 'ESP32 Device' : 'ESP32 设备',
		address: lang.isEnglish ? 'Silkworm Monitoring Point' : '蚕养殖监控点',
		scale: 18,
		fail: (err) => {
			console.error('Open location failed:', err);
			uni.showToast({
				title: lang.isEnglish ? 'Failed to open map' : '打开地图失败',
				icon: 'none'
			});
		}
	});
};
</script>

<style lang="scss">
.page-container {
	padding: 60rpx 30rpx 40rpx;
	min-height: 100vh;
	// 流动渐变背景动画 - 与其他页面一致
	background: linear-gradient(
		-45deg,
		#4a6a80,
		#6a55a0,
		#906585,
		#a88565,
		#5ab0d8,
		#a070d0
	);
	background-size: 600% 600%;
	animation: gradientFlow 10s ease infinite;
}
.header-section {
	margin-bottom: 32rpx;
	background: rgba(255, 255, 255, 0.5);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	border-radius: 24rpx;
	padding: 20rpx 28rpx;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
	border: 1rpx solid rgba(255, 255, 255, 0.3);
	.main-title {
		font-size: 48rpx;
		font-weight: 800;
		color: #1a1a2e;
		display: block;
		text-shadow: 0 1rpx 2rpx rgba(255, 255, 255, 0.8);
	}
	.sub-title {
		font-size: 24rpx;
		color: rgba(26, 26, 46, 0.65);
		text-shadow: 0 1rpx 2rpx rgba(255, 255, 255, 0.8);
	}
}
/* 流动渐变背景动画 */
@keyframes gradientFlow {
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
}

/* 状态概览 */
.overview-row {
	display: flex;
	gap: 20rpx;
	margin-bottom: 24rpx;
}
.overview-card {
	flex: 1;
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	border-radius: 24rpx;
	padding: 24rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.25);
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}
.ov-dot {
	width: 14rpx;
	height: 14rpx;
	border-radius: 7rpx;
	&.online { background: #10b981; box-shadow: 0 0 10rpx rgba(16, 185, 129, 0.5); }
	&.offline { background: #94a3b8; }
	&.warning { background: #ef4444; box-shadow: 0 0 10rpx rgba(239, 68, 68, 0.5); }
	&.ok { background: #10b981; box-shadow: 0 0 10rpx rgba(16, 185, 129, 0.5); }
}
.ov-label {
	font-size: 22rpx;
	color: rgba(26, 26, 46, 0.65);
}
.ov-value {
	font-size: 28rpx;
	font-weight: 700;
	&.green { color: #059669; }
	&.red { color: #dc2626; }
	&.gray { color: rgba(26, 26, 46, 0.5); }
}

/* 通用区块卡片 */
.section-card {
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 24rpx;
	padding: 28rpx;
	margin-bottom: 24rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.25);
	box-shadow: 
		0 4rpx 20rpx rgba(0, 0, 0, 0.08),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.5);
	&.alert {
		border-color: rgba(239, 68, 68, 0.4);
		box-shadow: 
			0 4rpx 20rpx rgba(0, 0, 0, 0.08),
			0 0 20rpx 2rpx rgba(239, 68, 68, 0.2);
	}
}
.section-header {
	display: flex;
	align-items: center;
	gap: 12rpx;
	margin-bottom: 20rpx;
}
.section-icon {
	width: 40rpx;
	height: 40rpx;
}
.section-title {
	font-size: 28rpx;
	font-weight: 700;
	color: #1a1a2e;
	flex: 1;
}
.section-badge {
	background: rgba(239, 68, 68, 0.5);
	color: #fff;
	font-size: 20rpx;
	font-weight: 600;
	padding: 2rpx 12rpx;
	border-radius: 999rpx;
	box-shadow: 0 0 10rpx rgba(239, 68, 68, 0.3);
}

/* 入侵检测 */
.ir-status {
	display: flex;
	align-items: center;
	gap: 12rpx;
}
.ir-dot {
	width: 18rpx;
	height: 18rpx;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.3);
	transition: all 0.3s ease;
	&.active {
		background: #ef4444;
		box-shadow: 0 0 15rpx rgba(239, 68, 68, 0.6);
		animation: irPulse 0.8s ease-in-out infinite;
	}
}
/* 入侵检测脉冲动画 */
@keyframes irPulse {
	0% { 
		box-shadow: 0 0 15rpx rgba(239, 68, 68, 0.6);
		transform: scale(1);
	}
	50% { 
		box-shadow: 0 0 30rpx rgba(239, 68, 68, 0.9), 0 0 50rpx rgba(239, 68, 68, 0.4);
		transform: scale(1.2);
	}
	100% { 
		box-shadow: 0 0 15rpx rgba(239, 68, 68, 0.6);
		transform: scale(1);
	}
}
.ir-text {
	font-size: 26rpx;
	color: rgba(26, 26, 46, 0.7);
	&.danger {
		color: #dc2626;
		font-weight: 600;
	}
}
/* 文字发光动画 */
@keyframes textGlow {
	0%, 100% { 
		text-shadow: 0 0 10rpx rgba(239, 68, 68, 0.3);
	}
	50% { 
		text-shadow: 0 0 20rpx rgba(239, 68, 68, 0.6), 0 0 30rpx rgba(239, 68, 68, 0.3);
	}
}

/* 告警记录 */
.empty-row {
	padding: 20rpx 0;
	text-align: center;
}
.empty-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.5);
}
.alert-row {
	display: flex;
	align-items: center;
	gap: 14rpx;
	padding: 16rpx 0;
	border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);
	&:last-child { border-bottom: none; }
}
.alert-dot {
	width: 10rpx;
	height: 10rpx;
	border-radius: 5rpx;
	flex-shrink: 0;
	&.severe { background: #fca5a5; box-shadow: 0 0 8rpx rgba(239, 68, 68, 0.4); }
	&.light { background: #fcd34d; box-shadow: 0 0 8rpx rgba(245, 158, 11, 0.4); }
}
.alert-info {
	flex: 1;
}
.alert-title {
	font-size: 24rpx;
	color: #1a1a2e;
	font-weight: 600;
	display: block;
}
.alert-meta {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.6);
}
.alert-time {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.5);
	flex-shrink: 0;
}

/* 蚕健康 */
.sw-stats {
	display: flex;
	justify-content: space-between;
	margin-bottom: 20rpx;
}
.sw-stat {
	text-align: center;
	flex: 1;
}
.sw-stat-label {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.6);
	display: block;
	margin-bottom: 4rpx;
}
.sw-stat-value {
	font-size: 36rpx;
	font-weight: 700;
	&.dark { color: #1a1a2e; }
	&.green { color: #059669; }
	&.red { color: #dc2626; }
	&.yellow { color: #d97706; }
}
.sw-bar-wrap {
	margin-top: 8rpx;
}
.sw-bar-label {
	font-size: 22rpx;
	color: rgba(26, 26, 46, 0.65);
	font-weight: 500;
	display: block;
	margin-bottom: 8rpx;
}
.sw-bar-bg {
	height: 16rpx;
	border-radius: 8rpx;
	background: rgba(26, 26, 46, 0.1);
	overflow: hidden;
}
.sw-bar-fill {
	height: 100%;
	border-radius: 8rpx;
	background: linear-gradient(90deg, #10b981, #059669);
	box-shadow: 0 0 10rpx rgba(16, 185, 129, 0.4);
	transition: width 0.5s ease;
}

/* GPS + 系统 */
.gps-info {
	margin-bottom: 20rpx;
	padding-bottom: 20rpx;
	border-bottom: 1rpx solid rgba(26, 26, 46, 0.1);
}
.gps-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 8rpx 0;
}
.gps-label {
	font-size: 24rpx;
	color: rgba(26, 26, 46, 0.6);
	flex-shrink: 0;
}
.gps-value {
	font-size: 24rpx;
	color: #1a1a2e;
	font-weight: 500;
	flex: 1;
	text-align: right;
	margin-right: 12rpx;
}
.gps-copy {
	font-size: 20rpx;
	color: #2563eb;
	background: rgba(59, 130, 246, 0.15);
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
	flex-shrink: 0;
}
.gps-actions {
	margin-top: 16rpx;
	display: flex;
	align-items: center;
	gap: 16rpx;
}
.gps-btn {
	flex: 1;
	background: rgba(59, 130, 246, 0.15);
	padding: 14rpx 20rpx;
	border-radius: 12rpx;
	border: 1rpx solid rgba(59, 130, 246, 0.2);
	text-align: center;
	transition: all 0.2s ease;
	&:active:not(.disabled) {
		transform: scale(0.96);
	}
	&.disabled {
		opacity: 0.5;
		background: rgba(26, 26, 46, 0.05);
		border-color: rgba(26, 26, 46, 0.1);
	}
}
.gps-btn-text {
	font-size: 24rpx;
	color: #2563eb;
	font-weight: 500;
}
.gps-hint {
	flex: 1;
}
.gps-hint-text {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.4);
}
.sys-info {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}
.sys-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
}
.sys-label {
	font-size: 24rpx;
	color: rgba(26, 26, 46, 0.6);
}
.sys-value {
	font-size: 24rpx;
	font-weight: 600;
	color: #1a1a2e;
	&.green { color: #059669; }
	&.gray { color: rgba(26, 26, 46, 0.5); }
}
</style>