<template>
	<view class="page-container">
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

					<!-- 加湿器：HumLowTh / HumHighTH -->
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

						<view class="th-row" @click="onRowTap('HumHighTH', 0, 100)" @longpress="openNumberInput('HumHighTH', 0, 100)">
							<text class="th-label">{{ lang.isEnglish ? 'Hum High Threshold' : '湿度上限' }}</text>
							<text class="th-value">{{ store.thresholds.HumHighTH }}</text>
						</view>
						<slider 
							:value="store.thresholds.HumHighTH"
							:min="0" :max="100" :step="1"
							activeColor="#0ea5e9"
							@changing="onSliderChanging('HumHighTH', $event)"
							@change="onSliderChange('HumHighTH', $event)"
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
					<view class="toggle-wrap" @click.stop="onToggle(key)">
						<view class="toggle-track" :class="{ active: store.controls[key] }">
							<view class="toggle-thumb" :class="{ active: store.controls[key] }"></view>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 数字输入弹层（长按/双击触发） -->
		<view v-if="edit.show" class="num-mask" @click="closeNumberInput">
			<view class="num-dialog" @click.stop>
				<text class="num-title">{{ edit.title }}</text>
				<input class="num-input" type="number" v-model="edit.valueStr" />
				<view class="num-actions">
					<text class="btn cancel" @click="closeNumberInput">{{ lang.isEnglish ? 'Cancel' : '取消' }}</text>
					<text class="btn ok" @click="confirmNumberInput">{{ lang.isEnglish ? 'OK' : '确定' }}</text>
				</view>
				<text class="num-hint">{{ edit.hint }}</text>
			</view>
		</view>
		<AlertPopup />
	</view>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { deviceStore as store } from '@/store/device';
import { langStore as lang } from '@/store/lang';
import AlertPopup from '@/components/AlertPopup.vue';

const statusBarHeight = ref(20);
const sysInfo = uni.getSystemInfoSync();
statusBarHeight.value = sysInfo.statusBarHeight || 20;

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
	if (key === 'HumLowTh' || key === 'HumHighTH') v = clamp(v, 0, 100);
	if (key === 'LuxLowTh' || key === 'LuxHighTh') v = clamp(v, 0, 65535);

	if (key === 'TempHighTh') v = Math.max(v, store.thresholds.TempLowTh);
	if (key === 'TempLowTh') v = Math.min(v, store.thresholds.TempHighTh);
	if (key === 'HumLowTh') v = Math.min(v, store.thresholds.HumHighTH);
	if (key === 'HumHighTH') v = Math.max(v, store.thresholds.HumLowTh);
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
	edit.show = false;
};

const confirmNumberInput = () => {
	const num = Number(edit.valueStr);
	const v = normalizeThreshold(edit.key, num);
	store.sendThreshold(edit.key, v);
	edit.show = false;
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
		color: #fff;
		display: block;
		text-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.3);
	}
	.sub-title {
		font-size: 24rpx;
		color: rgba(255, 255, 255, 0.7);
		text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.2);
	}
}
.mode-toggle {
	min-width: 120rpx;
	padding: 10rpx 22rpx;
	border-radius: 999rpx;
	background: rgba(16, 185, 129, 0.2);
	backdrop-filter: blur(10px);
	-webkit-backdrop-filter: blur(10px);
	border: 1rpx solid rgba(16, 185, 129, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 0 12rpx 2rpx rgba(16, 185, 129, 0.2);
	&.manual {
		background: rgba(239, 68, 68, 0.2);
		border-color: rgba(239, 68, 68, 0.3);
		box-shadow: 0 0 12rpx 2rpx rgba(239, 68, 68, 0.2);
	}
}
.mode-toggle-text {
	font-size: 24rpx;
	font-weight: 600;
	color: #fff;
	text-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.2);
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
		color: #fff;
		text-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.3);
	}
	.name-right {
		display: flex;
		align-items: center;
		gap: 8rpx;
	}
	.mode-tag {
		font-size: 20rpx;
		font-weight: 600;
		color: #fff;
		background: rgba(16, 185, 129, 0.4);
		padding: 4rpx 14rpx;
		border-radius: 999rpx;
		text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.2);
		&.manual {
			color: #fff;
			background: rgba(239, 68, 68, 0.4);
		}
	}
	.expand-arrow {
		font-size: 32rpx;
		color: rgba(255, 255, 255, 0.5);
		font-weight: 300;
		transition: transform 0.3s;
		&.expanded {
			transform: rotate(90deg);
			color: #fff;
		}
	}
	.status-text {
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.6);
		margin-top: 4rpx;
		&.running {
			color: #fff;
			font-weight: 600;
			text-shadow: 0 0 10rpx var(--theme-color);
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
		color: rgba(255, 255, 255, 0.8);
		font-weight: 500;
		text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.2);
	}
}

/* 自定义 Toggle 开关 - 发光效果 */
.toggle-wrap {
	padding: 4rpx;
}
.toggle-track {
	width: 100rpx;
	height: 56rpx;
	border-radius: 28rpx;
	background: rgba(255, 255, 255, 0.3);
	border: 1rpx solid rgba(255, 255, 255, 0.3);
	position: relative;
	transition: background 0.35s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.35s;
	&.active {
		background: linear-gradient(135deg, #10b981, #059669);
		box-shadow: 0 0 20rpx 4rpx rgba(16, 185, 129, 0.5);
		border-color: rgba(16, 185, 129, 0.6);
	}
}
.toggle-thumb {
	width: 44rpx;
	height: 44rpx;
	border-radius: 22rpx;
	background: #fff;
	position: absolute;
	left: 6rpx;
	top: 6rpx;
	box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.15), 0 0 0 1rpx rgba(0,0,0,0.04);
	transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
	&.active {
		transform: translateX(44rpx);
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
	color: rgba(255, 255, 255, 0.85);
	font-weight: 600;
	text-shadow: 0 1rpx 2rpx rgba(0, 0, 0, 0.2);
}
.th-value {
	font-size: 24rpx;
	color: #fff;
	font-weight: 700;
	text-shadow: 0 1rpx 3rpx rgba(0, 0, 0, 0.3);
}
.th-hint {
	font-size: 20rpx;
	color: rgba(255, 255, 255, 0.6);
	display: block;
	margin-top: 6rpx;
}

.num-mask {
	position: fixed;
	left: 0;
	top: 0;
	right: 0;
	bottom: 0;
	background: rgba(0,0,0,0.4);
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 40rpx;
	z-index: 9999;
}
.num-dialog {
	width: 100%;
	background: rgba(255, 255, 255, 0.85);
	backdrop-filter: blur(20px);
	-webkit-backdrop-filter: blur(20px);
	border-radius: 28rpx;
	padding: 36rpx;
	box-shadow: 0 20rpx 60rpx rgba(0,0,0,0.15);
	border: 1rpx solid rgba(255, 255, 255, 0.4);
}
.num-title {
	font-size: 32rpx;
	font-weight: 700;
	color: #0f172a;
	display: block;
	margin-bottom: 24rpx;
}
.num-input {
	background: rgba(255, 255, 255, 0.5);
	border: 1rpx solid rgba(255, 255, 255, 0.3);
	border-radius: 16rpx;
	padding: 22rpx;
	font-size: 32rpx;
	color: #0f172a;
	font-weight: 600;
}
.num-actions {
	display: flex;
	justify-content: flex-end;
	gap: 20rpx;
	margin-top: 24rpx;
}
.btn {
	padding: 14rpx 28rpx;
	border-radius: 16rpx;
	font-size: 26rpx;
	font-weight: 600;
}
.btn.cancel {
	background: rgba(255, 255, 255, 0.4);
	color: #475569;
	border: 1rpx solid rgba(255, 255, 255, 0.3);
}
.btn.ok {
	background: linear-gradient(135deg, #10b981, #059669);
	color: #fff;
	box-shadow: 0 4rpx 12rpx rgba(16, 185, 129, 0.4);
}
.num-hint {
	margin-top: 16rpx;
	font-size: 20rpx;
	color: #94a3b8;
	display: block;
}
/* 流动渐变背景动画 */
@keyframes gradientFlow {
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
}
</style>