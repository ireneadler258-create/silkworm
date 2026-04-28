<template>
	<view class="page-container" :style="backgroundStyle">
		<view class="header-section">
			<view class="header-top">
				<text class="main-title">
					{{ lang.isEnglish ? 'Overview' : '总览' }}
				</text>
				<view class="header-actions">
					<view class="theme-toggle" @click="store.switchBackgroundTheme()">
						<text class="theme-text">{{ currentThemeName }}</text>
					</view>
					<view class="lang-toggle" @click="lang.isEnglish = !lang.isEnglish">
						<text class="lang-text">{{ lang.isEnglish ? '中' : 'EN' }}</text>
					</view>
				</view>
			</view>
			<text class="sub-title">
				{{ lang.isEnglish ? 'Real-time monitoring of environment' : '环境实时监控' }}
			</text>
		</view>

		<!-- 1. ESP32 设备状态卡片 (Uiverse.io 风格) -->
		<view class="status-card" :class="{ pressed: isCardPressed }" @tap="onCardTap" @touchstart="isCardPressed = true" @touchend="isCardPressed = false">
			<view class="status-card-img" :class="{ online: store.status.esp32Online, pressed: isCardPressed }">
				<view class="status-dot" :class="{ online: store.status.esp32Online }"></view>
			</view>
			<view class="status-card-textBox">
				<view class="status-card-textContent">
					<text class="status-card-title">{{ lang.isEnglish ? 'ESP32 Status' : 'ESP32 状态' }}</text>
					<text class="status-card-time">{{ store.status.lastSeenText }}</text>
				</view>
				<text class="status-card-desc" :class="{ online: store.status.esp32Online }">
					{{ store.status.esp32Online 
						? (lang.isEnglish ? 'Online - Device Connected' : '在线 - 设备已连接') 
						: (lang.isEnglish ? 'Offline - Device Disconnected' : '离线 - 设备断开') }}
				</text>
			</view>
		</view>

		<!-- 2. 传感器网格区域 (渐变背景衬托 Liquid Glass) -->
		<view class="sensor-grid-wrapper">
			<view class="sensor-grid">
			<!-- 温度 -->
			<SensorCard 
				:title="lang.isEnglish ? 'Temperature' : '温度'"
				:value="store.sensors.temperature" unit="℃" 
				icon="temp" color="#22c55e" :time="store.status.lastSeenText" 
			/>
			<!-- 湿度 -->
			<SensorCard 
				:title="lang.isEnglish ? 'Humidity' : '湿度'"
				:value="store.sensors.humidity" unit="%" 
				icon="hum" color="#3b82f6" :time="store.status.lastSeenText" 
			/>
			<!-- 二氧化碳 -->
			<SensorCard 
				:title="lang.isEnglish ? 'CO2 Level' : '二氧化碳浓度'"
				:value="store.sensors.CO2" unit="ppm" 
				icon="co2" color="#0ea5e9" :time="store.status.lastSeenText" 
			/>
			<!-- 光照强度 -->
			<SensorCard 
				:title="lang.isEnglish ? 'Light Intensity' : '光照强度'"
				:value="store.sensors.lux" unit="Lux" 
				icon="lux" color="#f59e0b" :time="store.status.lastSeenText" 
			/>
			<!-- 氨气 (新增，匹配商用图) -->
			<SensorCard 
				:title="lang.isEnglish ? 'NH3 (Ammonia)' : '氨气 (NH3)'"
				:value="store.sensors.NH3" unit="ppm" 
				icon="nh3" color="#f43f5e" :time="store.status.lastSeenText" 
			/>
			<!-- 土壤湿度 (新增) -->
			<SensorCard 
				:title="lang.isEnglish ? 'Soil Moisture' : '土壤湿度'"
				:value="store.sensors.soilHumidity" unit="%" 
				icon="soil" color="#8b5cf6" :time="store.status.lastSeenText" 
			/>
			</view>
		</view>

		<!-- 3. 蚕数据区域 -->
		<view class="silkworm-wrapper">
			<view class="silkworm-card">
				<!-- Liquid Glass 高光层 -->
				<view class="sw-glass-shine"></view>
				<view class="sw-header">
					<view class="sw-title-row">
						<view class="sw-icon-box">
							<image src="/static/icons/silk.png" mode="aspectFit" class="sw-icon-img"></image>
						</view>
						<text class="sw-title">{{ lang.isEnglish ? 'Silkworm Status' : '蚕状态监测' }}</text>
					</view>
				</view>
			<view class="sw-grid">
				<view class="sw-item">
					<text class="sw-label">{{ lang.isEnglish ? 'Total' : '总数' }}</text>
					<text class="sw-value sw-value-total">{{ store.sensors.Silkworm_Total }}</text>
				</view>
				<view class="sw-item">
					<text class="sw-label">{{ lang.isEnglish ? 'Healthy' : '健康' }}</text>
					<text class="sw-value sw-value-healthy">{{ store.sensors.Silkworm_Healthy }}</text>
				</view>
				<view class="sw-item">
					<text class="sw-label">{{ lang.isEnglish ? 'Sick' : '病蚕' }}</text>
					<text class="sw-value sw-value-sick">{{ store.sensors.Silkworm_Sick }}</text>
				</view>
				<view class="sw-item">
					<text class="sw-label">{{ lang.isEnglish ? 'Dormant' : '眠期' }}</text>
					<text class="sw-value sw-value-sleep">{{ store.sensors.Silkworm_Sleep }}</text>
				</view>
			</view>
		</view>
		</view>
		<AlertPopup />
	</view>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { deviceStore as store } from '@/store/device';
import SensorCard from '@/components/SensorCard.vue';
import { langStore as lang } from '@/store/lang';
import AlertPopup from '@/components/AlertPopup.vue';

const statusBarHeight = ref(20);
const sysInfo = uni.getSystemInfoSync();
statusBarHeight.value = sysInfo.statusBarHeight || 20;

// 卡片点击状态（模拟 hover 效果）
const isCardPressed = ref(false);
const onCardTap = () => {
	store.fetchOnlineStatus();
};

// 当前主题名称
const currentThemeName = computed(() => {
	const theme = store.backgroundTheme.themes[store.backgroundTheme.current];
	return lang.isEnglish ? theme.nameEn : theme.name;
});

// 动态背景样式
const backgroundStyle = computed(() => {
	return store.getCurrentBackgroundStyle();
});

const updateLang = () => {
	const isEn = lang.isEnglish;
	uni.setTabBarItem({ index: 0, text: isEn ? 'Overview' : '总览' });
	uni.setTabBarItem({ index: 1, text: isEn ? 'Controls' : '控制' });
	uni.setTabBarItem({ index: 2, text: isEn ? 'History' : '历史' });
	uni.setTabBarItem({ index: 3, text: isEn ? 'Logs' : '日志' });
};
updateLang();
watch(() => lang.isEnglish, updateLang);
</script>

<style lang="scss">
.page-container {
	padding: 60rpx 30rpx 40rpx;
	min-height: 100vh;
}

.header-actions {
	display: flex;
	align-items: center;
	gap: 12rpx;
}

.theme-toggle {
	width: 100rpx;
	height: 44rpx;
	border-radius: 22rpx;
	background: rgba(26, 26, 46, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
}

.theme-text {
	font-size: 20rpx;
	font-weight: 600;
	color: rgba(26, 26, 46, 0.7);
}

.header-section {
	margin-bottom: 16rpx;
	background: rgba(255, 255, 255, 0.5);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	border-radius: 24rpx;
	padding: 20rpx 28rpx;
	box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
	border: 1rpx solid rgba(255, 255, 255, 0.3);
}
.header-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 6rpx;
}
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
.lang-toggle {
	width: 88rpx;
	height: 44rpx;
	border-radius: 22rpx;
	background: rgba(0, 0, 0, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
}
.lang-text {
	font-size: 22rpx;
	font-weight: 600;
	color: #475569;
}
/* ESP32 状态卡片 */
.status-card {
	width: 100%;
	height: 140rpx;
	background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
	border-radius: 40rpx;
	display: flex;
	align-items: center;
	justify-content: flex-start;
	margin-bottom: 20rpx;
	transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.2);
	&.pressed { transform: scale(1.05); }
	&:active {
		transform: translateY(-6rpx) scale(1.02);
		box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.3);
	}
}
.status-card-img {
	width: 100rpx;
	height: 100rpx;
	margin-left: 20rpx;
	border-radius: 20rpx;
	background: linear-gradient(#d7cfcf, #9198e5);
	display: flex;
	align-items: center;
	justify-content: center;
	transition: background 0.5s ease-in-out;
	&.online { background: linear-gradient(#10b981, #9198e5); }
	&.pressed { background: linear-gradient(#9198e5, #712020); }
}
.status-dot {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #ef4444;
	box-shadow: 0 0 16rpx rgba(239, 68, 68, 0.6);
	transition: all 0.3s;
	&.online {
		background: #10b981;
		box-shadow: 0 0 16rpx rgba(16, 185, 129, 0.6);
	}
}
.status-card-textBox {
	width: calc(100% - 180rpx);
	margin-left: 20rpx;
	color: #fff;
}
.status-card-textContent {
	display: flex;
	align-items: center;
	justify-content: space-between;
}
.status-card-title { font-size: 32rpx; font-weight: bold; color: #fff; }
.status-card-time { font-size: 20rpx; color: #94a3b8; }
.status-card-desc {
	font-size: 24rpx; font-weight: lighter; color: #ef4444; margin-top: 8rpx; display: block;
	&.online { color: #10b981; }
}
/* 传感器区域 - 毛玻璃效果 */
.sensor-grid-wrapper {
	background: rgba(255, 255, 255, 0.15);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 32rpx;
	padding: 24rpx;
	margin-bottom: 20rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.2);
	box-shadow: 
		0 4rpx 24rpx rgba(0, 0, 0, 0.08),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
}
.sensor-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 20rpx;
}
/* 蚕数据区域 - 毛玻璃效果 */
.silkworm-wrapper {
	background: rgba(255, 255, 255, 0.15);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 32rpx;
	padding: 24rpx;
	margin-top: 20rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.2);
	box-shadow: 
		0 4rpx 24rpx rgba(0, 0, 0, 0.08),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
}
/* 蚕数据卡片 */
.silkworm-card {
	position: relative;
	overflow: hidden;
	background: linear-gradient(135deg, rgba(255, 255, 255, 0.65) 0%, rgba(255, 255, 255, 0.35) 100%);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 28rpx;
	padding: 28rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04), 0 8rpx 24rpx rgba(0, 0, 0, 0.06),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.8), inset 0 -1rpx 0 rgba(0, 0, 0, 0.05);
	border: 1rpx solid rgba(255, 255, 255, 0.5);
	transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease;
	&:active {
		transform: scale(0.95);
		box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.03), 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
	}
}
.sw-glass-shine {
	position: absolute;
	top: 0; left: 0; right: 0;
	height: 50%;
	background: linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0) 100%);
	border-radius: 28rpx 28rpx 0 0;
	pointer-events: none;
}
.sw-header { margin-bottom: 24rpx; position: relative; z-index: 1; }
.sw-title-row { display: flex; align-items: center; gap: 12rpx; }
.sw-icon-box {
	width: 68rpx; height: 68rpx; border-radius: 20rpx;
	background: rgba(245, 158, 11, 0.2);
	display: flex; align-items: center; justify-content: center;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1), inset 0 1rpx 0 rgba(255, 255, 255, 0.5);
}
.sw-icon-img { width: 38rpx; height: 38rpx; }
.sw-title {
	font-size: 28rpx; font-weight: 700; color: rgba(0, 0, 0, 0.85);
	text-shadow: 0 1rpx 3rpx rgba(255, 255, 255, 0.9);
}
.sw-grid {
	display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16rpx;
	position: relative; z-index: 1;
}
.sw-item { text-align: center; padding: 16rpx 0; }
.sw-label {
	font-size: 22rpx; color: rgba(0, 0, 0, 0.55); display: block; margin-bottom: 8rpx;
	text-shadow: 0 1rpx 2rpx rgba(255, 255, 255, 0.9);
}
.sw-value {
	font-size: 40rpx; font-weight: 700;
	text-shadow: 0 2rpx 4rpx rgba(255, 255, 255, 0.6);
}
.sw-value-total { color: rgba(0, 0, 0, 0.85); }
.sw-value-healthy { color: #059669; }
.sw-value-sick { color: #dc2626; }
.sw-value-sleep { color: #d97706; }
/* 流动渐变背景动画 */
@keyframes gradientFlow {
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
}
</style>
