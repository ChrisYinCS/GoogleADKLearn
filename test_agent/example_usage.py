import asyncio
import json
from test_agent.index_run import FxiaokeCRMService, generate_field_projection

# 配置信息
CONFIG = {
    'appId': 'FSAID_131882c',
    'appSecret': '1a6d145803f84712ae4a4dee26efe7d3',
    'permanentCode': 'B80A369A935263232BAEBC5D42542899'
}

# 测试手机号
TEST_MOBILE = '18692224663'

async def example_usage():
    """
    使用示例
    """
    # 创建CRM服务实例
    crm_service = FxiaokeCRMService()
    
    try:
        # 1. 获取用户ID
        user_id = await crm_service.get_user_id_by_mobile(TEST_MOBILE)
        print(f"用户ID: {user_id}")
        
        # 2. 获取所有CRM对象
        crm_objects = await crm_service.get_crm_objects(user_id)
        print(f"CRM对象数量: {len(crm_objects)}")
        
        # 3. 获取第一个对象的字段信息
        if crm_objects:
            first_object = crm_objects[0]
            print(f"第一个对象: {first_object['displayName']} ({first_object['apiName']})")
            
            fields = await crm_service.get_object_fields(user_id, first_object['apiName'])
            print(f"字段数量: {len(fields)}")
            
            # 4. 生成字段投影
            field_labels = [field['label'] for field in fields[:5]]  # 取前5个字段
            field_projection = generate_field_projection(fields, field_labels)
            print(f"字段投影: {field_projection}")
            
            # 5. 查询数据
            data = await crm_service.query_object_data(
                user_id, 
                first_object['apiName'], 
                field_projection, 
                limit=3
            )
            print(f"查询到 {len(data)} 条数据")
            
        # 6. 获取用户信息
        user_info = await crm_service.get_user_by_mobile(TEST_MOBILE)
        print(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
        
    finally:
        # 清理资源
        crm_service.destroy()

if __name__ == '__main__':
    asyncio.run(example_usage()) 