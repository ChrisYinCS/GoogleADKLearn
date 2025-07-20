import os
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm 
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types 

DS_API_KEY = os.getenv("DS_API_KEY")
DS_BASE_URL = os.getenv("DS_BASE_URL")

model = LiteLlm(
    model="deepseek/deepseek-chat",  
    api_base=DS_BASE_URL,
    api_key=DS_API_KEY
)

CRM_agent = Agent(
    name="CRM_agent",
    model=model, 
    description="用于进行CRM查询的Agent智能体",
    instruction="你是一个有帮助的CRM助手。"
                "当用户提到与“客户、线索、商机、订单、合同、回款、拜访、产品、库存、审批、报表”等可能来源于 CRM 的主题时，"
                "你应在不假设字段含义的前提下，判断是否需要实时数据，并调用'get_crm_data'工具获取数据。"
                "如果工具返回错误，礼貌地告知用户。",
    tools=[get_crm_data], 
)