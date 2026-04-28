<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { deviceStore } from "@/store/device";

onLaunch(() => {
	console.log("App Launch: 正在初始化云端连接...");
	deviceStore.init();
});

onShow(() => {
	console.log("App Show: 进入前台");
	deviceStore.fetchOnlineStatus();
	// 增量同步云端历史数据
	deviceStore.fetchCloudHistory().catch(err => {
		console.warn('[Cloud] Incremental sync failed:', err);
	});
});

onHide(() => {
	console.log("App Hide: 进入后台");
});
</script>

<style lang="scss">
page {
	background-color: #f1f5f9;
	font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Helvetica, Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei', sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
}
::-webkit-scrollbar {
	display: none;
	width: 0 !important;
	height: 0 !important;
	-webkit-appearance: none;
	background: transparent;
}
</style>