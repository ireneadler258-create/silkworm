<template>
	<view class="s-card">
		<!-- Liquid Glass 高光层 -->
		<view class="s-glass-shine"></view>
		<view class="s-header">
			<view class="s-icon-box" :style="{ background: iconBg }">
				<image 
					:src="'/static/icons/' + icon + '.png'" 
					mode="aspectFit" 
					class="s-img"
				></image>
			</view>
			<view class="s-badge">
				<view class="s-dot" :style="{ background: color }"></view>
				<text class="s-time">{{ time }}</text>
			</view>
		</view>
		<text class="s-label">{{ title }}</text>
		<view class="s-value-row">
			<text class="s-value" :style="{ color: color }">{{ formatVal(value) }}</text>
			<text class="s-unit">{{ unit }}</text>
		</view>
	</view>
</template>

<script setup>
import { computed } from 'vue';
const props = defineProps(['title', 'value', 'unit', 'icon', 'color', 'time']);
const formatVal = (v) => (typeof v === 'number' ? v.toFixed(1) : v);

function hexAlpha(hex, alpha) {
	const r = parseInt(hex.slice(1, 3), 16);
	const g = parseInt(hex.slice(3, 5), 16);
	const b = parseInt(hex.slice(5, 7), 16);
	return `rgba(${r},${g},${b},${alpha})`;
}

const iconBg = computed(() => props.color ? hexAlpha(props.color, 0.1) : '#f1f5f9');
</script>

<style scoped>
.s-card {
	position: relative;
	overflow: hidden;
	background: linear-gradient(135deg, rgba(255, 255, 255, 0.65) 0%, rgba(255, 255, 255, 0.35) 100%);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 28rpx;
	padding: 28rpx;
	margin-bottom: 10rpx;
	box-shadow: 
		0 2rpx 8rpx rgba(0, 0, 0, 0.04),
		0 8rpx 24rpx rgba(0, 0, 0, 0.06),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.8),
		inset 0 -1rpx 0 rgba(0, 0, 0, 0.05);
	border: 1rpx solid rgba(255, 255, 255, 0.5);
	transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease;
}
.s-card:active {
	transform: scale(0.95);
	box-shadow: 0 1rpx 4rpx rgba(0, 0, 0, 0.03), 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
}
.s-glass-shine {
	position: absolute;
	top: 0; left: 0; right: 0;
	height: 50%;
	background: linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0) 100%);
	border-radius: 28rpx 28rpx 0 0;
	pointer-events: none;
}
.s-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24rpx;
	position: relative;
	z-index: 1;
}
.s-icon-box {
	width: 68rpx;
	height: 68rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08), inset 0 1rpx 0 rgba(255, 255, 255, 0.6);
}
.s-img { width: 38rpx; height: 38rpx; }
.s-badge { display: flex; align-items: center; gap: 8rpx; }
.s-dot { width: 12rpx; height: 12rpx; border-radius: 6rpx; }
.s-time { 
	font-size: 20rpx; 
	color: rgba(0, 0, 0, 0.5); 
	text-shadow: 0 1rpx 2rpx rgba(255, 255, 255, 0.8); 
}
.s-label {
	font-size: 24rpx; 
	color: rgba(0, 0, 0, 0.6); 
	display: block; 
	margin-bottom: 8rpx;
	position: relative; 
	z-index: 1; 
	text-shadow: 0 1rpx 2rpx rgba(255, 255, 255, 0.8);
}
.s-value {
	font-size: 44rpx; 
	font-weight: 700;
	color: rgba(0, 0, 0, 0.85);
	position: relative; 
	z-index: 1; 
	text-shadow: 0 2rpx 4rpx rgba(255, 255, 255, 0.6);
}
.s-unit { 
	font-size: 22rpx; 
	color: rgba(0, 0, 0, 0.5); 
	margin-left: 4rpx; 
	position: relative; 
	z-index: 1; 
}
</style>
