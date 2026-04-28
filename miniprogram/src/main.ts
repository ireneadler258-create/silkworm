import { createSSRApp } from "vue";
import * as Pinia from 'pinia'; // 必须这样引入
import App from "./App.vue";

export function createApp() {
  const app = createSSRApp(App);

  // 创建 pinia 实例
  const pinia = Pinia.createPinia();
  app.use(pinia);

  return {
    app,
    Pinia, // 必须返回，UniApp 编译需要
  };
}