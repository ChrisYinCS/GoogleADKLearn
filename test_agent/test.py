import asyncio
import logging
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_agent.index_run import FxiaokeCRMService, generate_field_projection

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_fxiaoke_crm_service():
    """
    测试纷享销客CRM服务的所有功能
    """
    # 测试手机号
    test_mobile = "18874155467"
    
    # 创建CRM服务实例
    crm_service = FxiaokeCRMService()
    
    try:
        logger.info("🚀 开始测试纷享销客CRM服务...")
        
        # 1. 测试初始化
        logger.info("\n📋 1. 测试服务初始化...")
        await crm_service.initialize()
        logger.info("✅ 服务初始化成功")
        
        # 2. 测试根据手机号获取用户ID
        logger.info("\n📋 2. 测试根据手机号获取用户ID...")
        user_id = await crm_service.get_user_id_by_mobile(test_mobile)
        logger.info(f"✅ 获取到用户ID: {user_id}")
        
        # # 3. 测试获取用户信息
        # logger.info("\n📋 3. 测试获取用户信息...")
        # user_info = await crm_service.get_user_by_mobile(test_mobile)
        # logger.info(f"✅ 获取到用户信息: {user_info}")
        
        # # 4. 测试获取用户详细信息
        # logger.info("\n📋 4. 测试获取用户详细信息...")
        # user_detail = await crm_service.get_user_detail(test_mobile)
        # logger.info(f"✅ 获取到用户详细信息: {user_detail}")
        
        # # 5. 测试批量获取用户信息
        # logger.info("\n📋 5. 测试批量获取用户信息...")
        # batch_users = await crm_service.batch_get_users_by_mobile([test_mobile])
        # logger.info(f"✅ 批量获取用户信息: {batch_users}")
        
        # 6. 测试获取CRM对象列表
        logger.info("\n📋 6. 测试获取CRM对象列表...")
        crm_objects = await crm_service.get_crm_objects(user_id)
        logger.info(f"✅ 获取到 {len(crm_objects)} 个CRM对象")
        
        # 打印前几个CRM对象
        for i, obj in enumerate(crm_objects[:5]):
            logger.info(f"   {i+1}. {obj.get('label', 'N/A')} ({obj.get('apiName', 'N/A')})")
        
        # 7. 测试获取对象字段信息（固定为 SalesOrderObj）
        logger.info("\n📋 7. 测试获取对象字段信息（SalesOrderObj）...")
        object_api_name = "SalesOrderObj"
        fields = await crm_service.get_object_fields(user_id, object_api_name)
        logger.info(f"✅ 获取到 {len(fields)} 个字段")
        for i, field in enumerate(fields[:5]):
            logger.info(f"   {i+1}. {field.get('label', 'N/A')} ({field.get('apiName', 'N/A')})")

        # 8. 测试查询对象数据（SalesOrderObj）
        logger.info("\n📋 8. 测试查询对象数据（SalesOrderObj）...")

        # 生成字段投影（包含前5个字段）
        target_labels = [field['label'] for field in fields[:5]]
        field_projection = generate_field_projection(fields, target_labels)
        logger.info(f"   字段投影: {field_projection}")

        # 查询数据
        data = await crm_service.query_object_data(
            user_id=user_id,
            object_api_name=object_api_name,
            field_projection=field_projection,
            limit=5,
            offset=0
        )
        logger.info(f"✅ 查询到 {len(data)} 条数据")
        for i, record in enumerate(data[:3]):
            logger.info(f"   记录 {i+1}: {record}")
        
        logger.info("\n🎉 所有测试完成！")
        
    except Exception as e:
        logger.error(f"❌ 测试过程中出现错误: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
    
    finally:
        # 清理资源
        crm_service.destroy()
        logger.info("🧹 资源清理完成")

async def test_field_projection():
    """
    测试字段投影生成功能
    """
    logger.info("\n📋 测试字段投影生成功能...")
    
    # 模拟字段数据
    fields = [
        {'label': '客户名称', 'apiName': 'name'},
        {'label': '联系电话', 'apiName': 'mobile'},
        {'label': '客户地址', 'apiName': 'address'},
        {'label': '创建时间', 'apiName': 'create_time'},
        {'label': '客户状态', 'apiName': 'status'}
    ]
    
    # 目标字段标签
    target_labels = ['客户名称', '联系电话', '客户地址']
    
    # 调用字段投影生成函数
    field_projection = generate_field_projection(fields, target_labels)
    
    logger.info(f"✅ 生成的字段投影: {field_projection}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_fxiaoke_crm_service())
    asyncio.run(test_field_projection())
