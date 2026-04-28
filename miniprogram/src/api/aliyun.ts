import CryptoJS from 'crypto-js';

// 阿里云 IoT API 配置 (请替换为实际值)
const AccessKeyId = 'YOUR_ACCESS_KEY_ID';
const AccessKeySecret = 'YOUR_ACCESS_KEY_SECRET';

/** URL 编码（保留 ~ 不编码） */
function specialEncode(str: string) {
    return encodeURIComponent(str).replace(/\+/g, '%20').replace(/\*/g, '%2A').replace(/%7E/g, '~');
}

/** 计算阿里云 API 签名 */
function computeSignature(params: any) {
    const sortedKeys = Object.keys(params).sort();
    let canonicalizedQueryString = "";
    for (const key of sortedKeys) {
        canonicalizedQueryString += "&" + specialEncode(key) + "=" + specialEncode(params[key].toString());
    }
    const stringToSign = "GET&%2F&" + specialEncode(canonicalizedQueryString.substring(1));
    return CryptoJS.HmacSHA1(stringToSign, AccessKeySecret + "&").toString(CryptoJS.enc.Base64);
}

/** 调用阿里云 IoT API */
export async function callAliyunIot(action: string, extraParams: any) {
    const params: any = {
        Action: action,
        Format: 'JSON',
        Version: '2018-01-20',  // IoT 物联网平台 API 版本
        AccessKeyId: AccessKeyId,
        SignatureMethod: 'HMAC-SHA1',
        Timestamp: new Date().toISOString(),
        SignatureVersion: '1.0',
        SignatureNonce: Math.random().toString(36).substring(2),
        RegionId: 'cn-shanghai',
        ...extraParams
    };
    params.Signature = computeSignature(params);
    
    // 调试日志
    console.log('[API] Calling:', action);
    console.log('[API] Params:', JSON.stringify({
        ProductKey: extraParams.ProductKey,
        DeviceName: extraParams.DeviceName,
        Identifier: extraParams.Identifier
    }));
    
    return new Promise((resolve, reject) => {
        uni.request({
            url: 'https://iot.cn-shanghai.aliyuncs.com',
            data: params,
            success: (res) => {
                console.log('[API] Response:', JSON.stringify(res.data).substring(0, 300));
                resolve(res.data);
            },
            fail: (err) => {
                console.error('[API] Request failed:', err);
                reject(err);
            }
        });
    });
}