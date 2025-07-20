#!/usr/bin/env python3
"""
测试导入脚本
验证所有模块的导入是否正常
"""

def test_imports():
    """测试所有模块的导入"""
    try:
        print("测试导入纷享销客CRM模块...")
        
        # 测试导入各个模块
        from fxiaoke_auth import FxiaokeAuthManager
        print("✅ FxiaokeAuthManager 导入成功")
        
        from fxiaoke_user import FxiaokeUserManager
        print("✅ FxiaokeUserManager 导入成功")
        
        from fxiaoke_crm import FxiaokeCRMClient
        print("✅ FxiaokeCRMClient 导入成功")
        
        from fxiaoke_crm_data import FxiaokeCRMDataClient
        print("✅ FxiaokeCRMDataClient 导入成功")
        
        # 测试包导入
        import fxiaoke_auth
        import fxiaoke_user
        import fxiaoke_crm
        import fxiaoke_crm_data
        print("✅ 所有模块导入成功")
        
        # 测试类实例化（不调用API）
        print("\n测试类实例化...")
        
        config = {
            'appId': 'test_app_id',
            'appSecret': 'test_app_secret',
            'permanentCode': 'test_permanent_code'
        }
        
        auth_manager = FxiaokeAuthManager(config)
        print("✅ FxiaokeAuthManager 实例化成功")
        
        user_manager = FxiaokeUserManager(auth_manager)
        print("✅ FxiaokeUserManager 实例化成功")
        
        crm_client = FxiaokeCRMClient(auth_manager)
        print("✅ FxiaokeCRMClient 实例化成功")
        
        crm_data_client = FxiaokeCRMDataClient(auth_manager)
        print("✅ FxiaokeCRMDataClient 实例化成功")
        
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()
        
        print("\n🎉 所有测试通过！Python版本的纷享销客CRM工具已成功创建。")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False
    
    return True


if __name__ == '__main__':
    success = test_imports()
    if success:
        print("\n✅ 导入测试完成，所有模块工作正常！")
    else:
        print("\n❌ 导入测试失败，请检查代码！") 