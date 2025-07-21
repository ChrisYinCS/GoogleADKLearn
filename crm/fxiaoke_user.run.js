const FxiaokeAuthManager = require('./fxiaoke_auth');
const FxiaokeUserManager = require('./fxiaoke_user');

// 配置示例
const config = {
    appId: 'FSAID_131882c',
    appSecret: '1a6d145803f84712ae4a4dee26efe7d3',
    permanentCode: 'B80A369A935263232BAEBC5D42542899'
};

async function testFxiaokeUser() {
    try {
        console.log('=== 纷享销客用户接口测试 ===');
        
        // 创建授权管理器实例
        const authManager = new FxiaokeAuthManager(config);
        
        // 创建用户管理器实例
        const userManager = new FxiaokeUserManager(authManager);
        
        // 测试手机号
        const testMobile = '18211565695';
        
        console.log(`\n--- 根据手机号获取用户信息: ${testMobile} ---`);
        const userInfo = await userManager.getUserByMobile(testMobile);
        console.log('用户信息:', JSON.stringify(userInfo, null, 2));
        
        console.log('\n--- 获取currentOpenUserId ---');
        const currentOpenUserId = await userManager.getCurrentOpenUserId(testMobile);
        console.log('currentOpenUserId:', currentOpenUserId);
        
        console.log('\n--- 获取用户详细信息 ---');
        const userDetail = await userManager.getUserDetail(testMobile);
        console.log('用户详细信息:', {
            openUserId: userDetail.openUserId,
            fullName: userDetail.fullName,
            mobile: userDetail.mobile,
            email: userDetail.email,
            status: userDetail.status
        });
        
        // 清理资源
        authManager.destroy();
        userManager.destroy();
        
        console.log('\n✅ 测试完成');
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
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
    const userManager = new FxiaokeUserManager(authManager);
    
    // 测试手机号验证
    console.log('\n--- 手机号验证测试 ---');
    const testMobiles = ['18211565695', '13800138000', 'invalid_mobile', ''];
    
    for (const mobile of testMobiles) {
        try {
            userManager.validateMobile(mobile);
            console.log(`✅ ${mobile}: 格式正确`);
        } catch (error) {
            console.log(`❌ ${mobile}: ${error.message}`);
        }
    }
    
    // 测试配置设置
    console.log('\n--- 配置设置测试 ---');
    userManager.setRetryConfig({ maxRetries: 5 });
    userManager.setRateLimitConfig({ maxRequestsPerWindow: 50 });
    userManager.setTimeout(15000);
    console.log('✅ 配置设置完成');
    
    // 清理资源
    authManager.destroy();
    userManager.destroy();
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
    
    // 2. 创建用户管理器
    const userManager = new FxiaokeUserManager(authManager);
    
    try {
        // 3. 根据手机号获取用户信息
        const mobile = '18211565695';
        const userInfo = await userManager.getUserByMobile(mobile);
        console.log('用户信息:', userInfo);
        
        // 4. 获取currentOpenUserId
        const currentOpenUserId = await userManager.getCurrentOpenUserId(mobile);
        console.log('currentOpenUserId:', currentOpenUserId);
        
        // 5. 获取用户详细信息
        const userDetail = await userManager.getUserDetail(mobile);
        console.log('用户详细信息:', userDetail);
        
        // 6. 批量获取用户信息
        const mobiles = ['18211565695', '13800138000'];
        const batchResults = await userManager.batchGetUsersByMobile(mobiles);
        console.log('批量结果:', batchResults);
        
        // 6. 在应用关闭时清理资源
        authManager.destroy();
        userManager.destroy();
        
    } catch (error) {
        console.error('操作失败:', error.message);
    }
}

// 批量测试
async function batchTest() {
    console.log('=== 批量测试 ===');
    
    const authManager = new FxiaokeAuthManager(config);
    const userManager = new FxiaokeUserManager(authManager);
    
    const testMobiles = [
        '18211565695',
        '13800138000',
        '13900139000'
    ];
    
    try {
        console.log('开始批量获取用户信息...');
        const results = await userManager.batchGetUsersByMobile(testMobiles);
        
        console.log('\n批量结果:');
        results.forEach((result, index) => {
            console.log(`${index + 1}. ${result.mobile}: ${result.success ? '成功' : '失败'}`);
            if (!result.success) {
                console.log(`   错误: ${result.error}`);
            }
        });
        
    } catch (error) {
        console.error('批量测试失败:', error.message);
    } finally {
        authManager.destroy();
        userManager.destroy();
    }
}

// 运行测试
if (require.main === module) {
    // 根据环境变量决定运行哪种测试
    const testMode = process.env.TEST_MODE || 'mock';
    
    switch (testMode) {
        case 'real':
            testFxiaokeUser();
            break;
        case 'mock':
            mockTest();
            break;
        case 'example':
            usageExample();
            break;
        case 'batch':
            batchTest();
            break;
        default:
            console.log('请设置 TEST_MODE 环境变量: real, mock, example, 或 batch');
    }
}

module.exports = {
    testFxiaokeUser,
    mockTest,
    usageExample,
    batchTest
}; 