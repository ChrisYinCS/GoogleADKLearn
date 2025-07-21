import logging
from typing import List, Dict, Any
from .fxiaoke_auth import FxiaokeAuthManager
from .fxiaoke_user import FxiaokeUserManager
from .fxiaoke_crm import FxiaokeCRMClient
from .fxiaoke_crm_data import FxiaokeCRMDataClient

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG = {
    'appId': 'FSAID_131882c',
    'appSecret': '1a6d145803f84712ae4a4dee26efe7d3',
    'permanentCode': 'B80A369A935263232BAEBC5D42542899'
}


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


class FxiaokeCRMService:
    """
    纷享销客CRM服务类，提供统一的CRM操作接口
    """
    
    def __init__(self):
        """
        初始化CRM服务
        
        Args:
            config: 配置信息，包含appId、appSecret、permanentCode
        """
        self.config = CONFIG
        self.auth_manager = None
        self.user_manager = None
        self.crm_client = None
        self.crm_data_client = None
    
    async def initialize(self):
        """
        初始化所有管理器
        """
        self.auth_manager = FxiaokeAuthManager(self.config)
        self.user_manager = FxiaokeUserManager(self.auth_manager)
        self.crm_client = FxiaokeCRMClient(self.auth_manager)
        self.crm_data_client = FxiaokeCRMDataClient(self.auth_manager)
    
    async def get_user_id_by_mobile(self, mobile: str) -> str:
        """
        根据手机号获取用户ID
        
        Args:
            mobile: 手机号
            
        Returns:
            用户ID
        """
        if not self.user_manager:
            await self.initialize()
        return await self.user_manager.get_current_open_user_id(mobile)
    
    async def get_crm_objects(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取所有CRM对象的中文名称和API名称
        
        Args:
            user_id: 用户ID
            
        Returns:
            CRM对象列表
        """
        if not self.crm_client:
            await self.initialize()
        return await self.crm_client.get_crm_object_list_descriptions({
            'currentOpenUserId': user_id
        })
    
    async def get_object_fields(self, user_id: str, object_api_name: str) -> List[Dict[str, Any]]:
        """
        获取指定对象的字段信息
        
        Args:
            user_id: 用户ID
            object_api_name: 对象API名称
            
        Returns:
            字段信息列表，只包含 apiName、label、helpText、description 字段
        """
        if not self.crm_client:
            await self.initialize()
        object_describe = await self.crm_client.get_crm_object_describe({
            'currentOpenUserId': user_id,
            'apiName': object_api_name,
            'includeDetail': False
        })
        
        # 只返回指定的字段
        filtered_fields = []
        for field in object_describe['fields']:
            filtered_field = {
                'apiName': field.get('apiName'),
                'label': field.get('label'),
                'helpText': field.get('helpText'),
                'description': field.get('description')
            }
            filtered_fields.append(filtered_field)
        
        return filtered_fields
    

    async def query_object_data(self, user_id: str, object_api_name: str, 
                               field_projection: List[str], search_query_info: Dict[str, Any]
                               ) -> List[Dict[str, Any]]:
        """
        查询指定对象的数据
        
        Args:
            user_id: 用户ID
            object_api_name: 对象API名称
            field_projection: 字段投影列表
            search_query_info: 详细查询条件，需要通过build_search_query_info方法构建
            
        Returns:
            查询结果数据列表
        """
        if not self.crm_data_client:
            await self.initialize()
        
        
        return await self.crm_data_client.find_simple_data(
            currentOpenUserId=user_id,
            dataObjectApiName=object_api_name,
            fieldProjection=field_projection,
            searchQueryInfo=search_query_info
        )
    
    async def get_user_by_mobile(self, mobile: str) -> Dict[str, Any]:
        """
        根据手机号获取用户信息
        
        Args:
            mobile: 手机号
            
        Returns:
            用户信息
        """
        if not self.user_manager:
            await self.initialize()
        return await self.user_manager.get_user_by_mobile(mobile)
    
    async def get_user_detail(self, mobile: str) -> Dict[str, Any]:
        """
        获取用户详细信息
        
        Args:
            mobile: 手机号
            
        Returns:
            用户详细信息
        """
        if not self.user_manager:
            await self.initialize()
        return await self.user_manager.get_user_detail(mobile)
    
    async def batch_get_users_by_mobile(self, mobiles: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取用户信息
        
        Args:
            mobiles: 手机号列表
            
        Returns:
            批量查询结果
        """
        if not self.user_manager:
            await self.initialize()
        return await self.user_manager.batch_get_users_by_mobile(mobiles)
    
    def destroy(self):
        """
        清理资源
        """
        if self.auth_manager:
            self.auth_manager.destroy()
        if self.user_manager:
            self.user_manager.destroy() 



