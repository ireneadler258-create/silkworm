/**
 * WebSocket Polyfill for uni-app Native App
 * 
 * mqtt.js v4.x 在非浏览器环境中使用 Node.js 的 ws 库（需要底层 TCP/TLS），
 * uni-app 原生 App 没有这些依赖。
 * 
 * 本文件将 uni.connectSocket 包装为标准 WebSocket 接口，
 * 注入到 globalThis.WebSocket，让 mqtt.js 以为这是浏览器环境。
 * 
 * 必须在 device.ts 之前被导入！
 */

class UniWebSocket {
    private socketTask: any = null;
    private _onopen: ((ev: any) => void) | null = null;
    private _onmessage: ((ev: any) => void) | null = null;
    private _onerror: ((ev: any) => void) | null = null;
    private _onclose: ((ev: any) => void) | null = null;
    private _readyState: number = 0;
    public url: string;
    public bufferedAmount: number = 0;
    public binaryType: string = 'arraybuffer';

    // WebSocket 标准常量
    static readonly CONNECTING = 0;
    static readonly OPEN = 1;
    static readonly CLOSING = 2;
    static readonly CLOSED = 3;
    readonly OPEN = 1;
    readonly CLOSING = 2;
    readonly CLOSED = 3;

    constructor(url: string, protocols?: string | string[]) {
        this.url = url;
        this._readyState = 0;
        this._connect();
    }

    get readyState(): number { return this._readyState; }

    set onopen(handler: ((ev: any) => void) | null) {
        this._onopen = handler;
        if (this._readyState === 1 && handler) handler({ type: 'open', target: this });
    }
    get onopen() { return this._onopen; }

    set onmessage(handler: ((ev: any) => void) | null) { this._onmessage = handler; }
    get onmessage() { return this._onmessage; }

    set onerror(handler: ((ev: any) => void) | null) { this._onerror = handler; }
    get onerror() { return this._onerror; }

    set onclose(handler: ((ev: any) => void) | null) { this._onclose = handler; }
    get onclose() { return this._onclose; }

    private _connect() {
        this.socketTask = uni.connectSocket({
            url: this.url,
            complete: () => { }
        });

        this.socketTask.onOpen((res: any) => {
            this._readyState = 1;
            if (this._onopen) this._onopen({ type: 'open', target: this });
        });

        this.socketTask.onMessage((res: any) => {
            if (this._onmessage) {
                this._onmessage({ data: res.data, type: 'message', target: this });
            }
        });

        this.socketTask.onError((err: any) => {
            this._readyState = 3;
            if (this._onerror) this._onerror({ type: 'error', target: this });
        });

        this.socketTask.onClose((res: any) => {
            this._readyState = 3;
            if (this._onclose) this._onclose({
                code: res.code || 1000,
                reason: res.reason || '',
                wasClean: true,
                type: 'close',
                target: this
            });
        });
    }

    send(data: string | ArrayBuffer) {
        if (this._readyState !== 1) return;
        this.socketTask.send({ data });
    }

    close(code?: number, reason?: string) {
        this._readyState = 2;
        if (this.socketTask) {
            this.socketTask.close({ code: code || 1000, reason: reason || '' });
        }
    }
}

// 注入到全局：让 mqtt.js 以为这是浏览器环境
if (typeof (globalThis as any).WebSocket === 'undefined') {
    (globalThis as any).WebSocket = UniWebSocket;
    console.log('[UniWS] Injected WebSocket into globalThis');
}
