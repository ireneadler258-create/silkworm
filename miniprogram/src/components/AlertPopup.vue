<template>
	<view v-if="store.alertPopup.show" class="popup-mask" @tap="onClose">
		<view class="popup-card" @tap.stop>
			<!-- 顶部色条 -->
			<view class="popup-top-bar" :class="store.alertPopup.severity"></view>

			<!-- 图标 -->
			<view class="popup-icon-wrap" :class="store.alertPopup.severity">
				<text class="popup-icon">{{ store.alertPopup.severity === 'severe' ? '!' : 'i' }}</text>
			</view>

			<!-- 标题 -->
			<text class="popup-title">{{ store.alertPopup.severity === 'severe' ? '严重告警' : '告警提醒' }}</text>
			<text class="popup-desc">{{ store.alertPopup.title }}</text>

			<!-- 分隔线 -->
			<view class="popup-divider"></view>

			<!-- 处理建议 -->
			<view class="popup-suggestion">
				<text class="sug-label">处理建议</text>
				<text class="sug-text">{{ store.alertPopup.suggestion }}</text>
			</view>

			<!-- 按钮 -->
			<view class="popup-btn" :class="store.alertPopup.severity" @tap="onClose">
				<text class="popup-btn-text">我知道了</text>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { deviceStore as store } from '@/store/device';

const onClose = () => {
	store.hideAlertPopup();
};

// 轻微告警 5 秒自动关闭
watch(() => store.alertPopup.show, (val) => {
	if (val && !store.alertPopup.isPersistent) {
		setTimeout(() => {
			if (store.alertPopup.show && !store.alertPopup.isPersistent) {
				store.hideAlertPopup();
			}
		}, 5000);
	}
});
</script>

<style scoped>
.popup-mask {
	position: fixed;
	top: 0; left: 0; right: 0; bottom: 0;
	background: rgba(15, 23, 42, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 99999;
	padding: 48rpx;
}
.popup-card {
	width: 100%;
	background: #fff;
	border-radius: 32rpx;
	padding: 0;
	padding-bottom: 36rpx;
	overflow: hidden;
	box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.2);
	display: flex;
	flex-direction: column;
	align-items: center;
}
.popup-top-bar {
	width: 100%;
	height: 8rpx;
	&.light { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
	&.severe { background: linear-gradient(90deg, #ef4444, #f87171); }
}
.popup-icon-wrap {
	width: 96rpx;
	height: 96rpx;
	border-radius: 48rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-top: 36rpx;
	margin-bottom: 20rpx;
	&.light { background: linear-gradient(135deg, #fef3c7, #fde68a); }
	&.severe { background: linear-gradient(135deg, #fee2e2, #fecaca); }
}
.popup-icon {
	font-size: 44rpx;
	font-weight: 800;
	&.light { color: #f59e0b; }
	&.severe { color: #ef4444; }
}
.popup-title {
	font-size: 34rpx;
	font-weight: 800;
	color: #0f172a;
	margin-bottom: 12rpx;
}
.popup-desc {
	font-size: 26rpx;
	color: #475569;
	text-align: center;
	padding: 0 36rpx;
	line-height: 1.6;
	margin-bottom: 24rpx;
}
.popup-divider {
	width: 80%;
	height: 1rpx;
	background: #f1f5f9;
	margin-bottom: 24rpx;
}
.popup-suggestion {
	width: 85%;
	background: #f8fafc;
	border-radius: 16rpx;
	padding: 20rpx 24rpx;
	margin-bottom: 28rpx;
}
.sug-label {
	font-size: 22rpx;
	color: #94a3b8;
	font-weight: 600;
	display: block;
	margin-bottom: 8rpx;
}
.sug-text {
	font-size: 24rpx;
	color: #475569;
	line-height: 1.6;
}
.popup-btn {
	width: 85%;
	padding: 22rpx 0;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	&.light { background: linear-gradient(135deg, #f59e0b, #d97706); }
	&.severe { background: linear-gradient(135deg, #ef4444, #dc2626); }
}
.popup-btn-text {
	font-size: 28rpx;
	font-weight: 700;
	color: #fff;
}
</style>