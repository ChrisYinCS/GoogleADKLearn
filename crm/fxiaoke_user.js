const axios = require('axios');

/**
 * 纷享销客用户管理类
 * 负责调用用户相关的API接口
 */
class FxiaokeUserManager {
    constructor(authManager) {
        this.authManager = authManager;
        
        // 请求配置
        this.requestConfig = {
            baseURL: 'https://open.fxiaoke.com',
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // 重试配置
        this.retryConfig = {
            maxRetries: 3,
            retryDelay: 1000, // 1秒
            backoffMultiplier: 2
        };
        
        // 频率限制配置
        this.rateLimitConfig = {
            maxRequestsPerWindow: 100,
            windowSize: 20000, // 20秒
            requestQueue: [],
            lastRequestTime: 0
        };
    }

    /**
     * 根据手机号获取用户信息
     * @param {string} mobile 手机号
     * @returns {Promise<Object>} 用户信息
     */
    async getUserByMobile(mobile) {
        try {
            // 验证参数
            this.validateMobile(mobile);
            
            // 获取认证信息
            const authInfo = await this.authManager.getCorpAccessToken();
            
            // 构建请求数据
            const requestData = {
                corpAccessToken: authInfo.corpAccessToken,
                corpId: authInfo.corpId,
                mobile: mobile
            };
            
            // 发送请求
            const response = await this.requestWithRateLimit(
                '/cgi/user/getByMobile',
                requestData
            );
            
            // 检查API错误
            if (response.errorCode !== 0) {
                throw new Error(`API错误: ${response.errorCode} - ${response.errorMessage || response.errorDescription}`);
            }
            
            return response;
            
        } catch (error) {
            console.error('[FxiaokeUser] 获取用户信息失败:', error.message);
            throw error;
        }
    }

    /**
     * 带频率限制的请求方法
     * @param {string} endpoint API端点
     * @param {Object} data 请求数据
     * @returns {Promise<Object>} API响应
     */
    async requestWithRateLimit(endpoint, data) {
        // 检查频率限制
        await this.checkRateLimit();
        
        // 发送请求
        const response = await this.requestWithRetry(endpoint, data);
        
        // 更新请求时间
        this.rateLimitConfig.lastRequestTime = Date.now();
        
        return response;
    }

    /**
     * 检查频率限制
     */
    async checkRateLimit() {
        const now = Date.now();
        const timeSinceLastRequest = now - this.rateLimitConfig.lastRequestTime;
        
        // 如果距离上次请求时间小于窗口大小，需要等待
        if (timeSinceLastRequest < this.rateLimitConfig.windowSize) {
            const waitTime = this.rateLimitConfig.windowSize - timeSinceLastRequest;
            console.log(`[FxiaokeUser] 频率限制，等待 ${waitTime}ms`);
            await this.sleep(waitTime);
        }
    }

    /**
     * 带重试机制的请求
     * @param {string} endpoint API端点
     * @param {Object} data 请求数据
     * @returns {Promise<Object>} API响应
     */
    async requestWithRetry(endpoint, data) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryConfig.maxRetries; attempt++) {
            try {
                const response = await axios.post(
                    endpoint,
                    data,
                    this.requestConfig
                );
                
                return response.data;
                
            } catch (error) {
                lastError = error;
                console.warn(`[FxiaokeUser] 第${attempt}次请求失败:`, error.message);
                
                // 如果是最后一次尝试，抛出错误
                if (attempt === this.retryConfig.maxRetries) {
                    break;
                }
                
                // 计算延迟时间（指数退避）
                const delay = this.retryConfig.retryDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt - 1);
                console.log(`[FxiaokeUser] ${delay}ms后重试...`);
                await this.sleep(delay);
            }
        }
        
        throw new Error(`请求失败，已重试${this.retryConfig.maxRetries}次: ${lastError.message}`);
    }

    /**
     * 验证手机号格式
     * @param {string} mobile 手机号
     */
    validateMobile(mobile) {
        if (!mobile) {
            throw new Error('手机号不能为空');
        }
        
        // 简单的手机号格式验证（中国大陆手机号）
        const mobileRegex = /^1[3-9]\d{9}$/;
        if (!mobileRegex.test(mobile)) {
            throw new Error('手机号格式不正确');
        }
    }

    /**
     * 获取用户信息并提取currentOpenUserId
     * @param {string} mobile 手机号
     * @returns {Promise<string>} currentOpenUserId
     */
    async getCurrentOpenUserId(mobile) {
        try {
            const userInfo = await this.getUserByMobile(mobile);
            
            // 检查返回的用户信息中是否包含empList
            if (userInfo.empList && userInfo.empList.length > 0) {
                const user = userInfo.empList[0]; // 取第一个匹配的用户
                
                // 检查是否有openUserId字段
                if (user.openUserId) {
                    return user.openUserId;
                }
                
                throw new Error('用户信息中未找到openUserId字段');
            }
            
            // 如果没有找到用户信息，抛出错误
            throw new Error('未找到匹配的用户信息，请检查手机号是否正确');
            
        } catch (error) {
            console.error('[FxiaokeUser] 获取currentOpenUserId失败:', error.message);
            throw error;
        }
    }

    /**
     * 获取用户详细信息
     * @param {string} mobile 手机号
     * @returns {Promise<Object>} 用户详细信息
     */
    async getUserDetail(mobile) {
        try {
            const userInfo = await this.getUserByMobile(mobile);
            
            // 检查返回的用户信息中是否包含empList
            if (userInfo.empList && userInfo.empList.length > 0) {
                const user = userInfo.empList[0]; // 取第一个匹配的用户
                return {
                    ...user,
                    traceId: userInfo.traceId,
                    errorCode: userInfo.errorCode,
                    errorMessage: userInfo.errorMessage
                };
            }
            
            throw new Error('未找到匹配的用户信息，请检查手机号是否正确');
            
        } catch (error) {
            console.error('[FxiaokeUser] 获取用户详细信息失败:', error.message);
            throw error;
        }
    }

    /**
     * 批量获取用户信息
     * @param {Array<string>} mobiles 手机号数组
     * @returns {Promise<Array>} 用户信息数组
     */
    async batchGetUsersByMobile(mobiles) {
        const results = [];
        
        for (const mobile of mobiles) {
            try {
                const userInfo = await this.getUserByMobile(mobile);
                results.push({
                    mobile,
                    success: true,
                    data: userInfo
                });
            } catch (error) {
                results.push({
                    mobile,
                    success: false,
                    error: error.message
                });
            }
        }
        
        return results;
    }

    /**
     * 设置重试配置
     * @param {Object} config 重试配置
     */
    setRetryConfig(config) {
        this.retryConfig = { ...this.retryConfig, ...config };
    }

    /**
     * 设置频率限制配置
     * @param {Object} config 频率限制配置
     */
    setRateLimitConfig(config) {
        this.rateLimitConfig = { ...this.rateLimitConfig, ...config };
    }

    /**
     * 设置请求超时时间
     * @param {number} timeout 超时时间（毫秒）
     */
    setTimeout(timeout) {
        this.requestConfig.timeout = timeout;
    }

    /**
     * 延迟函数
     * @param {number} ms 延迟时间（毫秒）
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 销毁实例，清理资源
     */
    destroy() {
        // 清理定时器和队列
        this.rateLimitConfig.requestQueue = [];
        console.log('[FxiaokeUser] 实例已销毁');
    }
}

module.exports = FxiaokeUserManager;