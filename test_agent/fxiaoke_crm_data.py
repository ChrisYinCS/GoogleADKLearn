import requests
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from .fxiaoke_auth import FxiaokeAuthManager

logger = logging.getLogger(__name__)


class FxiaokeCRMDataClient:
    """
    纷享销客CRM业务对象数据查询类
    提供CRM业务对象的数据查询功能
    """
    
    def __init__(self, auth_manager: FxiaokeAuthManager):
        """
        初始化CRM数据客户端
        
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
        
        # 频率限制配置（根据API文档：100次/20秒）
        self.rate_limit_config = {
            'maxRequestsPerWindow': 100,
            'windowSize': 20,  # 20秒
            'requestQueue': [],
            'lastRequestTime': 0
        }
    
    async def find_simple_data(
        self,
        currentOpenUserId: str,
        dataObjectApiName: str,
        fieldProjection: Optional[List[str]] = None,
        searchQueryInfo: Optional[Dict[str, Any]] = None,
        ignoreMediaIdConvert: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        通用查询CRM任意对象数据
        Args:
            currentOpenUserId: 当前用户ID
            dataObjectApiName: 对象ApiName
            fieldProjection: 返回字段列表
            searchQueryInfo: 查询条件，需要通过build_search_query_info方法构建
            ignoreMediaIdConvert: 是否忽略MediaId转换
            kwargs: 其他可选参数
        Returns:
            数据列表
        """
        if not currentOpenUserId:
            raise ValueError('currentOpenUserId是必需参数')
        if not dataObjectApiName:
            raise ValueError('dataObjectApiName是必需参数')

        auth_info = await self.auth_manager.get_corp_access_token()
        data = {
            'dataObjectApiName': dataObjectApiName,
            'ignoreMediaIdConvert': ignoreMediaIdConvert
        }
        if fieldProjection is not None:
            data['field_projection'] = fieldProjection
        if searchQueryInfo is not None:
            data['search_query_info'] = searchQueryInfo

        request_data = {
            'corpAccessToken': auth_info['corpAccessToken'],
            'corpId': auth_info['corpId'],
            'currentOpenUserId': currentOpenUserId,
            'data': data
        }

        logger.info('[FxiaokeCRMData] 请求业务对象数据，参数: %s', request_data)
        response = await self.request_with_rate_limit(
            '/cgi/crm/custom/v2/data/findSimple',
            request_data
        )
        if response.get('code', 0) != 0:
            logger.error(f"[FxiaokeCRMData] API返回错误: {response.get('msg')}")
            raise Exception(f"API Error: {response.get('msg')}")
        return response.get('data', {}).get('dataList', [])
    
    def build_search_query_info(self, search_query_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        构建查询条件
        
        Args:
            search_query_info: 查询条件
            
        Returns:
            构建后的查询条件
        """
        result = {}
        search_query_info = search_query_info or {}
        
        # 添加基本查询参数
        if search_query_info.get('limit') is not None:
            result['limit'] = str(search_query_info['limit'])
        
        if search_query_info.get('offset') is not None:
            result['offset'] = str(search_query_info['offset'])
        
        # 添加过滤条件
        if search_query_info.get('filters'):
            filters = search_query_info['filters']
            result['filters'] = {
                'field_name': filters.get('field_name'),
                'field_values': filters['field_values'] if isinstance(filters['field_values'], list) else [filters['field_values']],
                'operator': filters.get('operator')
            }
        
        # 添加排序条件
        if search_query_info.get('orders') and isinstance(search_query_info['orders'], list):
            result['orders'] = [
                {
                    'fieldName': order['fieldName'],
                    'isAsc': "true" if order.get('isAsc') else "false"
                }
                for order in search_query_info['orders']
            ]
        
        return result
    
    def validate_params(self, params: Dict[str, Any]):
        """
        验证必需参数
        
        Args:
            params: 参数对象
        """
        if not params:
            raise ValueError('参数不能为空')
        
        if not params.get('currentOpenUserId'):
            raise ValueError('currentOpenUserId是必需参数')
        
        if not params.get('dataObjectApiName'):
            raise ValueError('dataObjectApiName是必需参数')
        
        if not isinstance(params.get('fieldProjection', []), list):
            raise ValueError('fieldProjection必须是数组类型')
    
    async def request_with_rate_limit(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        带频率限制的请求方法
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            API响应字典
        """
        # 检查频率限制
        await self.check_rate_limit()
        
        # 发送请求
        response = await self.request_with_retry(endpoint, data)
        
        # 更新请求时间
        self.rate_limit_config['lastRequestTime'] = time.time()
        
        return response
    
    async def check_rate_limit(self):
        """检查频率限制"""
        now = time.time()
        time_since_last_request = now - self.rate_limit_config['lastRequestTime']
        
        # 如果距离上次请求时间小于窗口大小，需要等待
        if time_since_last_request < self.rate_limit_config['windowSize']:
            wait_time = self.rate_limit_config['windowSize'] - time_since_last_request
            logger.info(f'[FxiaokeCRMData] 频率限制，等待 {wait_time}秒')
            await self.sleep(wait_time)
    
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
                logger.warning(f'[FxiaokeCRMData] 第{attempt}次请求失败: {str(error)}')
                
                # 如果是最后一次尝试，抛出错误
                if attempt == self.retry_config['maxRetries']:
                    break
                
                # 计算延迟时间（指数退避）
                delay = self.retry_config['retryDelay'] * (self.retry_config['backoffMultiplier'] ** (attempt - 1))
                logger.info(f'[FxiaokeCRMData] {delay}ms后重试...')
                await self.sleep(delay / 1000)  # 转换为秒
        
        raise Exception(f"请求失败，已重试{self.retry_config['maxRetries']}次: {str(last_error)}")
    
    async def find_data_by_time_range(self, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        根据时间范围查询数据
        
        Args:
            params: 查询参数
                - currentOpenUserId: 当前用户ID
                - dataObjectApiName: 对象ApiName
                - fieldProjection: 返回字段列表
                - startTime: 开始时间
                - endTime: 结束时间
                - timeField: 时间字段名（默认'last_modified_time'）
                - limit: 查询条数
                - offset: 查询偏移量
                
        Returns:
            数据列表
        """
        try:
            params = params or {}
            
            # 转换时间格式
            start_time = self.convert_to_timestamp(params.get('startTime'))
            end_time = self.convert_to_timestamp(params.get('endTime'))
            time_field = params.get('timeField', 'last_modified_time')
            
            # 构建时间范围过滤条件
            search_query_info = {
                'limit': params.get('limit'),
                'offset': params.get('offset'),
                'filters': {
                    'field_name': time_field,
                    'field_values': [start_time, end_time],
                    'operator': 'BETWEEN'
                },
                'orders': [
                    {
                        'fieldName': time_field,
                        'isAsc': False
                    }
                ]
            }
            
            # 构建完整查询参数
            query_params = {
                'currentOpenUserId': params['currentOpenUserId'],
                'dataObjectApiName': params['dataObjectApiName'],
                'fieldProjection': params.get('fieldProjection', []),
                'searchQueryInfo': search_query_info
            }
            
            return await self.find_simple_data(query_params['currentOpenUserId'], query_params['dataObjectApiName'], query_params['fieldProjection'], query_params['searchQueryInfo'])
            
        except Exception as error:
            logger.error(f'[FxiaokeCRMData] 根据时间范围查询数据失败: {str(error)}')
            raise
    
    def convert_to_timestamp(self, time_value: Union[datetime, str, int, float]) -> int:
        """
        转换时间为时间戳
        
        Args:
            time_value: 时间值，可以是datetime对象、字符串、时间戳
            
        Returns:
            时间戳（毫秒）
        """
        if isinstance(time_value, datetime):
            return int(time_value.timestamp() * 1000)
        elif isinstance(time_value, str):
            # 尝试解析字符串时间
            try:
                dt = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                return int(dt.timestamp() * 1000)
            except ValueError:
                raise ValueError(f'无法解析时间字符串: {time_value}')
        elif isinstance(time_value, (int, float)):
            # 如果是秒级时间戳，转换为毫秒
            if time_value < 10000000000:  # 秒级时间戳
                return int(time_value * 1000)
            else:  # 毫秒级时间戳
                return int(time_value)
        else:
            raise ValueError(f'不支持的时间格式: {type(time_value)}')
    
    def set_retry_config(self, config: Dict[str, Any]):
        """
        设置重试配置
        
        Args:
            config: 重试配置字典
        """
        self.retry_config.update(config)
    
    def set_rate_limit_config(self, config: Dict[str, Any]):
        """
        设置频率限制配置
        
        Args:
            config: 频率限制配置字典
        """
        self.rate_limit_config.update(config)
    
    def set_timeout(self, timeout: int):
        """
        设置请求超时时间
        
        Args:
            timeout: 超时时间（秒）
        """
        self.request_config['timeout'] = timeout
    
    @staticmethod
    async def sleep(seconds: float):
        """
        异步睡眠
        
        Args:
            seconds: 睡眠秒数
        """
        import asyncio
        await asyncio.sleep(seconds)
    
    def destroy(self):
        """清理资源"""
        logger.info('[FxiaokeCRMData] 清理CRM数据客户端资源')
        # 清理请求队列
        self.rate_limit_config['requestQueue'].clear() 