<template>
	<view class="cube-container">
		<view class="cube-scene">
			<view class="cube-stack">
				<view 
					v-for="(cube, i) in cubes" 
					:key="i"
					class="cube-wrapper"
					:style="{ animationDelay: cube.delay + 's' }"
				>
					<view class="cube" :style="{ '--cube-color': cube.color, '--cube-light': cube.light, '--cube-dark': cube.dark }">
						<view class="cube-face cube-front"></view>
						<view class="cube-face cube-top"></view>
						<view class="cube-face cube-right"></view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
// 6 个立方体配置：颜色从红到黄渐变
const cubes = [
	{ color: '#ef4444', light: '#fca5a5', dark: '#dc2626', delay: 0 },      // 红
	{ color: '#f472b6', light: '#f9a8d4', dark: '#db2777', delay: 0.3 },    // 粉红
	{ color: '#fb923c', light: '#fdba74', dark: '#ea580c', delay: 0.6 },    // 橙红
	{ color: '#f97316', light: '#fdba74', dark: '#c2410c', delay: 0.9 },    // 橙
	{ color: '#fbbf24', light: '#fde047', dark: '#d97706', delay: 1.2 },    // 黄橙
	{ color: '#facc15', light: '#fef08a', dark: '#ca8a04', delay: 1.5 },    // 黄
];
</script>

<style scoped>
.cube-container {
	width: 100%;
	height: 400rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	perspective: 800rpx;
}

.cube-scene {
	transform-style: preserve-3d;
	transform: rotateX(-35deg) rotateY(-45deg);
}

.cube-stack {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	align-items: center;
}

/* 立方体容器 - 缩放动画 */
.cube-wrapper {
	animation: cubeScale 3.6s cubic-bezier(0.34, 1.56, 0.64, 1) infinite;
}

/* 缩放动画 - 弹性效果 */
@keyframes cubeScale {
	0%, 30%, 100% {
		transform: scale(1);
	}
	15% {
		transform: scale(0.5);
	}
}

/* 立方体基础 */
.cube {
	width: 60rpx;
	height: 60rpx;
	position: relative;
	transform-style: preserve-3d;
}

/* 立方体面 */
.cube-face {
	position: absolute;
	width: 60rpx;
	height: 60rpx;
}

/* 正面 - 基准颜色 */
.cube-front {
	background: var(--cube-color);
	transform: translateZ(30rpx);
}

/* 顶面 - 更亮 */
.cube-top {
	background: var(--cube-light);
	transform: rotateX(90deg) translateZ(30rpx);
}

/* 右侧面 - 更暗 */
.cube-right {
	background: var(--cube-dark);
	transform: rotateY(90deg) translateZ(30rpx);
}
</style>
