#!/usr/bin/env python3
"""
纷享销客CRM Python工具使用示例
"""

import asyncio
import json
from fxiaoke_auth import FxiaokeAuthManager
from fxiaoke_user import FxiaokeUserManager
from fxiaoke_crm import FxiaokeCRMClient
from fxiaoke_crm_data import FxiaokeCRMDataClient


# 配置信息
CONFIG = {
    'appId': 'FSAID_131882c',
    'appSecret': '1a6d145803f84712ae4a4dee26efe7d3',
    'permanentCode': 'B80A369A935263232BAEBC5D42542899'
}

# 测试手机号
TEST_MOBILE = '18692224663'


async def basic_example():
    """
    基本使用示例
    """
    print("=== 基本使用示例 ===")
    
    # 创建管理器
    auth_manager = FxiaokeAuthManager(CONFIG)
    user_manager = FxiaokeUserManager(auth_manager)
    
    try:
        # 获取用户信息
        print(f"\n1. 根据手机号 {TEST_MOBILE} 获取用户信息:")
        user_info = await user_manager.get_user_by_mobile(TEST_MOBILE)
        print(f"   用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
        
        # 获取用户ID
        print(f"\n2. 获取用户ID:")
        current_open_user_id = await user_manager.get_current_open_user_id(TEST_MOBILE)
        print(f"   用户ID: {current_open_user_id}")
        
        # 获取用户详情
        print(f"\n3. 获取用户详情:")
        user_detail = await user_manager.get_user_detail(TEST_MOBILE)
        print(f"   用户详情: {json.dumps(user_detail, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"   错误: {e}")
    finally:
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()


async def crm_example():
    """
    CRM对象查询示例
    """
    print("\n=== CRM对象查询示例 ===")
    
    # 创建管理器
    auth_manager = FxiaokeAuthManager(CONFIG)
    user_manager = FxiaokeUserManager(auth_manager)
    crm_client = FxiaokeCRMClient(auth_manager)
    
    try:
        # 获取用户ID
        current_open_user_id = await user_manager.get_current_open_user_id(TEST_MOBILE)
        
        # 获取CRM对象列表
        print(f"\n1. 获取CRM对象列表:")
        crm_objects = await crm_client.get_crm_object_list_descriptions({
            'currentOpenUserId': current_open_user_id
        })
        
        print(f"   找到 {len(crm_objects)} 个CRM对象:")
        for i, obj in enumerate(crm_objects[:5]):  # 只显示前5个
            print(f"   {i+1}. {obj['displayName']} ({obj['apiName']})")
        
        # 获取第一个对象的字段信息
        if crm_objects:
            first_object = crm_objects[0]
            print(f"\n2. 获取对象 '{first_object['displayName']}' 的字段信息:")
            
            object_describe = await crm_client.get_crm_object_describe({
                'currentOpenUserId': current_open_user_id,
                'apiName': first_object['apiName'],
                'includeDetail': False
            })
            
            fields = object_describe['fields']
            print(f"   字段数量: {len(fields)}")
            print(f"   前5个字段:")
            for i, field in enumerate(fields[:5]):
                print(f"   {i+1}. {field['label']} ({field['apiName']}) - {field['type']}")
        
    except Exception as e:
        print(f"   错误: {e}")
    finally:
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()


async def data_query_example():
    """
    CRM数据查询示例
    """
    print("\n=== CRM数据查询示例 ===")
    
    # 创建管理器
    auth_manager = FxiaokeAuthManager(CONFIG)
    user_manager = FxiaokeUserManager(auth_manager)
    crm_data_client = FxiaokeCRMDataClient(auth_manager)
    
    try:
        # 获取用户ID
        current_open_user_id = await user_manager.get_current_open_user_id(TEST_MOBILE)
        
        # 查询客户数据
        print(f"\n1. 查询客户数据:")
        customer_data = await crm_data_client.find_customer_data({
            'currentOpenUserId': current_open_user_id,
            'fieldProjection': ['_id', 'name', 'mobile', 'email', 'last_modified_time'],
            'searchQueryInfo': {
                'limit': 3,
                'offset': 0
            }
        })
        
        print(f"   客户数据数量: {len(customer_data)}")
        if customer_data:
            print(f"   第一个客户: {json.dumps(customer_data[0], indent=2, ensure_ascii=False)}")
        
        # 查询联系人数据
        print(f"\n2. 查询联系人数据:")
        contact_data = await crm_data_client.find_contact_data({
            'currentOpenUserId': current_open_user_id,
            'fieldProjection': ['_id', 'name', 'mobile', 'email', 'company_name'],
            'searchQueryInfo': {
                'limit': 3,
                'offset': 0
            }
        })
        
        print(f"   联系人数据数量: {len(contact_data)}")
        if contact_data:
            print(f"   第一个联系人: {json.dumps(contact_data[0], indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"   错误: {e}")
    finally:
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()


async def batch_example():
    """
    批量处理示例
    """
    print("\n=== 批量处理示例 ===")
    
    # 创建管理器
    auth_manager = FxiaokeAuthManager(CONFIG)
    user_manager = FxiaokeUserManager(auth_manager)
    
    try:
        # 批量查询用户
        test_mobiles = [TEST_MOBILE, '13800138000', '13900139000']
        print(f"\n批量查询手机号: {test_mobiles}")
        
        results = await user_manager.batch_get_users_by_mobile(test_mobiles)
        
        for result in results:
            if result['success']:
                print(f"   ✅ {result['mobile']}: 成功")
            else:
                print(f"   ❌ {result['mobile']}: 失败 - {result['error']}")
        
    except Exception as e:
        print(f"   错误: {e}")
    finally:
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()


async def main():
    """
    主函数
    """
    print("纷享销客CRM Python工具使用示例")
    print("=" * 50)
    
    # 运行各个示例
    await basic_example()
    await crm_example()
    await data_query_example()
    await batch_example()
    
    print("\n" + "=" * 50)
    print("示例运行完成！")


if __name__ == '__main__':
    asyncio.run(main()) 