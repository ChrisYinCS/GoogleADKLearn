import os
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import asyncio
import datetime
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types 
import datetime

# 启用 LiteLLM 调试模式
import litellm
litellm.set_verbose = True

from .index_run import FxiaokeCRMService, generate_field_projection


DS_API_KEY = os.getenv("DS_API_KEY")
DS_BASE_URL = os.getenv("DS_BASE_URL")

model = LiteLlm(
    model="deepseek/deepseek-chat",  
    api_base=DS_BASE_URL,
    api_key=DS_API_KEY
)

# 创建CRM服务实例
crm_service = FxiaokeCRMService()

# 定义CRM工具函数
async def get_user_id_by_mobile(mobile: str) -> str:
    """
    Retrieves the user ID based on the provided mobile phone number.

    Args:
        mobile (str): The mobile phone number of the user.

    Returns:
        str: The user ID associated with the mobile phone number.
    """
    # 参数验证
    if not mobile or not isinstance(mobile, str):
        raise ValueError("mobile must be a non-empty string")
    
    return await crm_service.get_user_id_by_mobile(mobile)

async def get_crm_objects(user_id: str) -> list:
    """
    Retrieves all CRM objects with their Chinese names and API names.

    Args:
        user_id (str): The ID of the current user.

    Returns:
        list: A list of dictionaries containing CRM object information,
              including Chinese names and API names.
    """
    # 参数验证
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id must be a non-empty string")
    
    return await crm_service.get_crm_objects(user_id)

async def get_object_fields(user_id: str, object_api_name: str) -> list:
    """
    Retrieves field information for a specified CRM object.

    Args:
        user_id (str): The ID of the current user.
        object_api_name (str): The API name of the CRM object.

    Returns:
        list: A list of dictionaries containing field information
              for the specified CRM object. Each field dictionary contains
              only the following keys: apiName, label, helpText, description.
    """
    # 参数验证
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id must be a non-empty string")
    if not object_api_name or not isinstance(object_api_name, str):
        raise ValueError("object_api_name must be a non-empty string")
    
    return await crm_service.get_object_fields(user_id, object_api_name)

async def query_object_data(user_id: str, object_api_name: str, field_projection: list, limit: int = 10, offset: int = 0) -> list:
    """
    Queries data for a specified CRM object with field projection.

    Args:
        user_id (str): The ID of the current user.
        object_api_name (str): The API name of the CRM object to query.
        field_projection (list): List of field names to include in the query results.
        limit (int, optional): Maximum number of records to return. Defaults to 10.
        offset (int, optional): Number of records to skip. Defaults to 0.

    Returns:
        list: A list of dictionaries containing the queried CRM data records.
    """
    # 参数验证
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id must be a non-empty string")
    if not object_api_name or not isinstance(object_api_name, str):
        raise ValueError("object_api_name must be a non-empty string")
    if not isinstance(field_projection, list):
        raise ValueError("field_projection must be a list")
    if not isinstance(limit, int) or limit < 1:
        limit = 10
    if not isinstance(offset, int) or offset < 0:
        offset = 0
    
    return await crm_service.query_object_data(user_id, object_api_name, field_projection, limit, offset)

async def get_user_by_mobile(mobile: str) -> dict:
    """
    Retrieves user information based on the provided mobile phone number.

    Args:
        mobile (str): The mobile phone number of the user.

    Returns:
        dict: A dictionary containing the user information.
    """
    # 参数验证
    if not mobile or not isinstance(mobile, str):
        raise ValueError("mobile must be a non-empty string")
    
    return await crm_service.get_user_by_mobile(mobile)

async def get_user_detail(mobile: str) -> dict:
    """
    Retrieves detailed user information based on the provided mobile phone number.

    Args:
        mobile (str): The mobile phone number of the user.

    Returns:
        dict: A dictionary containing detailed user information.
    """
    # 参数验证
    if not mobile or not isinstance(mobile, str):
        raise ValueError("mobile must be a non-empty string")
    
    return await crm_service.get_user_detail(mobile)

async def batch_get_users_by_mobile(mobiles: list) -> list:
    """
    Retrieves user information for multiple mobile phone numbers in batch.

    Args:
        mobiles (list): A list of mobile phone numbers.

    Returns:
        list: A list of dictionaries containing user information for each mobile number.
    """
    # 参数验证
    if not isinstance(mobiles, list):
        raise ValueError("mobiles must be a list")
    if not mobiles:
        raise ValueError("mobiles list cannot be empty")
    for mobile in mobiles:
        if not isinstance(mobile, str) or not mobile:
            raise ValueError("All mobile numbers must be non-empty strings")
    
    return await crm_service.batch_get_users_by_mobile(mobiles)

async def generate_field_projection_tool(fields: list, target_labels: list) -> list:
    """
    Generates field projection parameters based on field labels.

    Args:
        fields (list): A list of field information dictionaries.
        target_labels (list): A list of target field labels to match.

    Returns:
        list: A list of field projection parameters including '_id' and matched field API names.
    """
    # 参数验证
    if not isinstance(fields, list):
        raise ValueError("fields must be a list")
    if not isinstance(target_labels, list):
        raise ValueError("target_labels must be a list")
    if not target_labels:
        raise ValueError("target_labels list cannot be empty")
    
    return generate_field_projection(fields, target_labels)


experience_list = [
    {
        "标题": "毛利计算",
        "目的": "计算销售的毛利",
        "方法":  '''毛利=销售金额-成本金额。销售金额从【销售订单】中获取，成本金额从【实施立项申请】中获取，他们之间的关联是都挂靠在同一个【商机】下
        原则上，销售的一个订单的毛利率理应接近【商机】中的预估毛利率，如果【商机】的毛利率与【销售订单】的毛利率差异较大，则需要根据以下情况手动调整【销售订单】的一些数据：
        1、一个实施立项申请下涉及多个订单，导出数据中每个订单的金额对应的成本都是总成本，这里需要手动调整，按照实施服务的占比分摊成本
        2、如果实际签约金额与立项时商机金额不一致，会导致毛利变化，需要按照整单毛利率去重新计算成本对应实际签约金额
        3、如果实际签约 结构类型和立项商机结构金额不一致，会导致毛利变化，需要按照实际签约结构类型重新计算毛利
        4、纯软件不涉及立项申请的，毛利=不含税的软件收入
        '''
    }
]

experience_prompt = "\n".join([f"{item['标题']}: {item['目的']}\n{item['方法']}" for item in experience_list])


system_prompt = f"""
你是一个CRM专家，你熟悉CRM的各个模块和业务流程，你熟悉CRM的各个字段和业务逻辑，你熟悉CRM的各个工具和API。
当用户提到与"客户、线索、商机、订单、合同、回款、拜访、产品、库存、审批、报表"等可能来源于 CRM 的主题时，
你应在不假设字段含义的前提下，判断是否需要实时数据，并调用工具获取数据。
你无法提前获知用户的CRM中的对象和字段的api_name，所以如果一个工具调用需要传入对象和字段，请先调用get_crm_objects和get_object_fields工具获取对象和字段信息，然后再调用工具。
如果工具返回错误，礼貌地告知用户。
- 调用决策原则
    - 意图触发：只要用户问题涉及"查、看、列、统计、多少、最新、我的、某客户、某订单"等关键词，且你认为答案可能存在于 CRM，即可触发。
    - 最小必要：不提前批量抓取，只在单轮对话中按需提供。
    - 零规则侵入：所有业务逻辑由 CRM 返回的数据本身或用户在对话中即时声明。
    - 可解释性：在调用前用一句自然语言向用户确认或说明，例如"我去查一下您名下最近 7 天的线索"。
    - 严禁假造：严禁假造CRM中的数据，所有数据都应该来自于CRM系统工具的返回，如果用户提问中存在不明确的地方，请用户确认后再进行处理。

如果用户有提前声明的一些业务处理逻辑，这些逻辑将列举在下方。当用户的提问与这些逻辑相关时，请按照以下逻辑进行处理：
{experience_prompt}

当前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
"""


root_agent = Agent(
    name="CRM_agent",
    model=model, 
    description="用于进行CRM查询的Agent智能体",
    instruction=system_prompt,
    tools=[
        get_user_id_by_mobile,
        get_crm_objects,
        get_object_fields,
        query_object_data,
        get_user_by_mobile,
        get_user_detail,
        batch_get_users_by_mobile,
        generate_field_projection_tool
    ], 
)



