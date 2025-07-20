import requests
import time
import logging
from typing import Dict, List, Optional, Any
from fxiaoke_auth import FxiaokeAuthManager

logger = logging.getLogger(__name__)


class FxiaokeCRMClient:
    """
    纷享销客CRM API调用类
    提供CRM相关接口的调用功能
    """
    
    def __init__(self, auth_manager: FxiaokeAuthManager):
        """
        初始化CRM客户端
        
        Args:
            auth_manager: 认证管理器实例
        """
        self.auth_manager = auth_manager
        
        # 请求配置
        self.request_config = {
            'baseURL': 'https://open.fxiaoke.com',
            'timeout': 15,
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        # 重试配置
        self.retry_config = {
            'maxRetries': 3,
            'retryDelay': 1000,
            'backoffMultiplier': 2
        }
    
    async def get_object_list(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取CRM对象列表
        
        Args:
            params: 请求参数
                - currentOpenUserId: 当前用户ID
                - queryParams: 查询参数
                - objectType: 对象类型
                - pageSize: 每页数量
                - pageNumber: 页码
                
        Returns:
            返回对象列表数据
        """
        try:
            params = params or {}
            
            # 获取认证信息
            auth_info = await self.auth_manager.get_corp_access_token()
            
            # 构建请求参数
            request_data = {
                'corpAccessToken': auth_info['corpAccessToken'],
                'corpId': auth_info['corpId'],
                'currentOpenUserId': params.get('currentOpenUserId'),
                **(params.get('queryParams') or {})
            }

            logger.info('[FxiaokeCRM] 请求对象列表，参数: %s', {
                'corpId': auth_info['corpId'],
                'currentOpenUserId': params.get('currentOpenUserId'),
                'objectType': params.get('objectType', '未指定')
            })

            # 发送请求
            response = await self.request_with_retry('/cgi/crm/v2/object/list', request_data)
            
            logger.info('[FxiaokeCRM] 对象列表获取成功')
            return response
            
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取对象列表失败: {str(error)}')
            raise
    
    async def get_crm_object_list(self, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        获取CRM对象列表（获取系统中所有可用的对象类型）
        
        Args:
            params: 查询参数
                - currentOpenUserId: 当前用户ID
                
        Returns:
            CRM对象数组，每个对象包含以下字段：
            - describeApiName: 对象的API名称
            - describeDisplayName: 对象的中文显示名称
            - defineType: 对象定义类型
            - isActive: 对象是否激活
            - iconPath: 图标路径
            - iconIndex: 图标索引
            - hideButton: 是否隐藏按钮
            - publicObject: 是否为公共对象
        """
        try:
            params = params or {}
            
            # 获取认证信息
            auth_info = await self.auth_manager.get_corp_access_token()
            
            # 构建请求参数
            request_data = {
                'corpAccessToken': auth_info['corpAccessToken'],
                'corpId': auth_info['corpId'],
                'currentOpenUserId': params.get('currentOpenUserId')
            }

            logger.info('[FxiaokeCRM] 请求CRM对象列表，参数: %s', {
                'corpId': auth_info['corpId'],
                'currentOpenUserId': params.get('currentOpenUserId')
            })

            # 发送请求
            response = await self.request_with_retry('/cgi/crm/v2/object/list', request_data)
            
            # 提取并返回objects数组
            if response.get('data') and response['data'].get('objects') and isinstance(response['data']['objects'], list):
                logger.info(f'[FxiaokeCRM] CRM对象列表获取成功，对象数量: {len(response["data"]["objects"])}')
                return response['data']['objects']
            
            logger.info('[FxiaokeCRM] CRM对象列表获取成功，但未找到对象数据')
            return []
            
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取CRM对象列表失败: {str(error)}')
            raise
    
    async def get_crm_object_list_descriptions(self, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        获取CRM对象列表的中文描述（用于LLM分析）
        
        Args:
            params: 查询参数
                - currentOpenUserId: 当前用户ID
                
        Returns:
            中文描述列表，每个对象包含以下字段：
            - apiName: 对象的API名称
            - displayName: 对象的中文显示名称
            - defineType: 对象定义类型
            - isActive: 对象是否激活
            - publicObject: 是否为公共对象
        """
        try:
            objects = await self.get_crm_object_list(params)
            
            if isinstance(objects, list):
                # 提取所有对象的中文描述
                descriptions = [
                    {
                        'apiName': obj['describeApiName'],
                        'displayName': obj['describeDisplayName'],
                        'defineType': obj['defineType'],
                        'isActive': obj['isActive'],
                        'publicObject': obj['publicObject']
                    }
                    for obj in objects
                    if obj.get('isActive') and obj.get('describeDisplayName')
                ]
                
                logger.info(f'[FxiaokeCRM] 获取到 {len(descriptions)} 个CRM对象描述')
                return descriptions
            
            return []
            
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取CRM对象描述失败: {str(error)}')
            raise
    
    async def get_crm_object_display_names(self, params: Dict[str, Any] = None) -> List[str]:
        """
        获取CRM对象的纯中文描述列表（用于LLM指令关联分析）
        
        Args:
            params: 查询参数
                - currentOpenUserId: 当前用户ID
                
        Returns:
            中文描述字符串数组
        """
        try:
            descriptions = await self.get_crm_object_list_descriptions(params)
            
            # 只返回中文描述名称
            display_names = [desc['displayName'] for desc in descriptions]
            
            logger.info(f'[FxiaokeCRM] 获取到 {len(display_names)} 个CRM对象中文描述')
            return display_names
            
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取CRM对象中文描述失败: {str(error)}')
            raise
    
    async def get_crm_object_describe(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取单个CRM对象的详细描述信息
        
        Args:
            params: 查询参数
                - currentOpenUserId: 当前用户ID
                - apiName: 对象的apiName
                - includeDetail: 是否包括从对象
                - filterInactive: 是否过滤非激活字段（默认True）
                - filterSystem: 是否过滤系统字段（默认True）
                - filterEmpty: 是否过滤空标签字段（默认True）
                
        Returns:
            对象详细描述信息，包含以下字段：
            - data: 原始API返回数据
            - fields: 提取的字段信息数组
        """
        try:
            params = params or {}
            current_open_user_id = params.get('currentOpenUserId')
            api_name = params.get('apiName')
            
            if not current_open_user_id:
                raise ValueError('currentOpenUserId是必需参数')
            if not api_name:
                raise ValueError('apiName是必需参数')
            
            # 获取认证信息
            auth_info = await self.auth_manager.get_corp_access_token()
            
            # 构建请求参数
            request_data = {
                'corpAccessToken': auth_info['corpAccessToken'],
                'corpId': auth_info['corpId'],
                'currentOpenUserId': current_open_user_id,
                'apiName': api_name
            }

            logger.info('[FxiaokeCRM] 请求对象描述，参数: %s', {
                'corpId': auth_info['corpId'],
                'currentOpenUserId': current_open_user_id,
                'apiName': api_name
            })

            # 发送请求
            response = await self.request_with_retry('/cgi/crm/v2/object/describe', request_data)
            
            # 提取字段信息
            fields = self.extract_field_info(response)
            
            # 过滤字段
            filtered_fields = self.filter_fields(fields, params)
            
            result = {
                'data': response,
                'fields': filtered_fields
            }
            
            logger.info(f'[FxiaokeCRM] 对象描述获取成功，字段数量: {len(filtered_fields)}')
            return result
            
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取对象描述失败: {str(error)}')
            raise
    
    async def batch_get_crm_object_describe(self, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        批量获取CRM对象描述信息
        
        Args:
            params: 查询参数
                - currentOpenUserId: 当前用户ID
                - apiNames: 对象apiName列表
                - includeDetail: 是否包括从对象
                - filterInactive: 是否过滤非激活字段
                - filterSystem: 是否过滤系统字段
                - filterEmpty: 是否过滤空标签字段
                
        Returns:
            对象描述信息列表
        """
        try:
            params = params or {}
            api_names = params.get('apiNames', [])
            
            if not api_names:
                raise ValueError('apiNames是必需参数且不能为空')
            
            results = []
            
            for api_name in api_names:
                try:
                    object_params = {
                        'currentOpenUserId': params.get('currentOpenUserId'),
                        'apiName': api_name,
                        'includeDetail': params.get('includeDetail', True),
                        'filterInactive': params.get('filterInactive', True),
                        'filterSystem': params.get('filterSystem', True),
                        'filterEmpty': params.get('filterEmpty', True)
                    }
                    
                    result = await self.get_crm_object_describe(object_params)
                    results.append({
                        'apiName': api_name,
                        'success': True,
                        'data': result
                    })
                    
                except Exception as error:
                    results.append({
                        'apiName': api_name,
                        'success': False,
                        'error': str(error)
                    })
            
            return results
            
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 批量获取对象描述失败: {str(error)}')
            raise
    
    def extract_field_info(self, describe_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从对象描述信息中提取字段信息
        
        Args:
            describe_info: 对象描述信息
            
        Returns:
            字段信息列表
        """
        fields = []
        
        if describe_info.get('data') and describe_info['data'].get('fields'):
            for field in describe_info['data']['fields']:
                field_info = {
                    'apiName': field.get('apiName'),
                    'label': field.get('label'),
                    'type': field.get('type'),
                    'description': field.get('description', ''),
                    'isRequired': field.get('isRequired', False),
                    'helpText': field.get('helpText', ''),
                    'isActive': field.get('isActive', True),
                    'defineType': field.get('defineType'),
                    'defaultValue': field.get('defaultValue'),
                    'options': field.get('options', [])
                }
                fields.append(field_info)
        
        return fields
    
    def filter_fields(self, fields: List[Dict[str, Any]], params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        过滤字段
        
        Args:
            fields: 字段列表
            params: 过滤参数
            
        Returns:
            过滤后的字段列表
        """
        params = params or {}
        filtered_fields = fields
        
        # 过滤非激活字段
        if params.get('filterInactive', True):
            filtered_fields = [f for f in filtered_fields if f.get('isActive', True)]
        
        # 过滤系统字段
        if params.get('filterSystem', True):
            filtered_fields = [f for f in filtered_fields if not self.is_system_field(f.get('apiName', ''))]
        
        # 过滤空标签字段
        if params.get('filterEmpty', True):
            filtered_fields = [f for f in filtered_fields if f.get('label')]
        
        return filtered_fields
    
    def is_system_field(self, api_name: str) -> bool:
        """
        判断是否为系统字段
        
        Args:
            api_name: 字段API名称
            
        Returns:
            是否为系统字段
        """
        system_fields = {
            '_id', 'create_time', 'last_modified_time', 'owner_id', 'owner_name',
            'create_user_id', 'create_user_name', 'last_modified_user_id', 'last_modified_user_name'
        }
        return api_name in system_fields
    
    async def get_customer_list(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取客户列表
        
        Args:
            params: 查询参数
                
        Returns:
            客户列表数据
        """
        try:
            params = params or {}
            params['objectType'] = 'Customer'
            return await self.get_object_list(params)
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取客户列表失败: {str(error)}')
            raise
    
    async def get_contact_list(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取联系人列表
        
        Args:
            params: 查询参数
                
        Returns:
            联系人列表数据
        """
        try:
            params = params or {}
            params['objectType'] = 'Contact'
            return await self.get_object_list(params)
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取联系人列表失败: {str(error)}')
            raise
    
    async def get_opportunity_list(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        获取销售机会列表
        
        Args:
            params: 查询参数
                
        Returns:
            销售机会列表数据
        """
        try:
            params = params or {}
            params['objectType'] = 'Opportunity'
            return await self.get_object_list(params)
        except Exception as error:
            logger.error(f'[FxiaokeCRM] 获取销售机会列表失败: {str(error)}')
            raise
    
    async def request_with_retry(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        带重试机制的请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            API响应字典
        """
        last_error = None
        
        for attempt in range(1, self.retry_config['maxRetries'] + 1):
            try:
                url = f"{self.request_config['baseURL']}{endpoint}"
                
                response = requests.post(
                    url,
                    json=data,
                    headers=self.request_config['headers'],
                    timeout=self.request_config['timeout']
                )
                
                response.raise_for_status()
                return response.json()
                
            except Exception as error:
                last_error = error
                logger.warning(f'[FxiaokeCRM] 第{attempt}次请求失败: {str(error)}')
                
                # 如果是最后一次尝试，抛出错误
                if attempt == self.retry_config['maxRetries']:
                    break
                
                # 计算延迟时间（指数退避）
                delay = self.retry_config['retryDelay'] * (self.retry_config['backoffMultiplier'] ** (attempt - 1))
                logger.info(f'[FxiaokeCRM] {delay}ms后重试...')
                await self.sleep(delay / 1000)  # 转换为秒
        
        raise Exception(f"请求失败，已重试{self.retry_config['maxRetries']}次: {str(last_error)}")
    
    @staticmethod
    async def sleep(seconds: float):
        """
        异步睡眠
        
        Args:
            seconds: 睡眠秒数
        """
        import asyncio
        await asyncio.sleep(seconds)
    
    async def get_auth_info(self) -> Dict[str, Any]:
        """
        获取认证信息
        
        Returns:
            认证信息字典
        """
        return await self.auth_manager.get_corp_access_token()
    
    def is_auth_valid(self) -> bool:
        """
        检查认证是否有效
        
        Returns:
            认证是否有效
        """
        return self.auth_manager.is_token_valid() 