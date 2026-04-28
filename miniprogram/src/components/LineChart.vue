<template>
  <view class="chart-wrap">
    <view class="y-axis" :style="{ height: `${height}px` }">
      <text
        v-for="(label, index) in yLabels"
        :key="index"
        class="y-label"
        :style="{ top: `${label.y}px` }"
      >{{ label.text }}</text>
    </view>

    <view class="chart-scroll-area">
      <scroll-view
        class="scroll"
        scroll-x
        :show-scrollbar="false"
        :scroll-left="scrollLeft"
      >
        <view class="canvas-stack" :style="{ width: `${canvasWidth}px`, height: `${height}px` }">
          <canvas
            class="canvas"
            :canvas-id="canvasId"
            :id="canvasId"
            :style="{ width: `${canvasWidth}px`, height: `${height}px` }"
          />

          <view
            v-for="dot in clickableDots"
            :key="dot.originalIndex"
            class="dot-hitbox"
            :class="{ selected: selectedSourceIndex === dot.originalIndex, alert: dot.isAlert, below: dot.tooltipBelow }"
            :style="{ left: `${dot.hitLeft}px`, top: `${dot.hitTop}px`, width: `${dot.hitWidth}px`, height: `${dot.hitHeight}px` }"
            @tap="onDotTap(dot.originalIndex)"
          >
            <view class="dot-anchor" :style="{ left: `${dot.anchorLeft}px`, top: `${dot.anchorTop}px` }"></view>
            <view v-if="selectedSourceIndex === dot.originalIndex" class="dot-tooltip">
              <text class="dot-tooltip-text">{{ dot.rawLabel }}</text>
            </view>
          </view>
        </view>
      </scroll-view>

      <view v-if="overlayTitle" class="state-overlay" :class="overlayClass">
        <text class="state-title">{{ overlayTitle }}</text>
        <text class="state-desc">{{ overlayDescription }}</text>
      </view>

      <view v-else-if="chartState === 'low-data' && helperText" class="state-pill">
        <text class="state-pill-text">{{ helperText }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';

type ChartState = 'loading' | 'empty' | 'low-data' | 'ready';
type ChartMode = 'compact' | 'expanded';
type RangeHours = 1 | 6 | 24 | 168;
type RenderPoint = {
  originalIndex: number;
  x: number;
  y: number;
  rawValue: number;
  displayValue: number;
  time: string;
  isHighAlert: boolean;
  isLowAlert: boolean;
  isAlert: boolean;
  isClamped: boolean;
};
type YLabel = { y: number; text: string };

type ClickableDot = {
  originalIndex: number;
  x: number;
  y: number;
  rawLabel: string;
  isAlert: boolean;
  tooltipBelow: boolean;
  hitLeft: number;
  hitTop: number;
  hitWidth: number;
  hitHeight: number;
  anchorLeft: number;
  anchorTop: number;
};

const props = defineProps<{
  canvasId: string;
  width: number;
  height: number;
  categories: string[];
  values: number[];
  unit?: string;
  lineColor?: string;
  fillColor?: string;
  highTh?: number;
  lowTh?: number;
  emptyText?: string;
  state?: ChartState;
  statusTitle?: string;
  helperText?: string;
  mode?: ChartMode;
  rangeHours?: RangeHours;
}>();

const emit = defineEmits<{
  (e: 'pointTap', info: { index: number; value: number; time: string; isHighAlert: boolean; isLowAlert: boolean }): void;
}>();

const padL = 10;
const padR = 20;
const padT = 18;
const padB = 42;
const gridRows = 4;
const scrollLeft = ref(0);

const chartState = computed<ChartState>(() => props.state ?? (props.values.length < 2 ? 'empty' : 'ready'));
const chartMode = computed<ChartMode>(() => props.mode ?? 'compact');
const rangeHours = computed<RangeHours>(() => props.rangeHours ?? (chartMode.value === 'compact' ? 1 : 24));
const isCompact = computed(() => chartMode.value === 'compact');
const safeNum = (value: unknown) => (typeof value === 'number' && !Number.isNaN(value) ? value : 0);
const rawValues = computed(() => props.values.map(safeNum));
const seriesLength = computed(() => rawValues.value.length);
const hasDrawableSeries = computed(() => (chartState.value === 'ready' || chartState.value === 'low-data') && seriesLength.value >= 2);

const rangeConfig = computed(() => {
  switch (rangeHours.value) {
    case 1:
      return { labelCount: 5, interactiveCount: 8, pointSpacing: 34, widthFactor: 1.9, smoothWeight: 0.28 };
    case 6:
      return { labelCount: 6, interactiveCount: 10, pointSpacing: 30, widthFactor: 2.1, smoothWeight: 0.24 };
    case 24:
      return { labelCount: 6, interactiveCount: 12, pointSpacing: 26, widthFactor: 2.35, smoothWeight: 0.18 };
    case 168:
    default:
      return { labelCount: 7, interactiveCount: 14, pointSpacing: 22, widthFactor: 2.6, smoothWeight: 0.14 };
  }
});

function hexToRgba(hex: string, alpha: number): string {
  if (!hex.startsWith('#') || hex.length !== 7) return `rgba(59,130,246,${alpha})`;
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function formatYValue(value: number): string {
  if (Math.abs(value) >= 1000) return `${(value / 1000).toFixed(1)}k`;
  if (Math.abs(value) >= 100) return value.toFixed(0);
  return value.toFixed(1);
}

const canvasWidth = computed(() => {
  const baseWidth = Math.max(props.width, 280);
  const pointDrivenWidth = Math.max(baseWidth + 60, seriesLength.value * rangeConfig.value.pointSpacing + padL + padR);
  const widthCap = Math.round(baseWidth * rangeConfig.value.widthFactor);
  return Math.max(baseWidth + 40, Math.min(pointDrivenWidth, widthCap));
});

function computeDisplayValues(values: number[]): number[] {
  if (values.length <= 2) return values.slice();
  const smoothed = values.slice();
  for (let index = 1; index < values.length - 1; index += 1) {
    const prev = values[index - 1];
    const current = values[index];
    const next = values[index + 1];
    const neighborMean = (prev + next) / 2;
    const localDelta = Math.abs(current - neighborMean);
    const neighborDelta = Math.abs(prev - next);
    const outlierThreshold = Math.max(6, Math.max(Math.abs(neighborMean) * 0.2, neighborDelta * 3));
    if (localDelta > outlierThreshold) {
      smoothed[index] = neighborMean;
      continue;
    }
    smoothed[index] = current * (1 - rangeConfig.value.smoothWeight) + neighborMean * rangeConfig.value.smoothWeight;
  }
  return smoothed;
}

const displayValues = computed(() => computeDisplayValues(rawValues.value));

const valueRange = computed(() => {
  if (!hasDrawableSeries.value) return null;
  const values = displayValues.value;
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (min === max) {
    min -= 1;
    max += 1;
  }
  const padding = Math.max((max - min) * 0.16, Math.abs(max) * 0.03, 1);
  const paddedMin = min - padding;
  const paddedMax = max + padding;
  return {
    min: paddedMin,
    max: paddedMax,
    span: paddedMax - paddedMin
  };
});

const plotMetrics = computed(() => {
  const plotW = canvasWidth.value - padL - padR;
  const plotH = props.height - padT - padB;
  const step = seriesLength.value > 1 ? plotW / (seriesLength.value - 1) : 0;
  return { plotW, plotH, step };
});

const renderPoints = computed<RenderPoint[]>(() => {
  if (!hasDrawableSeries.value || !valueRange.value) return [];
  return rawValues.value.map((rawValue, originalIndex) => {
    const displayValue = displayValues.value[originalIndex] ?? rawValue;
    const clampedValue = Math.min(valueRange.value!.max, Math.max(valueRange.value!.min, displayValue));
    const x = padL + originalIndex * plotMetrics.value.step;
    const y = padT + (1 - (clampedValue - valueRange.value!.min) / valueRange.value!.span) * plotMetrics.value.plotH;
    const isHighAlert = props.highTh !== undefined && rawValue > props.highTh;
    const isLowAlert = props.lowTh !== undefined && rawValue < props.lowTh;
    return {
      originalIndex,
      x,
      y,
      rawValue,
      displayValue,
      time: props.categories[originalIndex] ?? '',
      isHighAlert,
      isLowAlert,
      isAlert: isHighAlert || isLowAlert,
      isClamped: clampedValue !== displayValue
    };
  });
});

const yLabels = computed<YLabel[]>(() => {
  if (!valueRange.value) return [];
  const labels: YLabel[] = [];
  for (let index = 0; index <= gridRows; index += 1) {
    const y = padT + (plotMetrics.value.plotH * index) / gridRows;
    const value = valueRange.value.max - (valueRange.value.span * index) / gridRows;
    labels.push({ y: y - 6, text: formatYValue(value) });
  }
  return labels;
});

function pickEvenlySpacedIndices(total: number, count: number) {
  if (total <= 0) return [] as number[];
  if (total <= count) return Array.from({ length: total }, (_, index) => index);
  const indices: number[] = [];
  const denominator = Math.max(1, count - 1);
  for (let slot = 0; slot < count; slot += 1) {
    indices.push(Math.round((slot * (total - 1)) / denominator));
  }
  return Array.from(new Set(indices)).sort((a, b) => a - b);
}

const xLabelIndices = computed(() => pickEvenlySpacedIndices(seriesLength.value, rangeConfig.value.labelCount));
const interactiveIndices = computed(() => {
  const base = pickEvenlySpacedIndices(seriesLength.value, rangeConfig.value.interactiveCount);
  const selected = selectedSourceIndex.value;
  if (selected !== null && !base.includes(selected)) base.push(selected);
  return Array.from(new Set(base)).sort((a, b) => a - b);
});

const selectedSourceIndex = ref<number | null>(null);

const clickableDots = computed<ClickableDot[]>(() => {
  if (!hasDrawableSeries.value) return [];
  const step = plotMetrics.value.step || 36;
  const hitWidth = Math.max(40, Math.min(68, step * 1.45));
  const hitHeight = Math.max(60, Math.min(88, props.height - padB));
  return interactiveIndices.value.map((originalIndex) => {
    const point = renderPoints.value[originalIndex];
    return {
      originalIndex,
      x: point.x,
      y: point.y,
      rawLabel: point.rawValue.toFixed(1),
      isAlert: point.isAlert,
      tooltipBelow: point.y < padT + 26,
      hitLeft: Math.max(0, point.x - hitWidth / 2),
      hitTop: Math.max(0, point.y - hitHeight / 2),
      hitWidth,
      hitHeight,
      anchorLeft: hitWidth / 2 - 8,
      anchorTop: hitHeight / 2 - 8
    };
  });
});

const overlayTitle = computed(() => {
  if (props.statusTitle) return props.statusTitle;
  if (chartState.value === 'loading') return 'Loading history';
  if (chartState.value === 'empty') return props.emptyText ?? 'No data available';
  return '';
});

const overlayDescription = computed(() => {
  if (chartState.value === 'loading') return props.helperText ?? 'Preparing the latest chart data';
  if (chartState.value === 'empty') return props.helperText ?? 'No samples in the selected range yet';
  return '';
});

const overlayClass = computed(() => `is-${chartState.value}`);

function drawBase(ctx: UniApp.CanvasContext, width: number, height: number) {
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, 'rgba(15, 23, 42, 0.08)');
  gradient.addColorStop(1, 'rgba(15, 23, 42, 0.18)');
  ctx.setFillStyle(gradient);
  ctx.fillRect(0, 0, width, height);
}

function drawGrid(ctx: UniApp.CanvasContext, width: number) {
  ctx.setStrokeStyle('rgba(255, 255, 255, 0.12)');
  ctx.setLineWidth(0.8);
  for (let row = 0; row <= gridRows; row += 1) {
    const y = padT + (plotMetrics.value.plotH * row) / gridRows;
    ctx.beginPath();
    ctx.moveTo(padL, y);
    ctx.lineTo(width - padR, y);
    ctx.stroke();
  }
}

function drawThreshold(ctx: UniApp.CanvasContext, threshold: number | undefined, color: string, label: string, width: number) {
  if (threshold === undefined || !valueRange.value) return;
  if (threshold < valueRange.value.min || threshold > valueRange.value.max) return;
  const y = padT + (1 - (threshold - valueRange.value.min) / valueRange.value.span) * plotMetrics.value.plotH;
  ctx.setStrokeStyle(hexToRgba(color, 0.68));
  ctx.setLineWidth(1);
  ctx.setLineDash([5, 5], 0);
  ctx.beginPath();
  ctx.moveTo(padL, y);
  ctx.lineTo(width - padR, y);
  ctx.stroke();
  ctx.setLineDash([], 0);
  ctx.setFillStyle(hexToRgba(color, 0.92));
  ctx.setFontSize(8);
  ctx.fillText(label, padL + 4, y - 6);
}

function drawXAxisLabels(ctx: UniApp.CanvasContext) {
  if (renderPoints.value.length === 0) return;
  ctx.setFillStyle('rgba(248, 250, 252, 0.92)');
  ctx.setFontSize(9);
  for (const [position, originalIndex] of xLabelIndices.value.entries()) {
    const point = renderPoints.value[originalIndex];
    if (!point) continue;
    const text = point.time;
    let drawX = point.x - 16;
    if (position === 0) drawX = padL;
    else if (position === xLabelIndices.value.length - 1) drawX = Math.max(padL, point.x - 34);
    ctx.fillText(text, drawX, props.height - 9);
  }
}

function drawAreaAndLine(ctx: UniApp.CanvasContext, points: RenderPoint[]) {
  if (points.length < 2) return;
  const fillColor = props.fillColor ?? props.lineColor ?? '#10b981';

  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let index = 1; index < points.length; index += 1) {
    const previous = points[index - 1];
    const current = points[index];
    const cpx = (previous.x + current.x) / 2;
    const cpy = (previous.y + current.y) / 2;
    ctx.quadraticCurveTo(previous.x, previous.y, cpx, cpy);
  }
  const last = points[points.length - 1];
  ctx.lineTo(last.x, last.y);
  ctx.lineTo(last.x, padT + plotMetrics.value.plotH);
  ctx.lineTo(points[0].x, padT + plotMetrics.value.plotH);
  ctx.closePath();

  const gradient = ctx.createLinearGradient(0, padT, 0, padT + plotMetrics.value.plotH);
  gradient.addColorStop(0, hexToRgba(fillColor, chartState.value === 'low-data' ? 0.2 : 0.16));
  gradient.addColorStop(1, hexToRgba(fillColor, 0.03));
  ctx.setFillStyle(gradient);
  ctx.fill();

  ctx.setStrokeStyle(props.lineColor ?? '#10b981');
  ctx.setLineWidth(chartState.value === 'low-data' ? 3 : 2.4);
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let index = 1; index < points.length; index += 1) {
    const previous = points[index - 1];
    const current = points[index];
    const cpx = (previous.x + current.x) / 2;
    const cpy = (previous.y + current.y) / 2;
    ctx.quadraticCurveTo(previous.x, previous.y, cpx, cpy);
  }
  ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y);
  ctx.stroke();
}

function drawMarkers(ctx: UniApp.CanvasContext, points: RenderPoint[]) {
  const sampled = new Set(interactiveIndices.value);
  for (const point of points) {
    const shouldDraw = sampled.has(point.originalIndex) || point.originalIndex === selectedSourceIndex.value;
    if (!shouldDraw) continue;
    const markerColor = point.isHighAlert ? '#ef4444' : point.isLowAlert ? '#3b82f6' : (props.lineColor ?? '#10b981');
    ctx.beginPath();
    ctx.arc(point.x, point.y, 4.4, 0, Math.PI * 2);
    ctx.setFillStyle('#ffffff');
    ctx.fill();
    ctx.beginPath();
    ctx.arc(point.x, point.y, 2.9, 0, Math.PI * 2);
    ctx.setFillStyle(markerColor);
    ctx.fill();
  }
}

function drawSelection(ctx: UniApp.CanvasContext, points: RenderPoint[]) {
  if (selectedSourceIndex.value === null) return;
  const point = points.find((item) => item.originalIndex === selectedSourceIndex.value);
  if (!point) return;
  ctx.setStrokeStyle('rgba(255, 255, 255, 0.3)');
  ctx.setLineWidth(1);
  ctx.setLineDash([4, 4], 0);
  ctx.beginPath();
  ctx.moveTo(point.x, padT);
  ctx.lineTo(point.x, padT + plotMetrics.value.plotH);
  ctx.stroke();
  ctx.setLineDash([], 0);

  ctx.beginPath();
  ctx.arc(point.x, point.y, 6, 0, Math.PI * 2);
  ctx.setFillStyle(hexToRgba(props.lineColor ?? '#10b981', 0.18));
  ctx.fill();
}

function draw() {
  const ctx = uni.createCanvasContext(props.canvasId);
  drawBase(ctx, canvasWidth.value, props.height);
  if (!hasDrawableSeries.value || !valueRange.value) {
    ctx.draw();
    return;
  }

  drawGrid(ctx, canvasWidth.value);
  drawThreshold(ctx, props.highTh, '#ef4444', 'High', canvasWidth.value);
  drawThreshold(ctx, props.lowTh, '#3b82f6', 'Low', canvasWidth.value);
  drawAreaAndLine(ctx, renderPoints.value);
  drawMarkers(ctx, renderPoints.value);
  drawSelection(ctx, renderPoints.value);
  drawXAxisLabels(ctx);
  ctx.draw();
}

function onDotTap(originalIndex: number) {
  const point = renderPoints.value.find((item) => item.originalIndex === originalIndex);
  if (!point) return;
  selectedSourceIndex.value = originalIndex;
  draw();
  emit('pointTap', {
    index: originalIndex,
    value: point.rawValue,
    time: point.time,
    isHighAlert: point.isHighAlert,
    isLowAlert: point.isLowAlert
  });
}

function syncInitialViewport() {
  const overflow = Math.max(0, canvasWidth.value - props.width);
  scrollLeft.value = overflow;
}

async function redraw() {
  await nextTick();
  if (selectedSourceIndex.value !== null && selectedSourceIndex.value >= seriesLength.value) {
    selectedSourceIndex.value = null;
  }
  syncInitialViewport();
  draw();
}

onMounted(() => {
  redraw();
});

watch(
  () => [props.categories, props.values, props.width, props.height, props.state, props.helperText, props.highTh, props.lowTh, props.mode, props.rangeHours],
  () => {
    redraw();
  },
  { deep: true }
);
</script>

<style scoped>
.chart-wrap {
  width: 100%;
  display: flex;
  flex-direction: row;
}

.y-axis {
  width: 72rpx;
  position: relative;
  flex-shrink: 0;
}

.y-label {
  position: absolute;
  right: 8rpx;
  font-size: 16rpx;
  color: rgba(15, 23, 42, 0.74);
  font-weight: 600;
}

.chart-scroll-area {
  flex: 1;
  overflow: hidden;
  position: relative;
  border-radius: 22rpx;
}

.scroll {
  width: 100%;
  height: 100%;
}

.canvas-stack {
  position: relative;
}

.canvas {
  display: block;
}

.dot-hitbox {
  position: absolute;
  z-index: 10;
}

.dot-hitbox.selected {
  z-index: 12;
}

.dot-hitbox.below {
  z-index: 13;
}

.dot-anchor {
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
}

.dot-hitbox.selected .dot-anchor {
  background: rgba(16, 185, 129, 0.12);
}

.dot-hitbox.alert .dot-anchor {
  background: rgba(239, 68, 68, 0.1);
}

.dot-tooltip {
  position: absolute;
  left: 50%;
  top: -42px;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.97);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 6px 10px;
  white-space: nowrap;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.82);
}

.dot-hitbox.below .dot-tooltip {
  top: auto;
  bottom: -42px;
}

.dot-tooltip-text {
  font-size: 20rpx;
  color: #0f172a;
  font-weight: 700;
}

.state-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 10rpx;
  border-radius: 22rpx;
  padding: 30rpx;
  backdrop-filter: blur(8px);
}

.state-overlay.is-loading {
  background: linear-gradient(180deg, rgba(219, 234, 254, 0.4), rgba(239, 246, 255, 0.54));
}

.state-overlay.is-empty {
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.52), rgba(241, 245, 249, 0.66));
}

.state-title {
  font-size: 28rpx;
  color: #0f172a;
  font-weight: 700;
}

.state-desc {
  font-size: 22rpx;
  line-height: 1.5;
  color: rgba(15, 23, 42, 0.68);
  max-width: 88%;
}

.state-pill {
  position: absolute;
  left: 18rpx;
  top: 14rpx;
  border-radius: 999rpx;
  background: rgba(255, 247, 237, 0.92);
  border: 1px solid rgba(245, 158, 11, 0.18);
  padding: 10rpx 18rpx;
  box-shadow: 0 8px 24px rgba(180, 83, 9, 0.08);
}

.state-pill-text {
  font-size: 20rpx;
  color: #b45309;
  font-weight: 700;
}
</style>
