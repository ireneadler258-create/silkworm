/// <reference types="vite/client" />

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 解决 mqtt/min.js 在 TS 下无类型声明的问题
declare module 'mqtt/dist/mqtt.min.js' {
  import * as mqtt from 'mqtt';
  export = mqtt;
}

// 如果 CryptoJS 类型丢失，可通过该声明兜底
declare module 'crypto-js';

// uni-app plus 对象（原生 App 环境）
declare const plus: any;
