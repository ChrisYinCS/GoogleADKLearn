const FxiaokeAuthManager = require('./fxiaoke_auth');
const FxiaokeCRMClient = require('./fxiaoke_crm');

// 测试配置
const config = {
    appId: 'FSAID_131882c',
    appSecret: '1a6d145803f84712ae4a4dee26efe7d3',
    permanentCode: 'B80A369A935263232BAEBC5D42542899'
};

async function testCRMClient() {
    try {
        console.log('=== 纷享销客CRM客户端测试 ===');
        
        // 创建授权管理器
        const authManager = new FxiaokeAuthManager(config);
        
        // 创建CRM客户端
        const crmClient = new FxiaokeCRMClient(authManager);
        
        // 验证认证配置
        authManager.validateConfig();
        console.log('✅ 认证配置验证通过');
        
        // 测试获取认证信息
        console.log('\n--- 获取认证信息 ---');
        const authInfo = await crmClient.getAuthInfo();
        console.log('认证信息:', {
            corpId: authInfo.corpId,
            expiresIn: authInfo.expiresIn,
            isValid: crmClient.isAuthValid()
        });
        
        // 测试获取客户列表
        console.log('\n--- 获取客户列表 ---');
        const customerList = await crmClient.getCustomerList({
            currentOpenUserId: 'test_user_id', // 需要替换为真实的用户ID
            pageSize: 10,
            pageNumber: 1
        });
        console.log('客户列表结果:', customerList);
        
        // 测试获取联系人列表
        console.log('\n--- 获取联系人列表 ---');
        const contactList = await crmClient.getContactList({
            currentOpenUserId: 'test_user_id', // 需要替换为真实的用户ID
            pageSize: 10,
            pageNumber: 1
        });
        console.log('联系人列表结果:', contactList);
        
        // 测试获取销售机会列表
        console.log('\n--- 获取销售机会列表 ---');
        const opportunityList = await crmClient.getOpportunityList({
            currentOpenUserId: 'test_user_id', // 需要替换为真实的用户ID
            pageSize: 10,
            pageNumber: 1
        });
        console.log('销售机会列表结果:', opportunityList);
        
        console.log('\n✅ CRM客户端测试完成');
        
        // 清理资源
        authManager.destroy();
        
    } catch (error) {
        console.error('❌ CRM客户端测试失败:', error.message);
    }
}

// 模拟测试（不实际调用API）
async function mockTest() {
    console.log('=== 模拟测试模式 ===');
    
    // 模拟配置
    const mockConfig = {
        appId: 'mock_app_id',
        appSecret: 'mock_app_secret',
        permanentCode: 'mock_permanent_code'
    };
    
    const authManager = new FxiaokeAuthManager(mockConfig);
    const crmClient = new FxiaokeCRMClient(authManager);
    
    // 验证配置
    try {
        authManager.validateConfig();
        console.log('✅ 配置验证通过');
    } catch (error) {
        console.error('❌ 配置验证失败:', error.message);
    }
    
    // 测试认证状态检查
    console.log('\n--- 认证状态测试 ---');
    console.log('认证是否有效:', crmClient.isAuthValid());
    
    // 清理资源
    authManager.destroy();
}

// 使用示例
async function usageExample() {
    console.log('=== 使用示例 ===');
    
    // 1. 创建授权管理器
    const authManager = new FxiaokeAuthManager({
        appId: 'your_app_id',
        appSecret: 'your_app_secret',
        permanentCode: 'your_permanent_code'
    });
    
    // 2. 创建CRM客户端
    const crmClient = new FxiaokeCRMClient(authManager);
    
    try {
        // 3. 获取客户列表
        const customers = await crmClient.getCustomerList({
            currentOpenUserId: 'your_user_id',
            pageSize: 20,
            pageNumber: 1,
            filters: {
                // 可以添加过滤条件
                // status: 'active',
                // createTime: '2024-01-01'
            }
        });
        
        console.log('客户列表:', customers);
        
        // 4. 获取联系人列表
        const contacts = await crmClient.getContactList({
            currentOpenUserId: 'your_user_id',
            pageSize: 20,
            pageNumber: 1
        });
        
        console.log('联系人列表:', contacts);
        
        // 5. 获取销售机会列表
        const opportunities = await crmClient.getOpportunityList({
            currentOpenUserId: 'your_user_id',
            pageSize: 20,
            pageNumber: 1
        });
        
        console.log('销售机会列表:', opportunities);
        
    } catch (error) {
        console.error('API调用失败:', error.message);
    } finally {
        // 6. 清理资源
        authManager.destroy();
    }
}

// 高级使用示例
async function advancedUsageExample() {
    console.log('=== 高级使用示例 ===');
    
    const authManager = new FxiaokeAuthManager(config);
    const crmClient = new FxiaokeCRMClient(authManager);
    
    try {
        // 检查认证状态
        if (!crmClient.isAuthValid()) {
            console.log('认证已过期，正在刷新...');
        }
        
        // 获取认证信息
        const authInfo = await crmClient.getAuthInfo();
        console.log('当前认证信息:', {
            corpId: authInfo.corpId,
            expiresIn: authInfo.expiresIn
        });
        
        // 自定义对象列表查询
        const customQuery = await crmClient.getObjectList({
            currentOpenUserId: 'your_user_id',
            queryParams: {
                objectType: 'Customer',
                pageSize: 50,
                pageNumber: 1,
                // 可以添加更多查询参数
                // fields: ['name', 'phone', 'email'],
                // filters: { status: 'active' }
            }
        });
        
        console.log('自定义查询结果:', customQuery);
        
    } catch (error) {
        console.error('高级使用示例失败:', error.message);
    } finally {
        authManager.destroy();
    }
}

// 运行测试
if (require.main === module) {
    // 根据环境变量决定运行哪种测试
    const testMode = process.env.TEST_MODE || 'mock';
    
    switch (testMode) {
        case 'real':
            testCRMClient();
            break;
        case 'mock':
            mockTest();
            break;
        case 'example':
            usageExample();
            break;
        case 'advanced':
            advancedUsageExample();
            break;
        default:
            console.log('请设置 TEST_MODE 环境变量: real, mock, example, 或 advanced');
    }
}

module.exports = {
    testCRMClient,
    mockTest,
    usageExample,
    advancedUsageExample
}; 