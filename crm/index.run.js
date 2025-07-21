const FxiaokeAuthManager = require('./fxiaoke_auth');
const FxiaokeUserManager = require('./fxiaoke_user');
const FxiaokeCRMClient = require('./fxiaoke_crm');
const FxiaokeCRMDataClient = require('./fxiaoke_crm_data');

// 配置示例
const config = {
    appId: 'FSAID_131882c',
    appSecret: '1a6d145803f84712ae4a4dee26efe7d3',
    permanentCode: 'B80A369A935263232BAEBC5D42542899'
};

// 测试手机号
const testMobile = '18692224663';

// 指定要测试的对象中文名称（可以修改这个常量来测试不同对象）
const TARGET_OBJECT_NAME = '销售订单';

// 指定要查询的字段标签列表（可以修改这个常量来查询不同字段）
// 示例：['订单名称', '创建时间', '最后修改时间', '客户名称', '订单金额']
const TARGET_FIELD_LABELS = ['系统订单编号', '客户名称', '销售订单总额'];

// 查询分页参数（可以修改这些常量来调整查询范围）
const QUERY_LIMIT = 5;  // 查询条数
const QUERY_OFFSET = 0; // 查询偏移量

/**
 * 根据字段标签生成fieldProjection参数
 * @param {Array} fields 字段信息数组
 * @param {Array} targetLabels 目标字段标签数组
 * @returns {Array} fieldProjection参数数组
 */
function generateFieldProjection(fields, targetLabels) {
    const fieldProjection = [];
    
    // 始终包含_id字段
    fieldProjection.push('_id');
    
    // 根据标签匹配字段
    for (const label of targetLabels) {
        const field = fields.find(f => f.label === label);
        if (field) {
            fieldProjection.push(field.apiName);
            console.log(`✅ 找到字段: ${label} -> ${field.apiName}`);
        } else {
            console.warn(`⚠️ 未找到字段: ${label}`);
        }
    }
    
    return fieldProjection;
}

/**
 * 精简的CRM测试流程
 */
async function simpleCRMTest() {
    try {
        console.log('=== 纷享销客CRM精简测试 ===');
        
        // 第一步：创建管理器
        console.log('\n--- 步骤1: 创建管理器 ---');
        const authManager = new FxiaokeAuthManager(config);
        const userManager = new FxiaokeUserManager(authManager);
        const crmClient = new FxiaokeCRMClient(authManager);
        const crmDataClient = new FxiaokeCRMDataClient(authManager);
        
        // 第二步：获取用户ID
        console.log('\n--- 步骤2: 获取用户ID ---');
        const currentOpenUserId = await userManager.getCurrentOpenUserId(testMobile);
        console.log('✅ 获取到用户ID:', currentOpenUserId);
        
        // 第三步：获取所有对象的中文名称
        console.log('\n--- 步骤3: 获取所有对象的中文名称 ---');
        const crmDescriptions = await crmClient.getCRMObjectListDescriptions({
            currentOpenUserId: currentOpenUserId
        });
        
        const objectNames = crmDescriptions.map(obj => obj.displayName);
        console.log('所有对象中文名称:', objectNames.join(', '));
        
        // 第四步：获取指定对象的字段信息
        console.log('\n--- 步骤4: 获取指定对象的字段信息 ---');
        console.log(`目标对象: ${TARGET_OBJECT_NAME}`);
        
        const targetObject = crmDescriptions.find(obj => obj.displayName === TARGET_OBJECT_NAME);
        
        if (!targetObject) {
            console.log(`❌ 未找到名称为 "${TARGET_OBJECT_NAME}" 的对象`);
            console.log('可用的对象名称:', objectNames.join(', '));
            return;
        }
        
        console.log(`✅ 找到目标对象: ${targetObject.displayName} (${targetObject.apiName})`);
        
        const objectDescribe = await crmClient.getCRMObjectDescribe({
            currentOpenUserId: currentOpenUserId,
            apiName: targetObject.apiName,
            includeDetail: false
        });
        
        const fields = objectDescribe.fields;
        const fieldInfo = fields.map(field => ({
            label: field.label,
            description: field.description || '',
            apiName: field.apiName,
            type: field.type,
            isRequired: field.isRequired
        }));
        
        console.log('字段label列表:');
        console.log(fieldInfo.map(f => f.label).join(', '));
        
        // 第五步：根据字段标签生成fieldProjection参数
        console.log('\n--- 步骤5: 根据字段标签生成查询参数 ---');
        console.log(`目标字段标签: ${TARGET_FIELD_LABELS.join(', ')}`);
        
        const fieldProjection = generateFieldProjection(fields, TARGET_FIELD_LABELS);
        console.log('生成的fieldProjection参数:', fieldProjection);
        console.log('查询分页参数: limit =', QUERY_LIMIT, ', offset =', QUERY_OFFSET);
        
        // 显示可用的字段标签（前10个）
        const availableLabels = fields.map(f => f.label).slice(0, 10);
        console.log('可用的字段标签示例:', availableLabels.join(', '));
        
        // 第六步：获取指定对象的数据
        console.log('\n--- 步骤6: 获取指定对象的数据 ---');
        
        // 构建查询条件（使用生成的fieldProjection参数和分页常量）
        const queryParams = {
            currentOpenUserId: currentOpenUserId,
            dataObjectApiName: targetObject.apiName,
            fieldProjection: fieldProjection,
            searchQueryInfo: {
                limit: QUERY_LIMIT,
                offset: QUERY_OFFSET,
                orders: [
                    {
                        fieldName: 'last_modified_time',
                        isAsc: false
                    }
                ]
            }
        };
        
        const dataResult = await crmDataClient.findSimpleData(queryParams);
        
        console.log('查询结果 (JSON字符串):');
        console.log(JSON.stringify(dataResult, null, 2));
        
        // 清理资源
        authManager.destroy();
        userManager.destroy();
        console.log('\n✅ 测试完成');
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
        console.error('错误详情:', error);
    }
}

// 运行测试
if (require.main === module) {
    simpleCRMTest();
}

module.exports = {
    simpleCRMTest
};
