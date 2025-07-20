import asyncio
import json
import logging
from typing import List, Dict, Any
from fxiaoke_auth import FxiaokeAuthManager
from fxiaoke_user import FxiaokeUserManager
from fxiaoke_crm import FxiaokeCRMClient
from fxiaoke_crm_data import FxiaokeCRMDataClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置示例
CONFIG = {
    'appId': 'FSAID_131882c',
    'appSecret': '1a6d145803f84712ae4a4dee26efe7d3',
    'permanentCode': 'B80A369A935263232BAEBC5D42542899'
}

# 测试手机号
TEST_MOBILE = '18692224663'

# 指定要测试的对象中文名称（可以修改这个常量来测试不同对象）
TARGET_OBJECT_NAME = '报表'

# 指定要查询的字段标签列表（可以修改这个常量来查询不同字段）
# 示例：['订单名称', '创建时间', '最后修改时间', '客户名称', '订单金额']
TARGET_FIELD_LABELS = ['系统订单编号', '客户名称', '销售订单总额']

# 查询分页参数（可以修改这些常量来调整查询范围）
QUERY_LIMIT = 5  # 查询条数
QUERY_OFFSET = 0  # 查询偏移量


def generate_field_projection(fields: List[Dict[str, Any]], target_labels: List[str]) -> List[str]:
    """
    根据字段标签生成fieldProjection参数
    
    Args:
        fields: 字段信息数组
        target_labels: 目标字段标签数组
        
    Returns:
        fieldProjection参数数组
    """
    field_projection = []
    
    # 始终包含_id字段
    field_projection.append('_id')
    
    # 根据标签匹配字段
    for label in target_labels:
        field = next((f for f in fields if f['label'] == label), None)
        if field:
            field_projection.append(field['apiName'])
            logger.info(f'✅ 找到字段: {label} -> {field["apiName"]}')
        else:
            logger.warning(f'⚠️ 未找到字段: {label}')
    
    return field_projection


async def simple_crm_test():
    """
    精简的CRM测试流程
    """
    try:
        logger.info('=== 纷享销客CRM精简测试 ===')
        
        # 第一步：创建管理器
        logger.info('\n--- 步骤1: 创建管理器 ---')
        auth_manager = FxiaokeAuthManager(CONFIG)
        user_manager = FxiaokeUserManager(auth_manager)
        crm_client = FxiaokeCRMClient(auth_manager)
        crm_data_client = FxiaokeCRMDataClient(auth_manager)
        
        # 第二步：获取用户ID
        logger.info('\n--- 步骤2: 获取用户ID ---')
        current_open_user_id = await user_manager.get_current_open_user_id(TEST_MOBILE)
        logger.info(f'✅ 获取到用户ID: {current_open_user_id}')
        
        # 第三步：获取所有对象的中文名称
        logger.info('\n--- 步骤3: 获取所有对象的中文名称 ---')
        crm_descriptions = await crm_client.get_crm_object_list_descriptions({
            'currentOpenUserId': current_open_user_id
        })
        
        object_names = [obj['displayName'] for obj in crm_descriptions]
        logger.info(f'所有对象中文名称: {", ".join(object_names)}')
        
        # 第四步：获取指定对象的字段信息
        logger.info('\n--- 步骤4: 获取指定对象的字段信息 ---')
        logger.info(f'目标对象: {TARGET_OBJECT_NAME}')
        
        target_object = next((obj for obj in crm_descriptions if obj['displayName'] == TARGET_OBJECT_NAME), None)
        
        if not target_object:
            logger.error(f'❌ 未找到名称为 "{TARGET_OBJECT_NAME}" 的对象')
            logger.info(f'可用的对象名称: {", ".join(object_names)}')
            return
        
        logger.info(f'✅ 找到目标对象: {target_object["displayName"]} ({target_object["apiName"]})')
        
        object_describe = await crm_client.get_crm_object_describe({
            'currentOpenUserId': current_open_user_id,
            'apiName': target_object['apiName'],
            'includeDetail': False
        })
        
        fields = object_describe['fields']
        field_info = [
            {
                'label': field['label'],
                'description': field.get('description', ''),
                'apiName': field['apiName'],
                'type': field['type'],
                'isRequired': field['isRequired']
            }
            for field in fields
        ]
        
        logger.info('字段label列表:')
        logger.info(', '.join(f['label'] for f in field_info))
        
        # 第五步：根据字段标签生成fieldProjection参数
        logger.info('\n--- 步骤5: 根据字段标签生成查询参数 ---')
        logger.info(f'目标字段标签: {", ".join(TARGET_FIELD_LABELS)}')
        
        field_projection = generate_field_projection(fields, TARGET_FIELD_LABELS)
        logger.info(f'生成的fieldProjection参数: {field_projection}')
        logger.info(f'查询分页参数: limit = {QUERY_LIMIT}, offset = {QUERY_OFFSET}')
        
        # 显示可用的字段标签（前10个）
        available_labels = [f['label'] for f in field_info][:10]
        logger.info(f'可用的字段标签示例: {", ".join(available_labels)}')
        
        # 第六步：获取指定对象的数据
        logger.info('\n--- 步骤6: 获取指定对象的数据 ---')
        
        # 构建查询条件（使用生成的fieldProjection参数和分页常量）
        query_params = {
            'currentOpenUserId': current_open_user_id,
            'dataObjectApiName': target_object['apiName'],
            'fieldProjection': field_projection,
            'searchQueryInfo': {
                'limit': QUERY_LIMIT,
                'offset': QUERY_OFFSET,
                'orders': [
                    {
                        'fieldName': 'last_modified_time',
                        'isAsc': False
                    }
                ]
            }
        }
        
        data_result = await crm_data_client.find_simple_data(query_params)
        
        logger.info('查询结果 (JSON字符串):')
        logger.info(json.dumps(data_result, indent=2, ensure_ascii=False))
        
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()
        logger.info('\n✅ 测试完成')
        
    except Exception as error:
        logger.error(f'❌ 测试失败: {str(error)}')
        logger.error(f'错误详情: {error}')


async def user_test():
    """
    用户管理测试
    """
    try:
        logger.info('=== 用户管理测试 ===')
        
        # 创建管理器
        auth_manager = FxiaokeAuthManager(CONFIG)
        user_manager = FxiaokeUserManager(auth_manager)
        
        # 测试单个用户查询
        logger.info('\n--- 测试单个用户查询 ---')
        user_info = await user_manager.get_user_by_mobile(TEST_MOBILE)
        logger.info(f'用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}')
        
        # 测试获取用户ID
        logger.info('\n--- 测试获取用户ID ---')
        current_open_user_id = await user_manager.get_current_open_user_id(TEST_MOBILE)
        logger.info(f'用户ID: {current_open_user_id}')
        
        # 测试获取用户详情
        logger.info('\n--- 测试获取用户详情 ---')
        user_detail = await user_manager.get_user_detail(TEST_MOBILE)
        logger.info(f'用户详情: {json.dumps(user_detail, indent=2, ensure_ascii=False)}')
        
        # 测试批量查询
        logger.info('\n--- 测试批量查询 ---')
        test_mobiles = [TEST_MOBILE, '13800138000', '13900139000']
        batch_results = await user_manager.batch_get_users_by_mobile(test_mobiles)
        
        for result in batch_results:
            if result['success']:
                logger.info(f"✅ {result['mobile']}: 成功")
            else:
                logger.info(f"❌ {result['mobile']}: 失败 - {result['error']}")
        
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()
        logger.info('\n✅ 用户管理测试完成')
        
    except Exception as error:
        logger.error(f'❌ 用户管理测试失败: {str(error)}')


async def crm_object_test():
    """
    CRM对象测试
    """
    try:
        logger.info('=== CRM对象测试 ===')
        
        # 创建管理器
        auth_manager = FxiaokeAuthManager(CONFIG)
        user_manager = FxiaokeUserManager(auth_manager)
        crm_client = FxiaokeCRMClient(auth_manager)
        
        # 获取用户ID
        current_open_user_id = await user_manager.get_current_open_user_id(TEST_MOBILE)
        
        # 测试获取CRM对象列表
        logger.info('\n--- 测试获取CRM对象列表 ---')
        crm_objects = await crm_client.get_crm_object_list({
            'currentOpenUserId': current_open_user_id
        })
        logger.info(f'CRM对象数量: {len(crm_objects)}')
        
        # 测试获取对象描述
        logger.info('\n--- 测试获取对象描述 ---')
        object_descriptions = await crm_client.get_crm_object_list_descriptions({
            'currentOpenUserId': current_open_user_id
        })
        
        for obj in object_descriptions[:5]:  # 只显示前5个
            logger.info(f"对象: {obj['displayName']} ({obj['apiName']})")
        
        # 测试获取特定对象描述
        if object_descriptions:
            first_object = object_descriptions[0]
            logger.info(f'\n--- 测试获取对象 "{first_object["displayName"]}" 的详细描述 ---')
            
            object_describe = await crm_client.get_crm_object_describe({
                'currentOpenUserId': current_open_user_id,
                'apiName': first_object['apiName'],
                'includeDetail': False
            })
            
            fields = object_describe['fields']
            logger.info(f'字段数量: {len(fields)}')
            logger.info('前5个字段:')
            for field in fields[:5]:
                logger.info(f"  - {field['label']} ({field['apiName']}) - {field['type']}")
        
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()
        logger.info('\n✅ CRM对象测试完成')
        
    except Exception as error:
        logger.error(f'❌ CRM对象测试失败: {str(error)}')


async def crm_data_test():
    """
    CRM数据查询测试
    """
    try:
        logger.info('=== CRM数据查询测试 ===')
        
        # 创建管理器
        auth_manager = FxiaokeAuthManager(CONFIG)
        user_manager = FxiaokeUserManager(auth_manager)
        crm_data_client = FxiaokeCRMDataClient(auth_manager)
        
        # 获取用户ID
        current_open_user_id = await user_manager.get_current_open_user_id(TEST_MOBILE)
        
        # 测试查询客户数据
        logger.info('\n--- 测试查询客户数据 ---')
        customer_data = await crm_data_client.find_customer_data({
            'currentOpenUserId': current_open_user_id,
            'fieldProjection': ['_id', 'name', 'mobile', 'email', 'last_modified_time'],
            'searchQueryInfo': {
                'limit': 3,
                'offset': 0
            }
        })
        
        logger.info(f'客户数据数量: {len(customer_data)}')
        if customer_data:
            logger.info(f'第一个客户: {json.dumps(customer_data[0], indent=2, ensure_ascii=False)}')
        
        # 测试查询联系人数据
        logger.info('\n--- 测试查询联系人数据 ---')
        contact_data = await crm_data_client.find_contact_data({
            'currentOpenUserId': current_open_user_id,
            'fieldProjection': ['_id', 'name', 'mobile', 'email', 'company_name'],
            'searchQueryInfo': {
                'limit': 3,
                'offset': 0
            }
        })
        
        logger.info(f'联系人数据数量: {len(contact_data)}')
        if contact_data:
            logger.info(f'第一个联系人: {json.dumps(contact_data[0], indent=2, ensure_ascii=False)}')
        
        # 测试查询销售机会数据
        logger.info('\n--- 测试查询销售机会数据 ---')
        opportunity_data = await crm_data_client.find_opportunity_data({
            'currentOpenUserId': current_open_user_id,
            'fieldProjection': ['_id', 'name', 'amount', 'stage', 'expected_close_date'],
            'searchQueryInfo': {
                'limit': 3,
                'offset': 0
            }
        })
        
        logger.info(f'销售机会数据数量: {len(opportunity_data)}')
        if opportunity_data:
            logger.info(f'第一个销售机会: {json.dumps(opportunity_data[0], indent=2, ensure_ascii=False)}')
        
        # 清理资源
        auth_manager.destroy()
        user_manager.destroy()
        logger.info('\n✅ CRM数据查询测试完成')
        
    except Exception as error:
        logger.error(f'❌ CRM数据查询测试失败: {str(error)}')


async def main():
    """
    主函数
    """
    import sys
    
    # 获取测试模式
    test_mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    if test_mode == 'user':
        await user_test()
    elif test_mode == 'crm':
        await crm_object_test()
    elif test_mode == 'data':
        await crm_data_test()
    elif test_mode == 'simple':
        await simple_crm_test()
    else:
        # 运行所有测试
        await user_test()
        await crm_object_test()
        await crm_data_test()
        await simple_crm_test()


if __name__ == '__main__':
    asyncio.run(main()) 