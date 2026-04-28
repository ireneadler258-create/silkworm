<template>
	<view class="page-container" :style="backgroundStyle">
		<view class="header-section" :style="{ paddingTop: statusBarHeight + 'px' }">
			<text class="main-title">{{ lang.isEnglish ? 'Sick Silkworm History' : '病蚕历史记录' }}</text>
			<text class="sub-title">{{ lang.isEnglish ? 'Historical sick silkworm detections' : '历史病蚕检测记录' }}</text>
		</view>

		<!-- 统计概览 -->
		<view class="stats-row">
			<view class="stat-card">
				<text class="stat-value">{{ records.length }}</text>
				<text class="stat-label">{{ lang.isEnglish ? 'Total Records' : '总记录数' }}</text>
			</view>
			<view class="stat-card">
				<text class="stat-value">{{ totalSick }}</text>
				<text class="stat-label">{{ lang.isEnglish ? 'Total Sick' : '累计病蚕' }}</text>
			</view>
		</view>

		<!-- 操作按钮 -->
		<view class="action-row" v-if="records.length > 0">
			<view class="clear-btn" @tap="clearAll">
				<text class="clear-text">{{ lang.isEnglish ? 'Clear All' : '清空全部' }}</text>
			</view>
		</view>

		<!-- 记录列表 -->
		<view v-if="records.length === 0" class="empty-state">
			<text class="empty-text">{{ lang.isEnglish ? 'No records yet' : '暂无记录' }}</text>
		</view>

		<view v-for="record in records" :key="record.id" class="record-card">
			<view class="record-image-wrap" @tap="previewImage(record.localPath || record.url)">
				<image
					:src="record.localPath || record.url"
					mode="aspectFill"
					class="record-image"
				/>
			</view>
			<view class="record-info">
				<view class="record-header">
					<text class="record-count">{{ record.sickCount }} {{ lang.isEnglish ? 'sick' : '只病蚕' }}</text>
					<view class="delete-btn" @tap="deleteRecord(record.id)">
						<text class="delete-text">{{ lang.isEnglish ? 'Delete' : '删除' }}</text>
					</view>
				</view>
				<text class="record-time">{{ formatTime(record.timestamp) }}</text>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { deviceStore as store } from '@/store/device';
import { langStore as lang } from '@/store/lang';

const statusBarHeight = ref(20);
const sysInfo = uni.getSystemInfoSync();
statusBarHeight.value = sysInfo.statusBarHeight || 20;

// 动态背景样式
const backgroundStyle = computed(() => store.getCurrentBackgroundStyle());

const records = computed(() => store.sickImageRecords);

const totalSick = computed(() => {
	return records.value.reduce((sum, r) => sum + r.sickCount, 0);
});

const formatTime = (ts: number) => {
	const d = new Date(ts);
	const date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
	const time = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`;
	return `${date} ${time}`;
};

const previewImage = (url: string) => {
	if (!url) return;
	uni.previewImage({
		urls: records.value.map(r => r.localPath || r.url),
		current: url
	});
};

const deleteRecord = (id: string) => {
	uni.showModal({
		title: lang.isEnglish ? 'Confirm Delete' : '确认删除',
		content: lang.isEnglish ? 'Delete this record?' : '确定删除此记录？',
		success: (res) => {
			if (res.confirm) {
				store.deleteSickImageRecord(id);
			}
		}
	});
};

const clearAll = () => {
	uni.showModal({
		title: lang.isEnglish ? 'Confirm Clear' : '确认清空',
		content: lang.isEnglish ? 'Clear all records?' : '确定清空所有记录？',
		success: (res) => {
			if (res.confirm) {
				store.clearSickImageRecords();
			}
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

/* 流动渐变背景动画 */
@keyframes gradientFlow {
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
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

.stats-row {
	display: flex;
	gap: 20rpx;
	margin-bottom: 24rpx;
}

.stat-card {
	flex: 1;
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(16px);
	-webkit-backdrop-filter: blur(16px);
	border-radius: 20rpx;
	padding: 24rpx;
	text-align: center;
	border: 2rpx solid rgba(255, 255, 255, 0.25);
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.stat-value {
	font-size: 48rpx;
	font-weight: 800;
	color: #1a1a2e;
	display: block;
}

.stat-label {
	font-size: 22rpx;
	color: rgba(26, 26, 46, 0.65);
	margin-top: 8rpx;
}

.action-row {
	display: flex;
	justify-content: flex-end;
	margin-bottom: 20rpx;
}

.clear-btn {
	background: rgba(239, 68, 68, 0.25);
	backdrop-filter: blur(10px);
	-webkit-backdrop-filter: blur(10px);
	padding: 12rpx 24rpx;
	border-radius: 12rpx;
	border: 1rpx solid rgba(239, 68, 68, 0.3);
}

.clear-text {
	font-size: 24rpx;
	color: #fca5a5;
	font-weight: 600;
}

.empty-state {
	padding: 80rpx 0;
	text-align: center;
}

.empty-text {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.5);
}

.record-card {
	display: flex;
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 20rpx;
	padding: 20rpx;
	margin-bottom: 16rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.2);
	box-shadow: 
		0 4rpx 16rpx rgba(0, 0, 0, 0.08),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.4);
	transition: transform 0.2s ease;
	&:active {
		transform: scale(0.98);
	}
}

.record-image-wrap {
	width: 160rpx;
	height: 160rpx;
	border-radius: 16rpx;
	overflow: hidden;
	flex-shrink: 0;
	border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.record-image {
	width: 100%;
	height: 100%;
}

.record-info {
	flex: 1;
	margin-left: 20rpx;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}

.record-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.record-count {
	font-size: 28rpx;
	font-weight: 700;
	color: #1a1a2e;
}

.delete-btn {
	background: rgba(255, 255, 255, 0.15);
	padding: 8rpx 16rpx;
	border-radius: 8rpx;
	border: 1rpx solid rgba(255, 255, 255, 0.2);
}

.delete-text {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.7);
}

.record-time {
	font-size: 22rpx;
	color: rgba(26, 26, 46, 0.55);
}
</style>
