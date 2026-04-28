<template>
	<view class="sick-card" :class="{ 'has-image': hasImage }">
		<view class="sick-header">
			<view class="sick-title-row">
				<image src="/static/icons/silk.png" mode="aspectFit" class="sick-icon" />
				<text class="sick-title">{{ lang.isEnglish ? 'Sick Silkworm Alert' : '病蚕警报' }}</text>
			</view>
			<view v-if="hasImage" class="sick-badge">
				<text class="badge-text">{{ sickCount }}</text>
			</view>
		</view>

		<!-- 图片区域 -->
		<view v-if="hasImage" class="sick-image-wrap" @tap="previewImage">
			<image
				:src="imagePath"
				mode="aspectFit"
				class="sick-image"
				@error="onImageError"
			/>
			<view class="image-overlay">
				<text class="overlay-text">{{ lang.isEnglish ? 'Tap to view' : '点击查看' }}</text>
			</view>
		</view>

		<!-- 无图片状态 -->
		<view v-else class="sick-empty">
			<text class="empty-text">{{ lang.isEnglish ? 'No sick silkworm detected' : '暂无病蚕检测' }}</text>
		</view>

		<!-- 底部信息 -->
		<view class="sick-footer">
			<view class="history-btn" @tap="goToHistory">
				<text class="history-text">{{ lang.isEnglish ? 'View History' : '查看历史' }} ({{ recordCount }})</text>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { deviceStore as store } from '@/store/device';
import { langStore as lang } from '@/store/lang';

const hasImage = computed(() => !!store._currentSickImagePath);
const imagePath = computed(() => store._currentSickImagePath);
const sickCount = computed(() => store.sensors.Silkworm_Sick);
const recordCount = computed(() => store.sickImageRecords.length);

const formattedTime = computed(() => {
	if (!store.status.lastSeen) return '--';
	const d = new Date(store.status.lastSeen);
	return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`;
});

const previewImage = () => {
	if (!imagePath.value) return;
	uni.previewImage({
		urls: [imagePath.value],
		current: imagePath.value
	});
};

const goToHistory = () => {
	uni.navigateTo({
		url: '/pages/sick-history/index'
	});
};

const onImageError = () => {
	console.warn('[SickAlertCard] Image load error');
};
</script>

<style scoped>
.sick-card {
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
}

.sick-card.has-image {
	border-color: rgba(239, 68, 68, 0.4);
	box-shadow: 
		0 4rpx 20rpx rgba(0, 0, 0, 0.08),
		0 0 25rpx 3rpx rgba(239, 68, 68, 0.25);
	animation: sickPulse 2s ease-in-out infinite;
}

@keyframes sickPulse {
	0%, 100% { 
		box-shadow: 
			0 4rpx 20rpx rgba(0, 0, 0, 0.08),
			0 0 25rpx 3rpx rgba(239, 68, 68, 0.25);
	}
	50% { 
		box-shadow: 
			0 4rpx 20rpx rgba(0, 0, 0, 0.08),
			0 0 35rpx 5rpx rgba(239, 68, 68, 0.4);
	}
}

.sick-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.sick-title-row {
	display: flex;
	align-items: center;
	gap: 12rpx;
}

.sick-icon {
	width: 40rpx;
	height: 40rpx;
}

.sick-title {
	font-size: 28rpx;
	font-weight: 700;
	color: #1a1a2e;
}

.sick-badge {
	background: rgba(220, 38, 38, 0.8);
	padding: 4rpx 16rpx;
	border-radius: 999rpx;
}

.badge-text {
	font-size: 22rpx;
	font-weight: 600;
	color: #fff;
}

.sick-image-wrap {
	position: relative;
	border-radius: 16rpx;
	overflow: hidden;
	margin-bottom: 20rpx;
	background: rgba(0, 0, 0, 0.2);
}

.sick-image {
	width: 100%;
	height: 360rpx;
	display: block;
}

.image-overlay {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	background: linear-gradient(transparent, rgba(0,0,0,0.5));
	padding: 16rpx;
	text-align: center;
}

.overlay-text {
	font-size: 22rpx;
	color: #fff;
}

.sick-empty {
	padding: 40rpx;
	text-align: center;
	background: rgba(255, 255, 255, 0.1);
	border-radius: 16rpx;
	margin-bottom: 20rpx;
	border: 1rpx dashed rgba(255, 255, 255, 0.2);
}

.empty-text {
	font-size: 24rpx;
	color: rgba(26, 26, 46, 0.5);
}

.sick-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding-top: 16rpx;
	border-top: 1rpx solid rgba(26, 26, 46, 0.1);
}

.sick-info {
	flex: 1;
}

.info-label {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.55);
	display: block;
	margin-bottom: 4rpx;
}

.info-value {
	font-size: 26rpx;
	font-weight: 600;
	color: #1a1a2e;
}

.history-btn {
	background: rgba(26, 26, 46, 0.1);
	padding: 12rpx 20rpx;
	border-radius: 12rpx;
	flex-shrink: 0;
	border: 1rpx solid rgba(26, 26, 46, 0.15);
}

.history-text {
	font-size: 22rpx;
	color: rgba(26, 26, 46, 0.7);
	font-weight: 500;
}
</style>
