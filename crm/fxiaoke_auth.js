const axios = require('axios');
const crypto = require('crypto');

/**
 * 纷享销客CRM授权管理类
 * 负责获取、缓存和自动刷新企业访问令牌
 */
class FxiaokeAuthManager {
    constructor(config = {}) {
        this.appId = config.appId;
        this.appSecret = config.appSecret;
        this.permanentCode = config.permanentCode;
        
        // 缓存相关
        this.tokenCache = {
            corpAccessToken: null,
            corpId: null,
            expiresIn: null,
            createdAt: null,
            lastRefreshTime: null
        };
        
        // 重试配置
        this.retryConfig = {
            maxRetries: 3,
            retryDelay: 1000, // 1秒
            backoffMultiplier: 2
        };
        
        // 时间配置（秒）
        this.timeConfig = {
            cacheMinTime: 6600,    // 最小缓存时间
            refreshWindowStart: 6650, // 开始刷新窗口
            refreshWindowEnd: 7200,   // 结束刷新窗口
            maxTokenLifetime: 7200    // 最大token生命周期
        };
        
        // 请求配置
        this.requestConfig = {
            baseURL: 'https://open.fxiaoke.com',
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json'
            }
        };
    }

    /**
     * 获取企业访问令牌
     * @returns {Promise<Object>} 返回token信息
     */
    async getCorpAccessToken() {
        try {
            // 检查缓存是否有效
            if (this.isTokenValid()) {
                console.log('[FxiaokeAuth] 使用缓存的token');
                return this.tokenCache;
            }

            // 检查是否需要刷新
            if (this.shouldRefreshToken()) {
                console.log('[FxiaokeAuth] 开始刷新token');
            } else {
                console.log('[FxiaokeAuth] 获取新token');
            }

            // 请求新token
            const tokenData = await this.requestTokenWithRetry();
            
            // 更新缓存
            this.updateTokenCache(tokenData);
            
            console.log('[FxiaokeAuth] Token获取成功，过期时间:', tokenData.expiresIn, '秒');
            return this.tokenCache;
            
        } catch (error) {
            console.error('[FxiaokeAuth] 获取token失败:', error.message);
            throw error;
        }
    }

    /**
     * 带重试机制的token请求
     * @returns {Promise<Object>} token数据
     */
    async requestTokenWithRetry() {
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryConfig.maxRetries; attempt++) {
            try {
                const response = await this.requestToken();
                
                // 检查错误码
                if (response.errorCode !== 0) {
                    throw new Error(`API错误: ${response.errorCode} - ${response.errorMessage}`);
                }
                
                return response;
                
            } catch (error) {
                lastError = error;
                console.warn(`[FxiaokeAuth] 第${attempt}次请求失败:`, error.message);
                
                // 如果是最后一次尝试，抛出错误
                if (attempt === this.retryConfig.maxRetries) {
                    break;
                }
                
                // 计算延迟时间（指数退避）
                const delay = this.retryConfig.retryDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt - 1);
                console.log(`[FxiaokeAuth] ${delay}ms后重试...`);
                await this.sleep(delay);
            }
        }
        
        throw new Error(`获取token失败，已重试${this.retryConfig.maxRetries}次: ${lastError.message}`);
    }

    /**
     * 发送token请求
     * @returns {Promise<Object>} API响应
     */
    async requestToken() {
        const requestData = {
            appId: this.appId,
            appSecret: this.appSecret,
            permanentCode: this.permanentCode
        };

        const response = await axios.post(
            '/cgi/corpAccessToken/get/V2',
            requestData,
            this.requestConfig
        );

        return response.data;
    }

    /**
     * 检查token是否有效
     * @returns {boolean}
     */
    isTokenValid() {
        if (!this.tokenCache.corpAccessToken || !this.tokenCache.createdAt) {
            return false;
        }

        const now = Date.now();
        const elapsed = (now - this.tokenCache.createdAt) / 1000;
        const remaining = this.tokenCache.expiresIn - elapsed;

        return remaining > 0;
    }

    /**
     * 检查是否需要刷新token
     * @returns {boolean}
     */
    shouldRefreshToken() {
        if (!this.tokenCache.createdAt || !this.tokenCache.expiresIn) {
            return false;
        }

        const now = Date.now();
        const elapsed = (now - this.tokenCache.createdAt) / 1000;
        const remaining = this.tokenCache.expiresIn - elapsed;

        // 在刷新窗口内且距离上次刷新超过一定时间
        const timeSinceLastRefresh = this.tokenCache.lastRefreshTime 
            ? (now - this.tokenCache.lastRefreshTime) / 1000 
            : Infinity;

        return remaining <= this.timeConfig.refreshWindowEnd && 
               remaining >= this.timeConfig.refreshWindowStart &&
               timeSinceLastRefresh > 60; // 至少间隔1分钟
    }

    /**
     * 更新token缓存
     * @param {Object} tokenData API返回的token数据
     */
    updateTokenCache(tokenData) {
        const now = Date.now();
        
        this.tokenCache = {
            corpAccessToken: tokenData.corpAccessToken,
            corpId: tokenData.corpId,
            expiresIn: parseInt(tokenData.expiresIn),
            createdAt: now,
            lastRefreshTime: now
        };

        // 设置自动刷新定时器
        this.scheduleTokenRefresh();
    }

    /**
     * 设置自动刷新定时器
     */
    scheduleTokenRefresh() {
        // 清除现有定时器
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
        }

        // 计算下次刷新时间
        const now = Date.now();
        const elapsed = (now - this.tokenCache.createdAt) / 1000;
        const remaining = this.tokenCache.expiresIn - elapsed;
        
        // 在刷新窗口中间点进行刷新
        const refreshTime = Math.max(0, remaining - (this.timeConfig.refreshWindowEnd - this.timeConfig.refreshWindowStart) / 2);
        
        console.log(`[FxiaokeAuth] 设置${refreshTime}秒后自动刷新token`);
        
        this.refreshTimer = setTimeout(async () => {
            try {
                console.log('[FxiaokeAuth] 执行自动刷新token');
                await this.getCorpAccessToken();
            } catch (error) {
                console.error('[FxiaokeAuth] 自动刷新token失败:', error.message);
            }
        }, refreshTime * 1000);
    }

    /**
     * 获取当前token信息
     * @returns {Object} token信息
     */
    getCurrentToken() {
        return {
            corpAccessToken: this.tokenCache.corpAccessToken,
            corpId: this.tokenCache.corpId,
            expiresIn: this.tokenCache.expiresIn,
            createdAt: this.tokenCache.createdAt,
            isValid: this.isTokenValid()
        };
    }

    /**
     * 强制刷新token
     * @returns {Promise<Object>} 新的token信息
     */
    async forceRefreshToken() {
        console.log('[FxiaokeAuth] 强制刷新token');
        
        // 清除缓存
        this.tokenCache = {
            corpAccessToken: null,
            corpId: null,
            expiresIn: null,
            createdAt: null,
            lastRefreshTime: null
        };
        
        // 清除定时器
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
        
        // 重新获取token
        return await this.getCorpAccessToken();
    }

    /**
     * 清理资源
     */
    destroy() {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    /**
     * 工具方法：延时
     * @param {number} ms 毫秒数
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 验证配置
     * @returns {boolean}
     */
    validateConfig() {
        if (!this.appId || !this.appSecret || !this.permanentCode) {
            throw new Error('缺少必要的配置参数: appId, appSecret, permanentCode');
        }
        return true;
    }
}

module.exports = FxiaokeAuthManager; 