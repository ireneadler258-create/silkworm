<template>
	<view class="page-container" :style="backgroundStyle">
		<view class="header-section" :style="{ paddingTop: statusBarHeight + 'px' }">
			<view class="header-top">
				<text class="main-title">
					{{ lang.isEnglish ? 'Controls' : '设备控制' }}
				</text>
				<view 
					class="mode-toggle" 
					:class="{ manual: store.status.workMode }"
					@click="onToggleMode"
				>
					<text class="mode-toggle-text">
						{{ store.status.workMode
							? (lang.isEnglish ? 'MANUAL' : '手动')
							: (lang.isEnglish ? 'AUTO' : '自动') }}
					</text>
				</view>
			</view>
			<text class="sub-title">
				{{ lang.isEnglish ? 'Manual and Automatic Adjustments' : '手动 / 自动调节执行器' }}
			</text>
		</view>

		<view class="control-list">
			<view
				class="ctrl-card"
				v-for="(val, key) in ctrlMap"
				:key="key"
				:class="{ active: store.controls[key] }"
				:style="{ '--theme-color': val.color }"
			>
				<view class="ctrl-top">
					<view class="ctrl-top-click" @click="toggleExpand(key)">
						<view
							class="ctrl-icon"
							:style="store.controls[key] ? { background: val.color, boxShadow: '0 8rpx 20rpx ' + val.color + '40' } : {}"
						>
							<image
								class="ctrl-icon-img"
								:src="val.icon"
								mode="aspectFit"
							/>
						</view>
						<view class="ctrl-name">
							<view class="name-row">
								<text class="title">
									{{ lang.isEnglish ? val.nameEn : val.nameZh }}
								</text>
								<view class="name-right">
									<text
										class="mode-tag"
										:class="{ manual: store.status.workMode }"
									>
										{{ store.status.workMode
											? (lang.isEnglish ? 'MANUAL' : '手动')
											: (lang.isEnglish ? 'AUTO' : '自动') }}
									</text>
									<text class="expand-arrow" :class="{ expanded: expandedKey === key }">›</text>
								</view>
							</view>
							<text class="status-text" :class="{ running: store.controls[key] }">
								{{ store.controls[key]
									? (lang.isEnglish ? 'Running' : '运行中')
									: (lang.isEnglish ? 'Stopped' : '已停止') }}
							</text>
						</view>
					</view>
				</view>

				<!-- 阈值调节面板：点击对应卡片展开 -->
				<view class="th-panel" v-if="expandedKey === key">
					<!-- 风扇：TempHighTh -->
					<view v-if="key === 'fanStatus'" class="th-group" @longpress="openNumberInput('TempHighTh', -40, 80)">
						<view class="th-row" @click="onRowTap('TempHighTh', -40, 80)">
							<text class="th-label">{{ lang.isEnglish ? 'Temp High Threshold' : '高温阈值' }}</text>
							<text class="th-value">{{ store.thresholds.TempHighTh }}</text>
						</view>
						<slider 
							:value="store.thresholds.TempHighTh"
							:min="-40" :max="80" :step="1"
							activeColor="#22c55e"
							@changing="onSliderChanging('TempHighTh', $event)"
							@change="onSliderChange('TempHighTh', $event)"
						/>
						<text class="th-hint">{{ lang.isEnglish ? 'Must be >= Temp Low' : '不得低于低温阈值' }}</text>
					</view>

					<!-- 加热器：TempLowTh -->
					<view v-else-if="key === 'heaterStatus'" class="th-group" @longpress="openNumberInput('TempLowTh', -40, 80)">
						<view class="th-row" @click="onRowTap('TempLowTh', -40, 80)">
							<text class="th-label">{{ lang.isEnglish ? 'Temp Low Threshold' : '低温阈值' }}</text>
							<text class="th-value">{{ store.thresholds.TempLowTh }}</text>
						</view>
						<slider 
							:value="store.thresholds.TempLowTh"
							:min="-40" :max="80" :step="1"
							activeColor="#f97316"
							@changing="onSliderChanging('TempLowTh', $event)"
							@change="onSliderChange('TempLowTh', $event)"
						/>
						<text class="th-hint">{{ lang.isEnglish ? 'Must be <= Temp High' : '不得高于高温阈值' }}</text>
					</view>

					<!-- 加湿器：HumLowTh / HumHighTh -->
					<view v-else-if="key === 'atomizerStatus'" class="th-group">
						<view class="th-row" @click="onRowTap('HumLowTh', 0, 100)" @longpress="openNumberInput('HumLowTh', 0, 100)">
							<text class="th-label">{{ lang.isEnglish ? 'Hum Low Threshold' : '湿度下限' }}</text>
							<text class="th-value">{{ store.thresholds.HumLowTh }}</text>
						</view>
						<slider 
							:value="store.thresholds.HumLowTh"
							:min="0" :max="100" :step="1"
							activeColor="#3b82f6"
							@changing="onSliderChanging('HumLowTh', $event)"
							@change="onSliderChange('HumLowTh', $event)"
						/>

						<view class="th-row" @click="onRowTap('HumHighTh', 0, 100)" @longpress="openNumberInput('HumHighTh', 0, 100)">
							<text class="th-label">{{ lang.isEnglish ? 'Hum High Threshold' : '湿度上限' }}</text>
							<text class="th-value">{{ store.thresholds.HumHighTh }}</text>
						</view>
						<slider 
							:value="store.thresholds.HumHighTh"
							:min="0" :max="100" :step="1"
							activeColor="#0ea5e9"
							@changing="onSliderChanging('HumHighTh', $event)"
							@change="onSliderChange('HumHighTh', $event)"
						/>
						<text class="th-hint">{{ lang.isEnglish ? 'Low must be <= High' : '下限不得高于上限' }}</text>
					</view>

					<!-- LED：LuxLowTh / LuxHighTh -->
					<view v-else-if="key === 'lightStatus'" class="th-group">
						<view class="th-row" @click="onRowTap('LuxLowTh', 0, 65535)" @longpress="openNumberInput('LuxLowTh', 0, 65535)">
							<text class="th-label">{{ lang.isEnglish ? 'Lux Low Threshold' : '光照下限' }}</text>
							<text class="th-value">{{ store.thresholds.LuxLowTh }}</text>
						</view>
						<slider 
							:value="store.thresholds.LuxLowTh"
							:min="0" :max="65535" :step="1"
							activeColor="#8b5cf6"
							@changing="onSliderChanging('LuxLowTh', $event)"
							@change="onSliderChange('LuxLowTh', $event)"
						/>

						<view class="th-row" @click="onRowTap('LuxHighTh', 0, 65535)" @longpress="openNumberInput('LuxHighTh', 0, 65535)">
							<text class="th-label">{{ lang.isEnglish ? 'Lux High Threshold' : '光照上限' }}</text>
							<text class="th-value">{{ store.thresholds.LuxHighTh }}</text>
						</view>
						<slider 
							:value="store.thresholds.LuxHighTh"
							:min="0" :max="65535" :step="1"
							activeColor="#a855f7"
							@changing="onSliderChanging('LuxHighTh', $event)"
							@change="onSliderChange('LuxHighTh', $event)"
						/>
						<text class="th-hint">{{ lang.isEnglish ? 'Low must be <= High' : '下限不得高于上限' }}</text>
					</view>
				</view>
				<view class="ctrl-bottom">
					<text class="power-label">
						{{ lang.isEnglish ? 'Power Status' : '电源状态' }}
					</text>
					<NeonToggle3D 
						:modelValue="store.controls[key]" 
						@update:modelValue="onToggle(key)"
					/>
				</view>
			</view>
		</view>

		<!-- 数字输入弹层（长按/双击触发） -->
		<view v-if="edit.show" class="num-mask" @click="closeNumberInput" :class="{ show: edit.show }">
			<view class="num-dialog" @click.stop>
				<!-- 发光装饰线 -->
				<view class="glow-line"></view>
				
				<view class="num-header">
					<text class="num-title">{{ edit.title }}</text>
					<text class="num-range">{{ edit.hint }}</text>
				</view>
				
				<view class="num-input-wrap">
					<view class="num-btn minus" @click="adjustValue(-1)">
						<text class="num-btn-text">−</text>
					</view>
					<input 
						class="num-input" 
						type="number" 
						v-model="edit.valueStr"
						:focus="edit.show"
					/>
					<view class="num-btn plus" @click="adjustValue(1)">
						<text class="num-btn-text">+</text>
					</view>
				</view>
				
				<view class="num-actions">
					<text class="btn cancel" @click="closeNumberInput">
						{{ lang.isEnglish ? 'Cancel' : '取消' }}
					</text>
					<text class="btn ok" @click="confirmNumberInput">
						{{ lang.isEnglish ? 'Confirm' : '确定' }}
					</text>
				</view>
			</view>
		</view>
		<AlertPopup />
	</view>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { deviceStore as store } from '@/store/device';
import { langStore as lang } from '@/store/lang';
import AlertPopup from '@/components/AlertPopup.vue';
import NeonToggle3D from '@/components/NeonToggle3D.vue';

const statusBarHeight = ref(20);
const sysInfo = uni.getSystemInfoSync();
statusBarHeight.value = sysInfo.statusBarHeight || 20;

// 动态背景样式
const backgroundStyle = computed(() => store.getCurrentBackgroundStyle());

const ctrlMap = {
	fanStatus: { 
		nameEn: 'Ventilation Fan', 
		nameZh: '通风风扇', 
		icon: '/static/icons/fan.png',
		color: '#10b981'
	},
	heaterStatus: { 
		nameEn: 'Ceramic Heater', 
		nameZh: '陶瓷加热器', 
		icon: '/static/icons/heater.png',
		color: '#f59e0b'
	},
	atomizerStatus: { 
		nameEn: 'Atomizer / Humidifier', 
		nameZh: '雾化加湿器', 
		icon: '/static/icons/atomizer.png',
		color: '#3b82f6'
	},
	lightStatus: {
		nameEn: 'LED Light',
		nameZh: 'LED 灯',
		icon: '/static/icons/light.png',
		color: '#8b5cf6'
	},
	IRStatus: {
		nameEn: 'Alarm Light',
		nameZh: '警报灯',
		icon: '/static/icons/alert.png',
		color: '#ef4444'
	}
} as const;

type CtrlKey = keyof typeof ctrlMap;

const onToggle = (key: CtrlKey) => {
	const next = !store.controls[key];
	store.sendControl(key as string, next);
};

const onToggleMode = () => {
	const next = !store.status.workMode;
	store.setWorkMode(next);
};

const expandedKey = ref<CtrlKey | ''>('');
const toggleExpand = (key: CtrlKey) => {
	expandedKey.value = expandedKey.value === key ? '' : key;
};

const lastTap = reactive<Record<string, number>>({});
const onRowTap = (thKey: string, min: number, max: number) => {
	const now = Date.now();
	const prev = lastTap[thKey] || 0;
	lastTap[thKey] = now;
	if (now - prev < 350) openNumberInput(thKey, min, max);
};

const clamp = (v: number, min: number, max: number) => Math.max(min, Math.min(max, v));

const normalizeThreshold = (key: string, raw: number) => {
	let v = Number(raw);
	if (Number.isNaN(v)) v = 0;

	if (key === 'TempHighTh' || key === 'TempLowTh') v = clamp(v, -40, 80);
	if (key === 'HumLowTh' || key === 'HumHighTh') v = clamp(v, 0, 100);
	if (key === 'LuxLowTh' || key === 'LuxHighTh') v = clamp(v, 0, 65535);

	if (key === 'TempHighTh') v = Math.max(v, store.thresholds.TempLowTh);
	if (key === 'TempLowTh') v = Math.min(v, store.thresholds.TempHighTh);
	if (key === 'HumLowTh') v = Math.min(v, store.thresholds.HumHighTh);
	if (key === 'HumHighTh') v = Math.max(v, store.thresholds.HumLowTh);
	if (key === 'LuxLowTh') v = Math.min(v, store.thresholds.LuxHighTh);
	if (key === 'LuxHighTh') v = Math.max(v, store.thresholds.LuxLowTh);

	return v;
};

const onSliderChanging = (key: string, e: any) => {
	const v = normalizeThreshold(key, e?.detail?.value);
	(store.thresholds as any)[key] = v;
};

const onSliderChange = (key: string, e: any) => {
	const v = normalizeThreshold(key, e?.detail?.value);
	store.sendThreshold(key, v);
};

const edit = reactive({
	show: false,
	key: '' as string,
	min: 0,
	max: 0,
	title: '',
	hint: '',
	valueStr: ''
});

const openNumberInput = (key: string, min: number, max: number) => {
	edit.show = true;
	edit.key = key;
	edit.min = min;
	edit.max = max;
	edit.title = lang.isEnglish ? `Set ${key}` : `设置 ${key}`;
	edit.hint = (lang.isEnglish ? 'Range: ' : '范围：') + `${min} ~ ${max}`;
	edit.valueStr = String((store.thresholds as any)[key] ?? '');
};

const closeNumberInput = () => {
	uni.hideKeyboard();  // 隐藏键盘
	edit.show = false;
};

const confirmNumberInput = () => {
	uni.hideKeyboard();  // 隐藏键盘
	const num = Number(edit.valueStr);
	const v = normalizeThreshold(edit.key, num);
	store.sendThreshold(edit.key, v);
	edit.show = false;
};

// 数值增减
const adjustValue = (delta: number) => {
	let current = Number(edit.valueStr) || 0;
	current += delta;
	current = clamp(current, edit.min, edit.max);
	edit.valueStr = String(current);
};
</script>

<style lang="scss">
.page-container {
	padding: 60rpx 30rpx 40rpx;
	min-height: 100vh;
	// 流动渐变背景动画
	background: linear-gradient(
		-45deg,
		#4a6a80,           // 更深蓝
		#6a55a0,           // 更深紫
		#906585,           // 中粉
		#a88565,           // 中杏
		#5ab0d8,           // 更亮蓝
		#a070d0            // 更亮紫
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
}
.mode-toggle {
	min-width: 130rpx;
	padding: 12rpx 24rpx;
	border-radius: 999rpx;
	background: rgba(16, 185, 129, 0.25);
	backdrop-filter: blur(10px);
	-webkit-backdrop-filter: blur(10px);
	border: 2rpx solid rgba(16, 185, 129, 0.4);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 
		0 0 15rpx 3rpx rgba(16, 185, 129, 0.3),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.2);
	transition: all 0.3s ease;
	&.manual {
		background: rgba(239, 68, 68, 0.25);
		border-color: rgba(239, 68, 68, 0.4);
		box-shadow: 
			0 0 15rpx 3rpx rgba(239, 68, 68, 0.3),
			inset 0 1rpx 0 rgba(255, 255, 255, 0.2);
	}
}
.mode-toggle-text {
	font-size: 26rpx;
	font-weight: 700;
	color: #fff;
	text-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.25);
	letter-spacing: 1rpx;
}
.mode-toggle.manual .mode-toggle-text {
	color: #fff;
}
.ctrl-card {
	position: relative;
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 24rpx;
	padding: 30rpx;
	padding-left: 36rpx;
	margin-bottom: 24rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.25);
	box-shadow: 
		0 4rpx 20rpx rgba(0, 0, 0, 0.08),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.5);
	transition: border-color 0.3s, box-shadow 0.3s;
	&.active {
		border-color: var(--theme-color);
		box-shadow: 
			0 4rpx 20rpx rgba(0, 0, 0, 0.08),
			0 0 20rpx 2rpx color-mix(in srgb, var(--theme-color) 40%, transparent),
			inset 0 1rpx 0 rgba(255, 255, 255, 0.5);
	}
	.ctrl-top {
		display: flex;
		align-items: center;
		border-bottom: 1rpx solid rgba(255, 255, 255, 0.2);
		padding-bottom: 20rpx;
	}
	.ctrl-top-click {
		display: flex;
		align-items: center;
		flex: 1;
	}
	.ctrl-icon {
		width: 88rpx;
		height: 88rpx;
		border-radius: 22rpx;
		background: rgba(255, 255, 255, 0.3);
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.3s;
		box-shadow: inset 0 1rpx 0 rgba(255, 255, 255, 0.5);
	}
	.ctrl-icon-img {
		width: 48rpx;
		height: 48rpx;
	}
	.ctrl-name {
		margin-left: 24rpx;
		flex: 1;
	}
	.name-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.title {
		font-size: 30rpx;
		font-weight: 700;
		color: #1a1a2e;
		text-shadow: 0 1rpx 2rpx rgba(255, 255, 255, 0.8);
	}
	.name-right {
		display: flex;
		align-items: center;
		gap: 8rpx;
	}
	.mode-tag {
		font-size: 20rpx;
		font-weight: 600;
		color: #059669;
		background: rgba(16, 185, 129, 0.2);
		padding: 6rpx 16rpx;
		border-radius: 999rpx;
		border: 1rpx solid rgba(16, 185, 129, 0.3);
		transition: all 0.3s ease;
		&.manual {
			color: #dc2626;
			background: rgba(239, 68, 68, 0.2);
			border-color: rgba(239, 68, 68, 0.3);
		}
	}
	.expand-arrow {
		font-size: 32rpx;
		color: rgba(26, 26, 46, 0.4);
		font-weight: 300;
		transition: transform 0.3s;
		&.expanded {
			transform: rotate(90deg);
			color: #1a1a2e;
		}
	}
	.status-text {
		font-size: 22rpx;
		color: rgba(26, 26, 46, 0.6);
		margin-top: 4rpx;
		&.running {
			color: #059669;
			font-weight: 600;
		}
	}
	.ctrl-bottom {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 20rpx;
	}
	.power-label {
		font-size: 24rpx;
		color: rgba(26, 26, 46, 0.7);
		font-weight: 500;
	}
}

.th-panel {
	margin-top: 18rpx;
	padding-top: 10rpx;
}
.th-group {
	background: rgba(255, 255, 255, 0.3);
	backdrop-filter: blur(10px);
	-webkit-backdrop-filter: blur(10px);
	border-radius: 20rpx;
	padding: 20rpx 20rpx 12rpx;
	margin-bottom: 14rpx;
	border: 1rpx solid rgba(255, 255, 255, 0.25);
}
.th-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8rpx;
}
.th-label {
	font-size: 24rpx;
	color: rgba(26, 26, 46, 0.8);
	font-weight: 600;
}
.th-value {
	font-size: 24rpx;
	color: #1a1a2e;
	font-weight: 700;
}
.th-hint {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.5);
	display: block;
	margin-top: 6rpx;
}

.num-mask {
	position: fixed;
	left: 0;
	top: 0;
	right: 0;
	bottom: 0;
	/* 渐变遮罩 */
	background: radial-gradient(ellipse at center, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.6) 100%);
	backdrop-filter: blur(8px);
	-webkit-backdrop-filter: blur(8px);
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 40rpx;
	z-index: 9999;
	opacity: 0;
	transition: opacity 0.3s ease;
	&.show {
		opacity: 1;
	}
}
.num-dialog {
	width: 100%;
	position: relative;
	/* 明亮毛玻璃 */
	background: linear-gradient(135deg, 
		rgba(255, 255, 255, 0.75) 0%, 
		rgba(240, 240, 255, 0.7) 100%
	);
	backdrop-filter: blur(25px) saturate(180%);
	-webkit-backdrop-filter: blur(25px) saturate(180%);
	border-radius: 32rpx;
	padding: 40rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.5);
	box-shadow: 
		0 20rpx 60rpx rgba(0, 0, 0, 0.15),
		0 0 40rpx rgba(100, 150, 255, 0.08),
		inset 0 1rpx 0 rgba(255, 255, 255, 0.8);
	/* 入场动画 */
	animation: dialogSlideIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes dialogSlideIn {
	from {
		opacity: 0;
		transform: translateY(60rpx) scale(0.9);
	}
	to {
		opacity: 1;
		transform: translateY(0) scale(1);
	}
}
/* 顶部发光装饰线 */
.glow-line {
	position: absolute;
	top: 0;
	left: 50%;
	transform: translateX(-50%);
	width: 60%;
	height: 4rpx;
	border-radius: 2rpx;
	background: linear-gradient(90deg, 
		transparent 0%, 
		rgba(100, 200, 255, 0.8) 20%, 
		rgba(150, 100, 255, 0.8) 50%, 
		rgba(255, 100, 200, 0.8) 80%, 
		transparent 100%
	);
	box-shadow: 0 0 20rpx 4rpx rgba(150, 100, 255, 0.5);
}
.num-header {
	margin-bottom: 30rpx;
}
.num-title {
	font-size: 34rpx;
	font-weight: 700;
	color: #1a1a2e;
	display: block;
	margin-bottom: 8rpx;
}
.num-range {
	font-size: 22rpx;
	color: #64748b;
	display: block;
}
/* 数值输入区域 */
.num-input-wrap {
	display: flex;
	align-items: center;
	gap: 16rpx;
	margin-bottom: 30rpx;
}
.num-btn {
	width: 72rpx;
	height: 72rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(255, 255, 255, 0.6);
	border: 1rpx solid rgba(0, 0, 0, 0.08);
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
	transition: all 0.2s ease;
	&:active {
		transform: scale(0.92);
	}
	&.minus {
		background: rgba(239, 68, 68, 0.15);
		border-color: rgba(239, 68, 68, 0.25);
	}
	&.plus {
		background: rgba(16, 185, 129, 0.15);
		border-color: rgba(16, 185, 129, 0.25);
	}
}
.num-btn-text {
	font-size: 36rpx;
	font-weight: 600;
	color: #1a1a2e;
}
.num-input {
	flex: 1;
	background: rgba(255, 255, 255, 0.7);
	border: 2rpx solid rgba(0, 0, 0, 0.1);
	border-radius: 20rpx;
	padding: 20rpx;
	font-size: 40rpx;
	color: #1a1a2e;
	font-weight: 700;
	text-align: center;
	transition: all 0.3s ease;
}
.num-input:focus {
	border-color: rgba(100, 150, 255, 0.5);
	box-shadow: 0 0 20rpx 4rpx rgba(100, 150, 255, 0.15);
}
.num-actions {
	display: flex;
	justify-content: space-between;
	gap: 20rpx;
}
.btn {
	flex: 1;
	padding: 18rpx 28rpx;
	border-radius: 20rpx;
	font-size: 28rpx;
	font-weight: 600;
	text-align: center;
	transition: all 0.2s ease;
	&:active {
		transform: scale(0.96);
	}
}
.btn.cancel {
	background: rgba(0, 0, 0, 0.06);
	color: #64748b;
	border: 1rpx solid rgba(0, 0, 0, 0.08);
}
.btn.ok {
	background: linear-gradient(135deg, #10b981, #059669);
	color: #fff;
	border: none;
	box-shadow: 
		0 6rpx 20rpx rgba(16, 185, 129, 0.35),
		0 0 15rpx rgba(16, 185, 129, 0.15);
}
/* 流动渐变背景动画 */
@keyframes gradientFlow {
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
}
</style>