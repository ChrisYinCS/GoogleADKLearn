const axios = require('axios');

/**
 * 纷享销客CRM API调用类
 * 提供CRM相关接口的调用功能
 */
class FxiaokeCRMClient {
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
    }

    /**
     * 获取CRM对象列表
     * @param {Object} params 请求参数
     * @param {string} params.currentOpenUserId 当前用户ID（通过手机号查询员工接口返回）
     * @param {Object} [params.queryParams] 查询参数
     * @param {string} [params.objectType] 对象类型
     * @param {number} [params.pageSize] 每页数量
     * @param {number} [params.pageNumber] 页码
     * @returns {Promise<Object>} 返回对象列表数据
     */
    async getObjectList(params = {}) {
        try {
            // 获取认证信息
            const authInfo = await this.authManager.getCorpAccessToken();
            
            // 构建请求参数
            const requestData = {
                corpAccessToken: authInfo.corpAccessToken,
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId,
                ...params.queryParams
            };

            console.log('[FxiaokeCRM] 请求对象列表，参数:', {
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId,
                objectType: params.objectType || '未指定'
            });

            // 发送请求
            const response = await this.requestWithRetry('/cgi/crm/v2/object/list', requestData);
            
            console.log('[FxiaokeCRM] 对象列表获取成功');
            return response;
            
        } catch (error) {
            console.error('[FxiaokeCRM] 获取对象列表失败:', error.message);
            throw error;
        }
    }

    /**
     * 获取CRM对象列表（获取系统中所有可用的对象类型）
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @returns {Promise<Array>} CRM对象数组，每个对象包含以下字段：
     *   - describeApiName: string - 对象的API名称
     *   - describeDisplayName: string - 对象的中文显示名称
     *   - defineType: string - 对象定义类型
     *   - isActive: boolean - 对象是否激活
     *   - iconPath: string - 图标路径
     *   - iconIndex: number - 图标索引
     *   - hideButton: boolean - 是否隐藏按钮
     *   - publicObject: boolean - 是否为公共对象
     */
    async getCRMObjectList(params = {}) {
        try {
            // 获取认证信息
            const authInfo = await this.authManager.getCorpAccessToken();
            
            // 构建请求参数
            const requestData = {
                corpAccessToken: authInfo.corpAccessToken,
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId
            };

            console.log('[FxiaokeCRM] 请求CRM对象列表，参数:', {
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId
            });

            // 发送请求
            const response = await this.requestWithRetry('/cgi/crm/v2/object/list', requestData);
            
            // 提取并返回objects数组
            if (response.data && response.data.objects && Array.isArray(response.data.objects)) {
                console.log('[FxiaokeCRM] CRM对象列表获取成功，对象数量:', response.data.objects.length);
                return response.data.objects;
            }
            
            console.log('[FxiaokeCRM] CRM对象列表获取成功，但未找到对象数据');
            return [];
            
        } catch (error) {
            console.error('[FxiaokeCRM] 获取CRM对象列表失败:', error.message);
            throw error;
        }
    }

    /**
     * 获取CRM对象列表的中文描述（用于LLM分析）
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @returns {Promise<Array>} 中文描述列表，每个对象包含以下字段：
     *   - apiName: string - 对象的API名称
     *   - displayName: string - 对象的中文显示名称
     *   - defineType: string - 对象定义类型
     *   - isActive: boolean - 对象是否激活
     *   - publicObject: boolean - 是否为公共对象
     */
    async getCRMObjectListDescriptions(params = {}) {
        try {
            const objects = await this.getCRMObjectList(params);
            
            if (Array.isArray(objects)) {
                // 提取所有对象的中文描述
                const descriptions = objects
                    .filter(obj => obj.isActive && obj.describeDisplayName) // 只返回激活的对象
                    .map(obj => ({
                        apiName: obj.describeApiName,
                        displayName: obj.describeDisplayName,
                        defineType: obj.defineType,
                        isActive: obj.isActive,
                        publicObject: obj.publicObject
                    }));
                
                console.log(`[FxiaokeCRM] 获取到 ${descriptions.length} 个CRM对象描述`);
                return descriptions;
            }
            
            return [];
            
        } catch (error) {
            console.error('[FxiaokeCRM] 获取CRM对象描述失败:', error.message);
            throw error;
        }
    }

    /**
     * 获取CRM对象的纯中文描述列表（用于LLM指令关联分析）
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @returns {Promise<Array<string>>} 中文描述字符串数组
     */
    async getCRMObjectDisplayNames(params = {}) {
        try {
            const descriptions = await this.getCRMObjectListDescriptions(params);
            
            // 只返回中文描述名称
            const displayNames = descriptions.map(desc => desc.displayName);
            
            console.log(`[FxiaokeCRM] 获取到 ${displayNames.length} 个CRM对象中文描述`);
            return displayNames;
            
        } catch (error) {
            console.error('[FxiaokeCRM] 获取CRM对象中文描述失败:', error.message);
            throw error;
        }
    }

    /**
     * 获取单个CRM对象的详细描述信息
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {string} params.apiName 对象的apiName
     * @param {boolean} [params.includeDetail=true] 是否包括从对象
     * @param {boolean} [params.filterInactive=true] 是否过滤非激活字段（默认true）
     * @param {boolean} [params.filterSystem=true] 是否过滤系统字段（默认true）
     * @param {boolean} [params.filterEmpty=true] 是否过滤空标签字段（默认true）
     * @returns {Promise<Object>} 对象详细描述信息，包含以下字段：
     *   - data: Object - 原始API返回数据
     *   - fields: Array - 提取的字段信息数组，每个字段包含：
     *     - apiName: string - 字段API名称
     *     - label: string - 字段显示名称
     *     - type: string - 字段数据类型
     *     - description: string - 字段描述
     *     - isRequired: boolean - 是否必填
     *     - helpText: string - 帮助文本
     *     - isActive: boolean - 是否激活
     *     - defineType: string - 定义类型
     *     - defaultValue: string - 默认值
     *     - options: Array - 选项（仅选择字段）
     *     - targetApiName: string - 目标对象（仅引用字段）
     *     - fileSizeLimit: number - 文件大小限制（仅文件字段）
     *     - fileAmountLimit: number - 文件数量限制（仅文件字段）
     */
    async getCRMObjectDescribe(params = {}) {
        try {
            // 验证必需参数
            if (!params.apiName) {
                throw new Error('apiName参数是必需的');
            }

            // 获取认证信息
            const authInfo = await this.authManager.getCorpAccessToken();
            
            // 构建请求参数
            const requestData = {
                corpAccessToken: authInfo.corpAccessToken,
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId,
                data: {
                    includeDetail: params.includeDetail !== false, // 默认true
                    apiName: params.apiName
                }
            };

            console.log('[FxiaokeCRM] 请求对象描述信息，参数:', {
                corpId: authInfo.corpId,
                currentOpenUserId: params.currentOpenUserId,
                apiName: params.apiName,
                includeDetail: requestData.data.includeDetail
            });

            // 发送请求
            const response = await this.requestWithRetry('/cgi/crm/v2/object/describe', requestData);
            
            // 提取字段信息
            let fields = this.extractFieldInfo(response);
            
            // 应用过滤规则
            const originalCount = fields.length;
            fields = this.filterFields(fields, params);
            const filteredCount = fields.length;
            
            console.log('[FxiaokeCRM] 对象描述信息获取成功');
            console.log(`[FxiaokeCRM] 提取到 ${originalCount} 个字段，过滤后剩余 ${filteredCount} 个字段`);
            
            // 返回包含字段信息的完整结果
            return {
                data: response.data,
                fields: fields,
                errorCode: response.errorCode,
                errorMessage: response.errorMessage,
                errorDescription: response.errorDescription,
                traceId: response.traceId
            };
            
        } catch (error) {
            console.error('[FxiaokeCRM] 获取对象描述信息失败:', error.message);
            throw error;
        }
    }

    /**
     * 批量获取多个CRM对象的详细描述信息
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {Array<string>} params.apiNames 对象的apiName数组
     * @param {boolean} [params.includeDetail=true] 是否包括从对象
     * @returns {Promise<Array>} 对象详细描述信息数组
     */
    async batchGetCRMObjectDescribe(params = {}) {
        try {
            if (!params.apiNames || !Array.isArray(params.apiNames)) {
                throw new Error('apiNames参数必须是数组');
            }

            const results = [];
            
            for (const apiName of params.apiNames) {
                try {
                    const describeInfo = await this.getCRMObjectDescribe({
                        currentOpenUserId: params.currentOpenUserId,
                        apiName: apiName,
                        includeDetail: params.includeDetail
                    });
                    
                    results.push({
                        apiName: apiName,
                        success: true,
                        data: describeInfo
                    });
                } catch (error) {
                    results.push({
                        apiName: apiName,
                        success: false,
                        error: error.message
                    });
                }
            }
            
            console.log(`[FxiaokeCRM] 批量获取对象描述完成，成功: ${results.filter(r => r.success).length}/${results.length}`);
            return results;
            
        } catch (error) {
            console.error('[FxiaokeCRM] 批量获取对象描述失败:', error.message);
            throw error;
        }
    }

    /**
     * 提取CRM对象的字段信息
     * @param {Object} describeInfo 对象描述信息
     * @returns {Array} 字段信息数组，每个字段包含：
     *   - apiName: string - 字段API名称
     *   - label: string - 字段显示名称
     *   - type: string - 字段数据类型
     *   - description: string - 字段描述
     *   - isRequired: boolean - 是否必填
     *   - helpText: string - 帮助文本
     *   - options: Array - 选项（仅选择字段）
     *   - targetApiName: string - 目标对象（仅引用字段）
     */
    extractFieldInfo(describeInfo) {
        try {
            if (!describeInfo.data || !describeInfo.data.describe || !describeInfo.data.describe.fields) {
                return [];
            }

            const fields = describeInfo.data.describe.fields;
            const fieldList = [];

            for (const [fieldApiName, fieldInfo] of Object.entries(fields)) {
                const field = {
                    apiName: fieldApiName,
                    label: fieldInfo.label || '',
                    type: fieldInfo.type || '',
                    description: fieldInfo.description || '',
                    isRequired: fieldInfo.is_required || false,
                    helpText: fieldInfo.help_text || '',
                    isActive: fieldInfo.is_active !== false,
                    defineType: fieldInfo.define_type || '',
                    defaultValue: fieldInfo.default_value || ''
                };

                // 处理选择字段的选项
                if (fieldInfo.type === 'select_one' && fieldInfo.options) {
                    field.options = fieldInfo.options.map(option => ({
                        label: option.label,
                        value: option.value,
                        feKey: option.fe_key
                    }));
                }

                // 处理对象引用字段
                if (fieldInfo.type === 'object_reference' && fieldInfo.target_api_name) {
                    field.targetApiName = fieldInfo.target_api_name;
                    field.targetRelatedListName = fieldInfo.target_related_list_name;
                    field.targetRelatedListLabel = fieldInfo.target_related_list_label;
                }

                // 处理文件附件字段
                if (fieldInfo.type === 'file_attachment') {
                    field.fileSizeLimit = fieldInfo.file_size_limit;
                    field.fileAmountLimit = fieldInfo.file_amount_limit;
                    field.supportFileTypes = fieldInfo.support_file_types || [];
                    field.supportFileSuffix = fieldInfo.support_file_suffix || [];
                }

                fieldList.push(field);
            }

            return fieldList;
        } catch (error) {
            console.error('[FxiaokeCRM] 提取字段信息失败:', error.message);
            return [];
        }
    }

    /**
     * 过滤字段信息
     * @param {Array} fields 字段数组
     * @param {Object} params 过滤参数
     * @param {boolean} [params.filterInactive=true] 是否过滤非激活字段
     * @param {boolean} [params.filterSystem=true] 是否过滤系统字段
     * @param {boolean} [params.filterEmpty=true] 是否过滤空标签字段
     * @returns {Array} 过滤后的字段数组
     */
    filterFields(fields, params = {}) {
        const {
            filterInactive = true,
            filterSystem = true,
            filterEmpty = true
        } = params;

        return fields.filter(field => {
            // 过滤非激活字段
            if (filterInactive && !field.isActive) {
                return false;
            }

            // 过滤系统字段（通常以特定前缀开头）
            if (filterSystem && this.isSystemField(field.apiName)) {
                return false;
            }

            // 过滤空标签字段
            if (filterEmpty && (!field.label || field.label.trim() === '')) {
                return false;
            }

            return true;
        });
    }

    /**
     * 判断是否为系统字段
     * @param {string} apiName 字段API名称
     * @returns {boolean} 是否为系统字段
     */
    isSystemField(apiName) {
        // 系统字段通常以特定前缀开头
        const systemPrefixes = [
            'id', 'create_time', 'update_time', 'create_user', 'update_user',
            'is_deleted', 'deleted_time', 'owner_id', 'owner_name',
            'field_', 'system_', 'sys_', '_id', '_time', '_user'
        ];

        const lowerApiName = apiName.toLowerCase();
        return systemPrefixes.some(prefix => lowerApiName.startsWith(prefix));
    }

    /**
     * 获取客户列表
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {number} [params.pageSize=20] 每页数量
     * @param {number} [params.pageNumber=1] 页码
     * @param {Object} [params.filters] 过滤条件
     * @returns {Promise<Object>} 客户列表数据
     */
    async getCustomerList(params = {}) {
        const queryParams = {
            objectType: 'Customer',
            pageSize: params.pageSize || 20,
            pageNumber: params.pageNumber || 1,
            ...params.filters
        };

        return await this.getObjectList({
            currentOpenUserId: params.currentOpenUserId,
            queryParams
        });
    }

    /**
     * 获取联系人列表
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {number} [params.pageSize=20] 每页数量
     * @param {number} [params.pageNumber=1] 页码
     * @param {Object} [params.filters] 过滤条件
     * @returns {Promise<Object>} 联系人列表数据
     */
    async getContactList(params = {}) {
        const queryParams = {
            objectType: 'Contact',
            pageSize: params.pageSize || 20,
            pageNumber: params.pageNumber || 1,
            ...params.filters
        };

        return await this.getObjectList({
            currentOpenUserId: params.currentOpenUserId,
            queryParams
        });
    }

    /**
     * 获取销售机会列表
     * @param {Object} params 查询参数
     * @param {string} params.currentOpenUserId 当前用户ID
     * @param {number} [params.pageSize=20] 每页数量
     * @param {number} [params.pageNumber=1] 页码
     * @param {Object} [params.filters] 过滤条件
     * @returns {Promise<Object>} 销售机会列表数据
     */
    async getOpportunityList(params = {}) {
        const queryParams = {
            objectType: 'Opportunity',
            pageSize: params.pageSize || 20,
            pageNumber: params.pageNumber || 1,
            ...params.filters
        };

        return await this.getObjectList({
            currentOpenUserId: params.currentOpenUserId,
            queryParams
        });
    }

    /**
     * 带重试机制的API请求
     * @param {string} endpoint API端点
     * @param {Object} data 请求数据
     * @returns {Promise<Object>} API响应
     */
    async requestWithRetry(endpoint, data) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryConfig.maxRetries; attempt++) {
            try {
                const response = await axios.post(endpoint, data, this.requestConfig);
                
                // 检查错误码
                if (response.data.errorCode !== 0) {
                    throw new Error(`API错误: ${response.data.errorCode} - ${response.data.errorMessage}`);
                }
                
                return response.data;
                
            } catch (error) {
                lastError = error;
                console.warn(`[FxiaokeCRM] 第${attempt}次请求失败:`, error.message);
                
                // 如果是最后一次尝试，抛出错误
                if (attempt === this.retryConfig.maxRetries) {
                    break;
                }
                
                // 计算延迟时间（指数退避）
                const delay = this.retryConfig.retryDelay * Math.pow(this.retryConfig.backoffMultiplier, attempt - 1);
                console.log(`[FxiaokeCRM] ${delay}ms后重试...`);
                await this.sleep(delay);
            }
        }
        
        throw new Error(`API请求失败，已重试${this.retryConfig.maxRetries}次: ${lastError.message}`);
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
     * 获取当前认证信息
     * @returns {Promise<Object>} 认证信息
     */
    async getAuthInfo() {
        return await this.authManager.getCorpAccessToken();
    }

    /**
     * 检查认证状态
     * @returns {boolean}
     */
    isAuthValid() {
        return this.authManager.isTokenValid();
    }
}

module.exports = FxiaokeCRMClient; 