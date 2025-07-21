const FxiaokeAuthManager = require('./fxiaoke_auth');

// 配置示例
const config = {
    appId: 'FSAID_131882c',
    appSecret: '1a6d145803f84712ae4a4dee26efe7d3',
    permanentCode: 'B80A369A935263232BAEBC5D42542899'
};

async function testFxiaokeAuth() {
    try {
        console.log('=== 纷享销客CRM授权测试 ===');
        
        // 创建授权管理器实例
        const authManager = new FxiaokeAuthManager(config);
        
        // 验证配置
        authManager.validateConfig();
        console.log('✅ 配置验证通过');
        
        // 获取token
        console.log('\n--- 首次获取token ---');
        const tokenInfo = await authManager.getCorpAccessToken();
        console.log('Token信息:', {
            corpId: tokenInfo.corpId,
            expiresIn: tokenInfo.expiresIn,
            isValid: authManager.isTokenValid()
        });
        
        // 再次获取token（应该使用缓存）
        console.log('\n--- 再次获取token（使用缓存） ---');
        const cachedTokenInfo = await authManager.getCorpAccessToken();
        console.log('缓存Token信息:', {
            corpId: cachedTokenInfo.corpId,
            expiresIn: cachedTokenInfo.expiresIn,
            isValid: authManager.isTokenValid()
        });
        
        // 获取当前token状态
        console.log('\n--- 当前token状态 ---');
        const currentToken = authManager.getCurrentToken();
        console.log('当前Token状态:', currentToken);
        
        // 强制刷新token
        console.log('\n--- 强制刷新token ---');
        const refreshedToken = await authManager.forceRefreshToken();
        console.log('刷新后Token信息:', {
            corpId: refreshedToken.corpId,
            expiresIn: refreshedToken.expiresIn,
            isValid: authManager.isTokenValid()
        });
        
        console.log('\n✅ 测试完成');
        
        // 清理资源
        authManager.destroy();
        
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
    
    // 验证配置
    try {
        authManager.validateConfig();
        console.log('✅ 配置验证通过');
    } catch (error) {
        console.error('❌ 配置验证失败:', error.message);
    }
    
    // 测试token有效性检查
    console.log('\n--- Token有效性测试 ---');
    console.log('Token是否有效:', authManager.isTokenValid());
    console.log('是否需要刷新:', authManager.shouldRefreshToken());
    
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
    
    try {
        // 2. 获取token（会自动处理缓存和刷新）
        const tokenInfo = await authManager.getCorpAccessToken();
        
        // 3. 使用token进行API调用
        const headers = {
            'Authorization': `Bearer ${tokenInfo.corpAccessToken}`,
            'Content-Type': 'application/json'
        };
        
        console.log('API调用headers:', headers);
        
        // 4. 在应用关闭时清理资源
        authManager.destroy();
        
    } catch (error) {
        console.error('获取token失败:', error.message);
    }
}

// 运行测试
if (require.main === module) {
    // 根据环境变量决定运行哪种测试
    const testMode = process.env.TEST_MODE || 'real';
    
    switch (testMode) {
        case 'real':
            testFxiaokeAuth();
            break;
        case 'mock':
            mockTest();
            break;
        case 'example':
            usageExample();
            break;
        default:
            console.log('请设置 TEST_MODE 环境变量: real, mock, 或 example');
    }
}

module.exports = {
    testFxiaokeAuth,
    mockTest,
    usageExample
}; 