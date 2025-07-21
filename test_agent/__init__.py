"""
纷享销客CRM集成工具 (Python版本)

本包提供了纷享销客CRM的完整集成功能，包括认证管理、用户管理、CRM对象管理和数据查询。

主要模块:
- fxiaoke_auth: 认证管理类
- fxiaoke_user: 用户管理类  
- fxiaoke_crm: CRM客户端类
- fxiaoke_crm_data: CRM数据查询类
"""

from .fxiaoke_auth import FxiaokeAuthManager
from .fxiaoke_user import FxiaokeUserManager
from .fxiaoke_crm import FxiaokeCRMClient
from .fxiaoke_crm_data import FxiaokeCRMDataClient

from . import agent

__version__ = "1.0.0"
__author__ = "纷享销客CRM工具"
__description__ = "纷享销客CRM集成工具Python版本"

__all__ = [
    'FxiaokeAuthManager',
    'FxiaokeUserManager', 
    'FxiaokeCRMClient',
    'FxiaokeCRMDataClient'
] 