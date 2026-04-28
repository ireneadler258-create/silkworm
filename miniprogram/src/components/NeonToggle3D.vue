<template>
	<view class="neon-toggle" :class="{ active: modelValue }" @click="handleToggle">
		<!-- 底部发光层 -->
		<view class="glow-layer"></view>
		<!-- 开关轨道 -->
		<view class="toggle-track">
			<!-- 滑块 -->
			<view class="toggle-thumb"></view>
		</view>
	</view>
</template>

<script setup lang="ts">
const props = defineProps<{
	modelValue: boolean;
}>();

const emit = defineEmits<{
	(e: 'update:modelValue', value: boolean): void;
}>();

const handleToggle = () => {
	emit('update:modelValue', !props.modelValue);
};
</script>

<style scoped>
.neon-toggle {
	position: relative;
	display: inline-block;
	/* 轻微倾斜 - 3D 感 */
	transform: rotate(-1.5deg);
	animation: float 2.5s ease-in-out infinite;
}

/* 持续上下浮动 - 更明显 */
@keyframes float {
	0%, 100% {
		transform: rotate(-1.5deg) translateY(0) scale(1);
	}
	25% {
		transform: rotate(-2deg) translateY(-8rpx) scale(1.02);
	}
	50% {
		transform: rotate(-1.5deg) translateY(-12rpx) scale(1.03);
	}
	75% {
		transform: rotate(-1deg) translateY(-8rpx) scale(1.02);
	}
}

/* 底部彩色弥散发光 */
.glow-layer {
	position: absolute;
	bottom: -8rpx;
	left: 50%;
	transform: translateX(-50%);
	width: 85%;
	height: 24rpx;
	border-radius: 50%;
	/* 粉紫渐变 - 未选中 */
	background: linear-gradient(90deg, 
		rgba(255, 100, 180, 0.5), 
		rgba(200, 100, 255, 0.5), 
		rgba(150, 120, 255, 0.5)
	);
	filter: blur(12rpx);
	opacity: 0.7;
	transition: all 0.4s ease;
}

/* 选中 - 青蓝发光 */
.neon-toggle.active .glow-layer {
	background: linear-gradient(90deg, 
		rgba(100, 255, 220, 0.5), 
		rgba(100, 200, 255, 0.5), 
		rgba(100, 150, 255, 0.5)
	);
	opacity: 0.9;
	filter: blur(16rpx);
}

/* 开关轨道 */
.toggle-track {
	width: 110rpx;
	height: 58rpx;
	border-radius: 29rpx;
	/* 毛玻璃 - 未选中 */
	background: rgba(255, 255, 255, 0.25);
	backdrop-filter: blur(8px);
	-webkit-backdrop-filter: blur(8px);
	border: 2rpx solid rgba(255, 255, 255, 0.3);
	box-shadow: 
		inset 0 2rpx 8rpx rgba(0, 0, 0, 0.08),
		0 4rpx 12rpx rgba(0, 0, 0, 0.06);
	position: relative;
	transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 选中 - 深色轨道 */
.neon-toggle.active .toggle-track {
	background: rgba(20, 20, 40, 0.75);
	border-color: rgba(100, 220, 255, 0.35);
	box-shadow: 
		inset 0 2rpx 10rpx rgba(0, 0, 0, 0.25),
		0 0 18rpx rgba(100, 220, 255, 0.25);
}

/* 滑块 */
.toggle-thumb {
	width: 48rpx;
	height: 48rpx;
	border-radius: 50%;
	position: absolute;
	left: 5rpx;
	top: 50%;
	transform: translateY(-50%);
	/* 粉紫渐变 - 未选中 */
	background: linear-gradient(135deg, 
		#ff7eb3 0%, 
		#d47cff 50%, 
		#b47aff 100%
	);
	box-shadow: 
		0 0 12rpx rgba(255, 126, 179, 0.5),
		0 0 24rpx rgba(212, 124, 255, 0.35),
		0 3rpx 8rpx rgba(0, 0, 0, 0.18),
		inset 0 -2rpx 5rpx rgba(0, 0, 0, 0.15),
		inset 0 2rpx 5rpx rgba(255, 255, 255, 0.35);
	transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 选中 - 青蓝渐变 */
.neon-toggle.active .toggle-thumb {
	left: calc(100% - 53rpx);
	background: linear-gradient(135deg, 
		#5fffd0 0%, 
		#5cd4ff 50%, 
		#5ca0ff 100%
	);
	box-shadow: 
		0 0 12rpx rgba(95, 255, 208, 0.5),
		0 0 24rpx rgba(92, 212, 255, 0.35),
		0 3rpx 8rpx rgba(0, 0, 0, 0.18),
		inset 0 -2rpx 5rpx rgba(0, 0, 0, 0.15),
		inset 0 2rpx 5rpx rgba(255, 255, 255, 0.35);
}

/* 滑块内光晕 */
.toggle-thumb::after {
	content: '';
	position: absolute;
	top: 30%;
	left: 30%;
	width: 40%;
	height: 40%;
	border-radius: 50%;
	background: rgba(255, 255, 255, 0.5);
	filter: blur(3rpx);
}
</style>
