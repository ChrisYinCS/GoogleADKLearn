const FxiaokeAuthManager = require('./fxiaoke_auth');
const FxiaokeUserManager = require('./fxiaoke_user');
const FxiaokeCRMDataClient = require('./fxiaoke_crm_data');

/**
 * 纷享销客CRM数据查询测试和示例
 */
async function main() {
    try {
        // 1. 初始化认证管理器
        const authManager = new FxiaokeAuthManager({
            appId: 'your_app_id',
            appSecret: 'your_app_secret',
            permanentCode: 'your_permanent_code'
        });

        // 2. 初始化用户管理器
        const userManager = new FxiaokeUserManager(authManager);

        // 3. 初始化CRM数据查询客户端
        const crmDataClient = new FxiaokeCRMDataClient(authManager);

        // 4. 获取用户ID（通过手机号）
        const mobile = '13800138000'; // 替换为实际的手机号
        const currentOpenUserId = await userManager.getCurrentOpenUserId(mobile);
        console.log('获取到用户ID:', currentOpenUserId);

        // 5. 测试基本数据查询
        console.log('\n=== 测试基本数据查询 ===');
        const basicResult = await crmDataClient.findSimpleData({
            currentOpenUserId: currentOpenUserId,
            dataObjectApiName: 'Customer', // 客户对象
            fieldProjection: ['_id', 'name', 'mobile', 'email', 'last_modified_time'],
            searchQueryInfo: {
                limit: 10,
                offset: 0,
                orders: [
                    {
                        fieldName: 'last_modified_time',
                        isAsc: false
                    }
                ]
            }
        });
        console.log('基本查询结果:', JSON.stringify(basicResult, null, 2));

        // 6. 测试客户数据查询
        console.log('\n=== 测试客户数据查询 ===');
        const customerResult = await crmDataClient.findCustomerData({
            currentOpenUserId: currentOpenUserId,
            fields: ['_id', 'name', 'mobile', 'email', 'last_modified_time'],
            limit: 5,
            offset: 0,
            orders: [
                {
                    fieldName: 'last_modified_time',
                    isAsc: false
                }
            ]
        });
        console.log('客户数据查询结果:', JSON.stringify(customerResult, null, 2));

        // 7. 测试联系人数据查询
        console.log('\n=== 测试联系人数据查询 ===');
        const contactResult = await crmDataClient.findContactData({
            currentOpenUserId: currentOpenUserId,
            fields: ['_id', 'name', 'mobile', 'email', 'last_modified_time'],
            limit: 5,
            offset: 0
        });
        console.log('联系人数据查询结果:', JSON.stringify(contactResult, null, 2));

        // 8. 测试销售机会数据查询
        console.log('\n=== 测试销售机会数据查询 ===');
        const opportunityResult = await crmDataClient.findOpportunityData({
            currentOpenUserId: currentOpenUserId,
            fields: ['_id', 'name', 'amount', 'stage', 'last_modified_time'],
            limit: 5,
            offset: 0
        });
        console.log('销售机会数据查询结果:', JSON.stringify(opportunityResult, null, 2));

        // 9. 测试时间范围查询
        console.log('\n=== 测试时间范围查询 ===');
        const timeRangeResult = await crmDataClient.findDataByTimeRange({
            currentOpenUserId: currentOpenUserId,
            dataObjectApiName: 'Customer',
            fieldProjection: ['_id', 'name', 'mobile', 'last_modified_time'],
            startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7天前
            endTime: new Date(), // 现在
            timeField: 'last_modified_time',
            limit: 10,
            offset: 0
        });
        console.log('时间范围查询结果:', JSON.stringify(timeRangeResult, null, 2));

        // 10. 测试带过滤条件的查询
        console.log('\n=== 测试带过滤条件的查询 ===');
        const filterResult = await crmDataClient.findSimpleData({
            currentOpenUserId: currentOpenUserId,
            dataObjectApiName: 'Customer',
            fieldProjection: ['_id', 'name', 'mobile', 'email'],
            searchQueryInfo: {
                limit: 5,
                offset: 0,
                filters: {
                    field_name: 'name',
                    field_values: ['测试客户'],
                    operator: 'LIKE'
                }
            }
        });
        console.log('过滤条件查询结果:', JSON.stringify(filterResult, null, 2));

        console.log('\n=== 所有测试完成 ===');

    } catch (error) {
        console.error('测试失败:', error.message);
        console.error('错误详情:', error);
    }
}

/**
 * 演示如何使用CRM数据查询功能
 */
async function demonstrateUsage() {
    console.log('=== 纷享销客CRM数据查询功能演示 ===\n');

    // 配置信息（需要替换为实际的值）
    const config = {
        appId: 'your_app_id',
        appSecret: 'your_app_secret',
        permanentCode: 'your_permanent_code',
        mobile: '13800138000' // 用户手机号
    };

    try {
        // 初始化各个管理器
        const authManager = new FxiaokeAuthManager(config);
        const userManager = new FxiaokeUserManager(authManager);
        const crmDataClient = new FxiaokeCRMDataClient(authManager);

        // 获取用户ID
        const currentOpenUserId = await userManager.getCurrentOpenUserId(config.mobile);
        console.log('✅ 成功获取用户ID:', currentOpenUserId);

        // 示例1：查询最近修改的客户
        console.log('\n📋 示例1：查询最近修改的客户');
        const recentCustomers = await crmDataClient.findCustomerData({
            currentOpenUserId: currentOpenUserId,
            fields: ['_id', 'name', 'mobile', 'email', 'last_modified_time'],
            limit: 10,
            orders: [{ fieldName: 'last_modified_time', isAsc: false }]
        });
        console.log('查询结果:', recentCustomers);

        // 示例2：查询特定时间范围内的数据
        console.log('\n📋 示例2：查询最近7天的客户数据');
        const weeklyCustomers = await crmDataClient.findDataByTimeRange({
            currentOpenUserId: currentOpenUserId,
            dataObjectApiName: 'Customer',
            fieldProjection: ['_id', 'name', 'mobile', 'last_modified_time'],
            startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
            endTime: new Date(),
            limit: 20
        });
        console.log('查询结果:', weeklyCustomers);

        // 示例3：查询联系人数据
        console.log('\n📋 示例3：查询联系人数据');
        const contacts = await crmDataClient.findContactData({
            currentOpenUserId: currentOpenUserId,
            fields: ['_id', 'name', 'mobile', 'email', 'company_name'],
            limit: 5
        });
        console.log('查询结果:', contacts);

        // 示例4：查询销售机会
        console.log('\n📋 示例4：查询销售机会数据');
        const opportunities = await crmDataClient.findOpportunityData({
            currentOpenUserId: currentOpenUserId,
            fields: ['_id', 'name', 'amount', 'stage', 'expected_close_date'],
            limit: 5,
            orders: [{ fieldName: 'amount', isAsc: false }]
        });
        console.log('查询结果:', opportunities);

        console.log('\n✅ 所有示例执行完成');

    } catch (error) {
        console.error('❌ 演示失败:', error.message);
    }
}

/**
 * 错误处理示例
 */
async function errorHandlingExample() {
    console.log('=== 错误处理示例 ===\n');

    try {
        const authManager = new FxiaokeAuthManager({
            appId: 'invalid_app_id',
            appSecret: 'invalid_app_secret',
            permanentCode: 'invalid_permanent_code'
        });

        const crmDataClient = new FxiaokeCRMDataClient(authManager);

        // 这个请求会失败，演示错误处理
        await crmDataClient.findSimpleData({
            currentOpenUserId: 'invalid_user_id',
            dataObjectApiName: 'Customer',
            fieldProjection: ['_id', 'name']
        });

    } catch (error) {
        console.log('捕获到预期的错误:', error.message);
        console.log('错误类型:', error.constructor.name);
        
        // 根据错误类型进行不同的处理
        if (error.message.includes('API错误')) {
            console.log('这是API级别的错误');
        } else if (error.message.includes('参数')) {
            console.log('这是参数验证错误');
        } else {
            console.log('这是其他类型的错误');
        }
    }
}

// 如果直接运行此文件，执行主函数
if (require.main === module) {
    // 根据命令行参数选择不同的演示
    const args = process.argv.slice(2);
    
    if (args.includes('--demo')) {
        demonstrateUsage();
    } else if (args.includes('--error')) {
        errorHandlingExample();
    } else {
        main();
    }
}

module.exports = {
    main,
    demonstrateUsage,
    errorHandlingExample
}; 