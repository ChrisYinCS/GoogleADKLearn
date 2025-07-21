const axios = require('axios');

/**
 * 纷享销客CRM业务对象数据查询类
 * 提供CRM业务对象的数据查询功能
 */
class FxiaokeCRMDataClient {
    constructor(authManager) {
        this.authManager = authManager;
        
        // 请求配置
        this.requestConfig = {
            baseURL: 'https://open.fxiaoke.com',
            timeout: 15000,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        // 重试配置
        this.retryConfig = {
            maxRetries: 3,
            retryDelay: 1000,
            backoffMultiplier: 2
        };
        
        // 频率限制配置（根据API文档：100次/20秒）
        this.rateLimitConfig = {
            maxRequestsPerWindow: 100,
            windowSize: 20000, // 20秒
            requestQueue: [],
            lastRequestTime: 0
        };
    }

    /**
     * 查询CRM业务对象数据
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID（通过手机号查询员工接口返回）
     * @param {string} params.dataObjectApiName 对象ApiName
     * @param {Array<string>} params.fieldProjection 返回数据中包含的字段，为空则返回所有字段
     * @param {Object} [params.searchQueryInfo] 查询条件
     * @param {number} [params.searchQueryInfo.limit] 查询条数
     * @param {number} [params.searchQueryInfo.offset] 查询开始偏移量
     * @param {Object} [params.searchQueryInfo.filters] 查询条件
     * @param {string} [params.searchQueryInfo.filters.field_name] 字段apiName
     * @param {Array<string>} [params.searchQueryInfo.filters.field_values] 字段值
     * @param {string} [params.searchQueryInfo.filters.operator] 操作符
     * @param {Array<Object>} [params.searchQueryInfo.orders] 排序
     * @param {string} [params.searchQueryInfo.orders.fieldName] 排序字段
     * @param {boolean} [params.searchQueryInfo.orders.isAsc] 是否升序
     * @param {boolean} [params.igonreMediaIdConvert=false] 是否忽略转换MediaId
     * @returns {Promise<Array>} 返回数据数组
     */
    async findSimpleData(params = {}) {
        try {
            // 验证必需参数
            this.validateParams(params);
            
            // 获取认证信息
            const authInfo = await this.authManager.getCorpAccessToken();
            
            // 构建请求数据
            const requestData = {
                corpAccessToken: authInfo.corpAccessToken,
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId,
                data: {
                    dataObjectApiName: params.dataObjectApiName,
                    field_projection: params.fieldProjection || [],
                    igonreMediaIdConvert: params.igonreMediaIdConvert || false,
                    search_query_info: this.buildSearchQueryInfo(params.searchQueryInfo)
                }
            };

            console.log('[FxiaokeCRMData] 请求业务对象数据，参数:', {
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId,
                dataObjectApiName: params.dataObjectApiName,
                fieldProjection: params.fieldProjection?.length || 0,
                limit: params.searchQueryInfo?.limit,
                offset: params.searchQueryInfo?.offset
            });

            // 发送请求
            const response = await this.requestWithRateLimit(
                '/cgi/crm/custom/v2/data/findSimple',
                requestData
            );
            
            console.log('[FxiaokeCRMData] 业务对象数据查询成功');
            
            // 提取数据数组并返回
            if (response.data && response.data.dataList) {
                return response.data.dataList;
            } else {
                console.warn('[FxiaokeCRMData] 响应中没有找到dataList，返回空数组');
                return [];
            }
            
        } catch (error) {
            console.error('[FxiaokeCRMData] 查询业务对象数据失败:', error.message);
            throw error;
        }
    }

    /**
     * 构建查询条件
     * @param {Object} searchQueryInfo 查询条件
     * @returns {Object} 构建后的查询条件
     */
    buildSearchQueryInfo(searchQueryInfo = {}) {
        const result = {};
        
        // 添加基本查询参数
        if (searchQueryInfo.limit !== undefined) {
            result.limit = searchQueryInfo.limit.toString();
        }
        
        if (searchQueryInfo.offset !== undefined) {
            result.offset = searchQueryInfo.offset.toString();
        }
        
        // 添加过滤条件
        if (searchQueryInfo.filters) {
            result.filters = {
                field_name: searchQueryInfo.filters.field_name,
                field_values: Array.isArray(searchQueryInfo.filters.field_values) 
                    ? searchQueryInfo.filters.field_values 
                    : [searchQueryInfo.filters.field_values],
                operator: searchQueryInfo.filters.operator
            };
        }
        
        // 添加排序条件
        if (searchQueryInfo.orders && Array.isArray(searchQueryInfo.orders)) {
            result.orders = searchQueryInfo.orders.map(order => ({
                fieldName: order.fieldName,
                isAsc: order.isAsc ? "true" : "false"
            }));
        }
        
        return result;
    }

    /**
     * 验证必需参数
     * @param {Object} params 参数对象
     */
    validateParams(params) {
        if (!params.currentOpenUserId) {
            throw new Error('currentOpenUserId是必需参数');
        }
        
        if (!params.dataObjectApiName) {
            throw new Error('dataObjectApiName是必需参数');
        }
        
        if (!Array.isArray(params.fieldProjection)) {
            throw new Error('fieldProjection必须是数组类型');
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
            console.log(`[FxiaokeCRMData] 频率限制，等待 ${waitTime}ms`);
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
                
                // 检查API错误
                if (response.data.errorCode !== 0) {
                    throw new Error(`API错误: ${response.data.errorCode} - ${response.data.errorMessage || response.data.errorDescription}`);
                }
                
                return response.data;
                
            } catch (error) {
                lastError = error;
                console.warn(`[FxiaokeCRMData] 第${attempt}次请求失败:`, error.message);
                
                // 如果是最后一次尝试，抛出错误
                if (attempt === this.retryConfig.maxRetries) {
                    break;
                }
                
                // 计算延迟时间（指数退避）
                const delay = this.retryConfig.retryDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt - 1);
                console.log(`[FxiaokeCRMData] ${delay}ms后重试...`);
                await this.sleep(delay);
            }
        }
        
        throw new Error(`请求失败，已重试${this.retryConfig.maxRetries}次: ${lastError.message}`);
    }

    /**
     * 查询客户数据
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {Array<string>} [params.fields] 返回字段列表
     * @param {number} [params.limit=10] 查询条数
     * @param {number} [params.offset=0] 查询偏移量
     * @param {Object} [params.filters] 过滤条件
     * @param {Array<Object>} [params.orders] 排序条件
     * @returns {Promise<Array>} 客户数据数组
     */
    async findCustomerData(params = {}) {
        return this.findSimpleData({
            ...params,
            dataObjectApiName: 'Customer',
            fieldProjection: params.fields || ['_id', 'name', 'mobile', 'email', 'last_modified_time']
        });
    }

    /**
     * 查询联系人数据
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {Array<string>} [params.fields] 返回字段列表
     * @param {number} [params.limit=10] 查询条数
     * @param {number} [params.offset=0] 查询偏移量
     * @param {Object} [params.filters] 过滤条件
     * @param {Array<Object>} [params.orders] 排序条件
     * @returns {Promise<Array>} 联系人数据数组
     */
    async findContactData(params = {}) {
        return this.findSimpleData({
            ...params,
            dataObjectApiName: 'Contact',
            fieldProjection: params.fields || ['_id', 'name', 'mobile', 'email', 'last_modified_time']
        });
    }

    /**
     * 查询销售机会数据
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {Array<string>} [params.fields] 返回字段列表
     * @param {number} [params.limit=10] 查询条数
     * @param {number} [params.offset=0] 查询偏移量
     * @param {Object} [params.filters] 过滤条件
     * @param {Array<Object>} [params.orders] 排序条件
     * @returns {Promise<Array>} 销售机会数据数组
     */
    async findOpportunityData(params = {}) {
        return this.findSimpleData({
            ...params,
            dataObjectApiName: 'Opportunity',
            fieldProjection: params.fields || ['_id', 'name', 'amount', 'stage', 'last_modified_time']
        });
    }

    /**
     * 根据时间范围查询数据
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {string} params.dataObjectApiName 对象ApiName
     * @param {Array<string>} params.fieldProjection 返回字段列表
     * @param {Date|string|number} params.startTime 开始时间
     * @param {Date|string|number} params.endTime 结束时间
     * @param {string} [params.timeField='last_modified_time'] 时间字段名
     * @param {number} [params.limit=10] 查询条数
     * @param {number} [params.offset=0] 查询偏移量
     * @returns {Promise<Array>} 查询结果数组
     */
    async findDataByTimeRange(params = {}) {
        const startTime = this.convertToTimestamp(params.startTime);
        const endTime = this.convertToTimestamp(params.endTime);
        
        return this.findSimpleData({
            currentOpenUserId: params.currentOpenUserId,
            dataObjectApiName: params.dataObjectApiName,
            fieldProjection: params.fieldProjection,
            searchQueryInfo: {
                limit: params.limit || 10,
                offset: params.offset || 0,
                filters: {
                    field_name: params.timeField || 'last_modified_time',
                    field_values: [startTime.toString(), endTime.toString()],
                    operator: 'BETWEEN'
                },
                orders: [
                    {
                        fieldName: params.timeField || 'last_modified_time',
                        isAsc: false
                    }
                ]
            }
        });
    }

    /**
     * 转换时间为时间戳
     * @param {Date|string|number} time 时间
     * @returns {number} 时间戳
     */
    convertToTimestamp(time) {
        if (typeof time === 'number') {
            return time;
        }
        
        if (typeof time === 'string') {
            return new Date(time).getTime();
        }
        
        if (time instanceof Date) {
            return time.getTime();
        }
        
        throw new Error('无效的时间格式');
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
     * 休眠函数
     * @param {number} ms 休眠时间（毫秒）
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 销毁实例
     */
    destroy() {
        // 清理资源
        this.rateLimitConfig.requestQueue = [];
    }
}

module.exports = FxiaokeCRMDataClient; 