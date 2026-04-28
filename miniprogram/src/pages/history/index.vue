<template>
	<view class="page-container" :style="backgroundStyle">
		<view class="header-section" :style="{ paddingTop: statusBarHeight + 'px' }">
			<text class="main-title">{{ lang.isEnglish ? 'History' : '历史数据' }}</text>
			<text class="sub-title">{{ lang.isEnglish ? 'Historical data analysis' : '环境数据趋势与告警记录' }}</text>
		</view>

		<view class="chart-container">
			<view class="chart-head">
				<view class="chart-title-wrap">
					<text class="chart-title">{{ chartTitle }}</text>
					<text v-if="chartStateChip" class="chart-state-chip" :class="chartViewState">{{ chartStateChip }}</text>
				</view>
				<view class="range-tabs">
					<view class="tab" :class="{ active: rangeHours === 1 }" @click="rangeHours = 1">1h</view>
					<view class="tab" :class="{ active: rangeHours === 6 }" @click="rangeHours = 6">6h</view>
					<view class="tab" :class="{ active: rangeHours === 24 }" @click="rangeHours = 24">24h</view>
					<view class="tab" :class="{ active: rangeHours === 168 }" @click="rangeHours = 168">7d</view>
				</view>
			</view>

			<view class="metric-tabs">
				<view
					v-for="m in metrics"
					:key="m.key"
					class="m-tab"
					:class="{ active: metricKey === m.key }"
					@click="metricKey = m.key"
				>
					{{ lang.isEnglish ? m.en : m.zh }}
				</view>
			</view>

			<view class="trend-bar">
				<text class="trend-label">{{ lang.isEnglish ? 'Trend' : '趋势' }}:</text>
				<text class="trend-value" :class="trendInfo.dir">
					{{ trendInfo.icon }} {{ lang.isEnglish ? trendInfo.en : trendInfo.zh }}
				</text>
			</view>

			<view v-if="chartViewState !== 'ready'" class="chart-state-card" :class="chartViewState">
				<view class="chart-state-copy">
					<text class="chart-state-title">{{ chartStateTitle }}</text>
					<text class="chart-state-desc">{{ chartStateDescription }}</text>
				</view>
				<view class="chart-state-meta">
					<text class="chart-state-value">{{ latestMetricDisplay }}</text>
					<text class="chart-state-time">{{ latestPointText }}</text>
				</view>
			</view>

			<view class="chart-box">
				<LineChart
					:canvasId="canvasId"
					:width="chartWidth"
					:height="280"
					:categories="chartCategories"
					:values="chartValues"
					:unit="metricMeta.unit"
					:lineColor="lineColor"
					:fillColor="lineColor"
					:highTh="currentHighTh"
					:lowTh="currentLowTh"
					:emptyText="lang.isEnglish ? 'No data available' : '暂无数据'"
					:state="chartViewState"
					:mode="chartMode"
					:rangeHours="rangeHours"
					:statusTitle="chartStateTitle"
					:helperText="chartHintText"
					@pointTap="onPointTap"
				/>
			</view>

			<view class="stats-row">
				<view class="stat-item">
					<text class="stat-label">{{ lang.isEnglish ? 'Max' : '最大' }}</text>
					<text class="stat-value">{{ hasData ? stats.max.toFixed(1) + metricMeta.unit : '-' }}</text>
				</view>
				<view class="stat-item">
					<text class="stat-label">{{ lang.isEnglish ? 'Min' : '最小' }}</text>
					<text class="stat-value">{{ hasData ? stats.min.toFixed(1) + metricMeta.unit : '-' }}</text>
				</view>
				<view class="stat-item">
					<text class="stat-label">{{ lang.isEnglish ? 'Avg' : '平均' }}</text>
					<text class="stat-value">{{ hasData ? stats.avg.toFixed(1) + metricMeta.unit : '-' }}</text>
				</view>
				<view class="stat-item">
					<text class="stat-label">{{ lang.isEnglish ? 'Volatility' : '波动率' }}</text>
					<text class="stat-value">{{ hasData ? stats.volatility.toFixed(1) + '%' : '-' }}</text>
				</view>
			</view>
		</view>

		<view v-if="detail.show" class="detail-mask" @click="detail.show = false">
			<view class="detail-card" @click.stop>
				<text class="detail-time">{{ detail.time }}</text>
				<text class="detail-value">{{ detail.value }}{{ metricMeta.unit }}</text>
				<view v-if="detail.isHighAlert" class="detail-alert high">
					{{ lang.isEnglish ? 'Above High Threshold' : '超过最高阈值' }}
				</view>
				<view v-else-if="detail.isLowAlert" class="detail-alert low">
					{{ lang.isEnglish ? 'Below Low Threshold' : '低于最低阈值' }}
				</view>
				<view v-else class="detail-ok">
					{{ lang.isEnglish ? 'Normal' : '正常' }}
				</view>
			</view>
		</view>

		<view class="log-section">
			<view class="log-header">
				<text>{{ lang.isEnglish ? 'Alert Log' : '告警记录' }}</text>
				<view class="log-actions">
					<text class="count-tag">{{ envAlerts.length }} {{ lang.isEnglish ? 'Events' : '条' }}</text>
					<text class="clear-btn" @click="clearAlerts">
						{{ lang.isEnglish ? 'Clear' : '清除' }}
					</text>
				</view>
			</view>
			<view v-if="envAlerts.length === 0" class="empty">
				{{ lang.isEnglish ? 'No alerts in selected range.' : '当前时间范围内没有告警。' }}
			</view>
			<view class="log-item" v-for="a in envAlerts" :key="a.id" @click="onAlertTap(a)">
				<view class="log-status" :class="a.statusClass">
					<view class="log-dot"></view>
					<text>{{ a.badge }}</text>
				</view>
				<view class="log-info">
					<text class="log-title">{{ a.title }}</text>
					<text class="log-time">{{ a.timeText }}</text>
				</view>
			</view>
		</view>
		<AlertPopup />
	</view>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { deviceStore as store } from '@/store/device';
import { langStore as lang } from '@/store/lang';
import LineChart from '@/components/LineChart.vue';
import AlertPopup from '@/components/AlertPopup.vue';

const statusBarHeight = ref(20);
const sysInfo = uni.getSystemInfoSync();
statusBarHeight.value = sysInfo.statusBarHeight || 20;

const backgroundStyle = computed(() => store.getCurrentBackgroundStyle());
const rangeHours = ref<1 | 6 | 24 | 168>(24);

const metrics = [
	{ key: 'temperature', zh: '温度', en: 'Temp', unit: '℃', color: '#10b981', highThKey: 'TempHighTh', lowThKey: 'TempLowTh' },
	{ key: 'humidity', zh: '湿度', en: 'Hum', unit: '%', color: '#3b82f6', highThKey: 'HumHighTh', lowThKey: 'HumLowTh' },
	{ key: 'CO2', zh: 'CO2', en: 'CO2', unit: 'ppm', color: '#0ea5e9', highThKey: null, lowThKey: null },
	{ key: 'lux', zh: '光照', en: 'Lux', unit: 'Lux', color: '#f59e0b', highThKey: 'LuxHighTh', lowThKey: 'LuxLowTh' },
	{ key: 'NH3', zh: 'NH3', en: 'NH3', unit: 'ppm', color: '#f43f5e', highThKey: null, lowThKey: null },
	{ key: 'soilHumidity', zh: '土壤', en: 'Soil', unit: '%', color: '#8b5cf6', highThKey: null, lowThKey: null }
] as const;

type MetricKey = (typeof metrics)[number]['key'];
type ThresholdKey = 'TempHighTh' | 'TempLowTh' | 'HumHighTh' | 'HumLowTh' | 'LuxHighTh' | 'LuxLowTh';
type ChartViewState = 'loading' | 'empty' | 'low-data' | 'ready';
type HistoryPoint = (typeof store.history)[number];
type ChartPointTapInfo = {
	index: number;
	value: number;
	time: string;
	isHighAlert: boolean;
	isLowAlert: boolean;
};
type AlertItem = {
	id: string;
	statusClass: string;
	badge: string;
	title: string;
	timeText: string;
	raw: (typeof store.envAlertEvents)[number];
};

const metricKey = ref<MetricKey>('temperature');
const metricMeta = computed(() => metrics.find((item) => item.key === metricKey.value) ?? metrics[0]);
const lineColor = computed(() => metricMeta.value.color);
const rawPoints = computed(() => store.getHistory(rangeHours.value));
const rawPointCount = computed(() => rawPoints.value.length);
const thresholds = store.thresholds as Record<ThresholdKey, number>;

const currentHighTh = computed(() => {
	const key = metricMeta.value.highThKey;
	return key ? thresholds[key] : undefined;
});
const currentLowTh = computed(() => {
	const key = metricMeta.value.lowThKey;
	return key ? thresholds[key] : undefined;
});

const detail = reactive({
	show: false,
	time: '',
	value: '0.0',
	isHighAlert: false,
	isLowAlert: false
});

const fmtTime = (ts: number) => {
	const d = new Date(ts);
	const hours = String(d.getHours()).padStart(2, '0');
	const minutes = String(d.getMinutes()).padStart(2, '0');
	const month = String(d.getMonth() + 1).padStart(2, '0');
	const day = String(d.getDate()).padStart(2, '0');
	if (rangeHours.value >= 168) return `${month}-${day}`;
	return `${hours}:${minutes}`;
};

const fmtDateTime = (ts: number) => {
	const d = new Date(ts);
	const year = d.getFullYear();
	const month = String(d.getMonth() + 1).padStart(2, '0');
	const day = String(d.getDate()).padStart(2, '0');
	const hours = String(d.getHours()).padStart(2, '0');
	const minutes = String(d.getMinutes()).padStart(2, '0');
	return `${year}-${month}-${day} ${hours}:${minutes}`;
};

const chartTitle = computed(() => {
	const name = lang.isEnglish ? metricMeta.value.en : metricMeta.value.zh;
	const unit = rangeHours.value >= 168 ? '7d' : `${rangeHours.value}h`;
	return `${name} (${unit})`;
});

function downsample(arr: HistoryPoint[], intervalMs: number) {
	if (arr.length <= 200) return arr;
	const result: HistoryPoint[] = [];
	const metric = metricKey.value;
	let group: HistoryPoint[] = [];
	let nextTs = arr[0].ts + intervalMs;

	for (const point of arr) {
		if (point.ts >= nextTs && group.length > 0) {
			const first = group[0];
			const last = group[group.length - 1];
			let maxPoint = first;
			let minPoint = first;

			for (const groupPoint of group) {
				if ((groupPoint[metric] ?? 0) > (maxPoint[metric] ?? 0)) maxPoint = groupPoint;
				if ((groupPoint[metric] ?? 0) < (minPoint[metric] ?? 0)) minPoint = groupPoint;
			}

			const added = new Set<number>();
			for (const sampledPoint of [first, maxPoint, minPoint, last]) {
				if (!added.has(sampledPoint.ts)) {
					result.push(sampledPoint);
					added.add(sampledPoint.ts);
				}
			}

			group = [];
			nextTs = point.ts + intervalMs;
		}
		group.push(point);
	}

	if (group.length > 0) {
		const first = group[0];
		const last = group[group.length - 1];
		let maxPoint = first;
		let minPoint = first;

		for (const groupPoint of group) {
			if ((groupPoint[metric] ?? 0) > (maxPoint[metric] ?? 0)) maxPoint = groupPoint;
			if ((groupPoint[metric] ?? 0) < (minPoint[metric] ?? 0)) minPoint = groupPoint;
		}

		const added = new Set<number>();
		for (const sampledPoint of [first, maxPoint, minPoint, last]) {
			if (!added.has(sampledPoint.ts)) {
				result.push(sampledPoint);
				added.add(sampledPoint.ts);
			}
		}
	}

	return result;
}

function makeCurrentPoint(ts = Date.now()): HistoryPoint {
	return {
		ts,
		temperature: Number(store.sensors.temperature) || 0,
		humidity: Number(store.sensors.humidity) || 0,
		CO2: Number(store.sensors.CO2) || 0,
		lux: Number(store.sensors.lux) || 0,
		NH3: Number(store.sensors.NH3) || 0,
		soilHumidity: Number(store.sensors.soilHumidity) || 0,
		Silkworm_Total: Number(store.sensors.Silkworm_Total) || 0,
		Silkworm_Healthy: Number(store.sensors.Silkworm_Healthy) || 0,
		Silkworm_Sick: Number(store.sensors.Silkworm_Sick) || 0,
		Silkworm_Sleep: Number(store.sensors.Silkworm_Sleep) || 0
	};
}

const points = computed<HistoryPoint[]>(() => {
	const arr = rawPoints.value.slice();
	if (arr.length === 0) return [];
	if (arr.length === 1) {
		const nextTs = Math.min(Date.now(), arr[0].ts + 60 * 1000);
		return [arr[0], makeCurrentPoint(nextTs)];
	}
	if (rangeHours.value >= 168) return downsample(arr, 5 * 60 * 1000);
	if (rangeHours.value >= 24) return downsample(arr, 60 * 1000);
	return arr;
});

const chartCategories = computed(() => points.value.map((point) => fmtTime(point.ts)));
const chartValues = computed(() => points.value.map((point) => Number(point[metricKey.value] ?? 0)));
const rawMetricValues = computed(() => rawPoints.value.map((point) => Number(point[metricKey.value] ?? 0)));
const hasData = computed(() => rawMetricValues.value.length > 0);

const latestRawPoint = computed(() => rawPoints.value[rawPoints.value.length - 1]);
const latestMetricValue = computed(() => {
	const latestPoint = latestRawPoint.value;
	if (latestPoint) return Number(latestPoint[metricKey.value]).toFixed(1);
	return Number(store.sensors[metricKey.value]).toFixed(1);
});
const latestMetricDisplay = computed(() => `${latestMetricValue.value}${metricMeta.value.unit}`);
const latestPointText = computed(() => {
	if (latestRawPoint.value) return fmtDateTime(latestRawPoint.value.ts);
	if (store.status.lastDataTime) return fmtDateTime(store.status.lastDataTime);
	return lang.isEnglish ? 'Waiting for data' : '等待数据中';
});

const chartViewState = computed<ChartViewState>(() => {
	if (rawPointCount.value === 0 && store.historySyncing) return 'loading';
	if (rawPointCount.value === 0) return 'empty';
	if (rawPointCount.value < 4) return 'low-data';
	return 'ready';
});
const chartStateChip = computed(() => {
	if (chartViewState.value === 'loading') return lang.isEnglish ? 'Syncing' : '同步中';
	if (chartViewState.value === 'empty') return lang.isEnglish ? 'Empty' : '暂无';
	if (chartViewState.value === 'low-data') return lang.isEnglish ? 'Sparse' : '样本少';
	return '';
});
const chartStateTitle = computed(() => {
	if (chartViewState.value === 'loading') return lang.isEnglish ? 'Preparing chart' : '正在准备图表';
	if (chartViewState.value === 'empty') {
		if (store.historySyncError) return lang.isEnglish ? 'History sync failed' : '历史同步失败';
		return lang.isEnglish ? 'No history yet' : '当前暂无历史数据';
	}
	if (chartViewState.value === 'low-data') return lang.isEnglish ? 'Limited 1h samples' : '1h 数据样本较少';
	return '';
});
const chartStateDescription = computed(() => {
	if (chartViewState.value === 'loading') {
		return lang.isEnglish ? 'Using local cache first and syncing cloud history in background.' : '优先展示本地缓存，云端历史正在后台同步。';
	}
	if (chartViewState.value === 'empty') {
		if (store.historySyncError) {
			return lang.isEnglish ? `Cloud history sync failed. ${store.historySyncError}` : `云端历史同步失败：${store.historySyncError}`;
		}
		return lang.isEnglish ? 'No valid history was found in the selected range. New samples will appear here automatically.' : '当前时间范围内还没有可用历史点，新的采样到达后会自动显示。';
	}
	if (chartViewState.value === 'low-data') {
		return lang.isEnglish ? 'Only a few samples are available, so the chart highlights the latest reading instead of pretending a full trend exists.' : '当前只有少量样本，图表会优先突出最近读数，而不是伪装成完整趋势。';
	}
	return '';
});
const chartHintText = computed(() => {
	if (chartViewState.value === 'loading') return lang.isEnglish ? 'Syncing history…' : '历史数据同步中…';
	if (chartViewState.value === 'empty') {
		if (store.historySyncError) return lang.isEnglish ? 'Showing local fallback only' : '当前仅显示本地兜底信息';
		return lang.isEnglish ? 'Waiting for first valid sample' : '等待第一条有效历史采样';
	}
	if (chartViewState.value === 'low-data') return lang.isEnglish ? 'Showing the latest available readings' : '优先展示最近可用采样';
	return '';
});

const stats = computed(() => {
	const values = rawMetricValues.value;
	if (values.length === 0) return { max: 0, min: 0, avg: 0, volatility: 0 };
	const max = Math.max(...values);
	const min = Math.min(...values);
	const avg = values.reduce((total, value) => total + value, 0) / values.length;
	const volatility = avg !== 0 ? ((max - min) / avg) * 100 : 0;
	return { max, min, avg, volatility };
});

const trendInfo = computed(() => {
	const values = rawMetricValues.value;
	if (values.length < 10) return { dir: 'stable', icon: '→', zh: '数据不足', en: 'Insufficient data' };
	const sampleSize = Math.max(1, Math.floor(values.length * 0.3));
	const first = values.slice(0, sampleSize).reduce((total, value) => total + value, 0) / sampleSize;
	const last = values.slice(-sampleSize).reduce((total, value) => total + value, 0) / sampleSize;
	const diff = last - first;
	const pct = first !== 0 ? Math.abs(diff / first) * 100 : 0;
	if (pct < 3) return { dir: 'stable', icon: '→', zh: '稳定', en: 'Stable' };
	if (diff > 0) {
		return { dir: 'up', icon: '↑', zh: `上升 (+${diff.toFixed(1)}${metricMeta.value.unit})`, en: `Rising (+${diff.toFixed(1)}${metricMeta.value.unit})` };
	}
	return { dir: 'down', icon: '↓', zh: `下降 (${diff.toFixed(1)}${metricMeta.value.unit})`, en: `Falling (${diff.toFixed(1)}${metricMeta.value.unit})` };
});

const canvasId = 'history_line_canvas';
const chartWidth = Math.max(300, (sysInfo.windowWidth || 375) - 134);
const chartMode = computed<'compact' | 'expanded'>(() => (rangeHours.value <= 6 ? 'compact' : 'expanded'));
const clearAlerts = () => { store.clearEnvAlerts(); };

const envAlerts = computed<AlertItem[]>(() => {
	const cutoff = Date.now() - rangeHours.value * 60 * 60 * 1000;
	const metricNameZh = (metric: string) => {
		if (metric === 'temperature') return '温度';
		if (metric === 'humidity') return '湿度';
		if (metric === 'lux') return '光照';
		if (metric === 'infrared') return '入侵检测';
		return metric;
	};

	return store.envAlertEvents
		.filter((event) => event.ts >= cutoff)
		.slice()
		.sort((a, b) => b.ts - a.ts)
		.map((event) => {
			const isIR = event.metric === 'infrared';
			const isSevere = event.severity === 'severe';
			const statusClass = isIR || isSevere ? 'severe' : 'light';
			const badge = isIR
				? (lang.isEnglish ? 'Intrusion' : '入侵')
				: (!lang.isEnglish
					? `${event.level === 'high' ? '偏高' : '偏低'}${isSevere ? '(严重)' : '(轻微)'}`
					: `${event.level === 'high' ? 'HIGH' : 'LOW'}${isSevere ? ' (Severe)' : ' (Light)'}`);
			const title = isIR
				? (lang.isEnglish ? 'Intrusion - Motion Detected' : '入侵检测 - 检测到有人靠近')
				: (lang.isEnglish
					? `${event.metric} ${event.level === 'high' ? '>' : '<'} ${event.th} (${event.value})`
					: `${metricNameZh(event.metric)}${event.level === 'high' ? '高于' : '低于'} ${event.th}（当前 ${event.value}）`);
			return { id: `${event.metric}-${event.ts}-${event.type}`, statusClass, badge, title, timeText: fmtDateTime(event.ts), raw: event };
		});
});

const onPointTap = (info: ChartPointTapInfo) => {
	detail.show = true;
	const point = points.value[info.index];
	detail.time = point ? fmtDateTime(point.ts) : info.time;
	detail.value = Number(info.value).toFixed(1);
	detail.isHighAlert = info.isHighAlert;
	detail.isLowAlert = info.isLowAlert;
};

const onAlertTap = (item: AlertItem) => {
	const event = item.raw;
	store.showAlertPopup(event.metric, event.level, event.severity, event.value, event.th);
};
</script>

<style lang="scss">
.page-container {
	padding: 60rpx 30rpx 40rpx;
	min-height: 100vh;
	background: linear-gradient(-45deg, #4a6a80, #6a55a0, #906585, #a88565, #5ab0d8, #a070d0);
	background-size: 600% 600%;
	animation: gradientFlow 10s ease infinite;

	.header-section {
		margin-bottom: 26rpx;
		background: rgba(255, 255, 255, 0.5);
		backdrop-filter: blur(16px);
		-webkit-backdrop-filter: blur(16px);
		border-radius: 24rpx;
		padding: 20rpx 28rpx;
		box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
		border: 1rpx solid rgba(255, 255, 255, 0.3);
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

@keyframes gradientFlow {
	0% { background-position: 0% 50%; }
	50% { background-position: 100% 50%; }
	100% { background-position: 0% 50%; }
}

.chart-container {
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 24rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.25);
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08), inset 0 1rpx 0 rgba(255, 255, 255, 0.5);
}

.chart-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 16rpx;
	margin-bottom: 20rpx;
}

.chart-title-wrap {
	display: flex;
	align-items: center;
	gap: 12rpx;
	flex-wrap: wrap;
}

.chart-title {
	font-size: 30rpx;
	font-weight: 700;
	color: #1a1a2e;
}

.chart-state-chip {
	padding: 6rpx 14rpx;
	border-radius: 999rpx;
	font-size: 18rpx;
	font-weight: 700;

	&.loading {
		background: rgba(59, 130, 246, 0.14);
		color: #2563eb;
	}

	&.empty {
		background: rgba(100, 116, 139, 0.14);
		color: #475569;
	}

	&.low-data {
		background: rgba(245, 158, 11, 0.16);
		color: #b45309;
	}
}

.range-tabs {
	display: flex;
	gap: 8rpx;
	flex-shrink: 0;
}

.tab {
	padding: 8rpx 16rpx;
	border-radius: 999rpx;
	background: rgba(26, 26, 46, 0.1);
	color: rgba(26, 26, 46, 0.7);
	font-size: 20rpx;
	font-weight: 500;
	border: 1rpx solid rgba(26, 26, 46, 0.1);

	&.active {
		background: linear-gradient(135deg, #10b981, #059669);
		color: #fff;
		box-shadow: 0 0 15rpx 3rpx rgba(16, 185, 129, 0.35);
		border-color: transparent;
	}
}

.metric-tabs {
	display: flex;
	flex-wrap: wrap;
	gap: 10rpx;
	margin-bottom: 16rpx;
}

.m-tab {
	padding: 8rpx 18rpx;
	border-radius: 999rpx;
	background: rgba(26, 26, 46, 0.1);
	color: rgba(26, 26, 46, 0.7);
	font-size: 22rpx;
	font-weight: 500;
	border: 1rpx solid rgba(26, 26, 46, 0.1);

	&.active {
		background: linear-gradient(135deg, #3b82f6, #2563eb);
		color: #fff;
		box-shadow: 0 0 15rpx 3rpx rgba(59, 130, 246, 0.35);
		border-color: transparent;
	}
}

.trend-bar {
	display: flex;
	align-items: center;
	gap: 10rpx;
	margin-bottom: 16rpx;
}

.trend-label {
	font-size: 22rpx;
	color: rgba(26, 26, 46, 0.65);
}

.trend-value {
	font-size: 22rpx;
	font-weight: 600;
	padding: 4rpx 14rpx;
	border-radius: 999rpx;

	&.up {
		color: #dc2626;
		background: rgba(239, 68, 68, 0.2);
	}

	&.down {
		color: #2563eb;
		background: rgba(59, 130, 246, 0.2);
	}

	&.stable {
		color: #059669;
		background: rgba(16, 185, 129, 0.2);
	}
}

.chart-state-card {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 20rpx;
	padding: 22rpx 24rpx;
	margin-bottom: 18rpx;
	border-radius: 22rpx;
	border: 1rpx solid rgba(255, 255, 255, 0.28);
	background: rgba(255, 255, 255, 0.5);
	box-shadow: 0 8rpx 24rpx rgba(15, 23, 42, 0.06);

	&.loading {
		background: linear-gradient(135deg, rgba(219, 234, 254, 0.82), rgba(239, 246, 255, 0.72));
	}

	&.empty {
		background: linear-gradient(135deg, rgba(241, 245, 249, 0.82), rgba(248, 250, 252, 0.72));
	}

	&.low-data {
		background: linear-gradient(135deg, rgba(255, 247, 237, 0.88), rgba(255, 251, 235, 0.78));
	}
}

.chart-state-copy {
	flex: 1;
	min-width: 0;
}

.chart-state-title {
	display: block;
	font-size: 26rpx;
	font-weight: 700;
	color: #0f172a;
	margin-bottom: 6rpx;
}

.chart-state-desc {
	display: block;
	font-size: 21rpx;
	line-height: 1.5;
	color: rgba(15, 23, 42, 0.7);
}

.chart-state-meta {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 8rpx;
	flex-shrink: 0;
}

.chart-state-value {
	font-size: 34rpx;
	font-weight: 800;
	color: #0f172a;
}

.chart-state-time {
	font-size: 20rpx;
	color: rgba(15, 23, 42, 0.55);
}

.chart-box {
	height: 280px;
}

.stats-row {
	display: flex;
	justify-content: space-between;
	gap: 12rpx;
	flex-wrap: wrap;
	margin-top: 20rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid rgba(255, 255, 255, 0.15);
}

.stat-item {
	text-align: center;
	flex: 1;
	min-width: 140rpx;
	padding: 18rpx 14rpx;
	border-radius: 20rpx;
	background: rgba(255, 255, 255, 0.38);
	border: 1rpx solid rgba(255, 255, 255, 0.22);
	box-shadow: inset 0 1rpx 0 rgba(255, 255, 255, 0.55);
}

.stat-label {
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.6);
	display: block;
	margin-bottom: 4rpx;
}

.stat-value {
	font-size: 24rpx;
	font-weight: 700;
	color: #1a1a2e;
}

.detail-mask {
	position: fixed;
	left: 0;
	top: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 9999;
}

.detail-card {
	background: #fff;
	border-radius: 24rpx;
	padding: 40rpx 48rpx;
	text-align: center;
	box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.12);
	min-width: 300rpx;
}

.detail-time {
	font-size: 24rpx;
	color: #94a3b8;
	display: block;
	margin-bottom: 12rpx;
}

.detail-value {
	font-size: 56rpx;
	font-weight: 800;
	color: #0f172a;
	display: block;
	margin-bottom: 16rpx;
}

.detail-alert {
	font-size: 22rpx;
	font-weight: 600;
	padding: 6rpx 20rpx;
	border-radius: 999rpx;
	display: inline-block;

	&.high {
		color: #dc2626;
		background: #fef2f2;
	}

	&.low {
		color: #2563eb;
		background: #eff6ff;
	}
}

.detail-ok {
	font-size: 22rpx;
	font-weight: 600;
	color: #059669;
	background: #ecfdf5;
	padding: 6rpx 20rpx;
	border-radius: 999rpx;
	display: inline-block;
}

.log-section {
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(20px) saturate(180%);
	-webkit-backdrop-filter: blur(20px) saturate(180%);
	border-radius: 24rpx;
	padding: 24rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.25);
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08), inset 0 1rpx 0 rgba(255, 255, 255, 0.5);
}

.log-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
	font-weight: 700;
	color: #1a1a2e;
	font-size: 28rpx;
}

.log-actions {
	display: flex;
	align-items: center;
	gap: 12rpx;
}

.count-tag {
	background: rgba(26, 26, 46, 0.1);
	padding: 6rpx 16rpx;
	border-radius: 999rpx;
	font-size: 20rpx;
	color: rgba(26, 26, 46, 0.7);
	font-weight: 500;
}

.clear-btn {
	background: rgba(220, 38, 38, 0.15);
	color: #dc2626;
	padding: 6rpx 18rpx;
	border-radius: 999rpx;
	font-size: 20rpx;
	font-weight: 600;
}

.log-item {
	display: flex;
	padding: 24rpx 8rpx;
	border-bottom: 1rpx solid rgba(255, 255, 255, 0.1);

	&:last-child {
		border-bottom: none;
	}
}

.log-status {
	width: 160rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	font-size: 20rpx;
	font-weight: 600;
	gap: 6rpx;

	&.light {
		color: #fcd34d;
	}

	&.recovery {
		color: #6ee7b7;
	}

	&.severe {
		color: #fca5a5;
	}
}

.log-dot {
	width: 10rpx;
	height: 10rpx;
	border-radius: 5rpx;
}

.log-status.light .log-dot {
	background: #fcd34d;
}

.log-status.recovery .log-dot {
	background: #6ee7b7;
}

.log-status.severe .log-dot {
	background: #fca5a5;
}

.log-info {
	margin-left: 20rpx;
	flex: 1;

	.log-title {
		font-size: 26rpx;
		color: #1a1a2e;
		font-weight: 600;
		display: block;
	}

	.log-time {
		font-size: 22rpx;
		color: rgba(26, 26, 46, 0.55);
		margin-top: 4rpx;
	}
}

.empty {
	padding: 36rpx;
	color: rgba(26, 26, 46, 0.5);
	font-size: 24rpx;
	text-align: center;
}
</style>
