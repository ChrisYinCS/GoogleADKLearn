import requests
import re
import time
import logging
from typing import Dict, List, Optional, Any
from fxiaoke_auth import FxiaokeAuthManager

logger = logging.getLogger(__name__)


class FxiaokeUserManager:
    """
    纷享销客用户管理类
    负责调用用户相关的API接口
    """
    
    def __init__(self, auth_manager: FxiaokeAuthManager):
        """
        初始化用户管理器
        
        Args:
            auth_manager: 认证管理器实例
        """
        self.auth_manager = auth_manager
        
        # 请求配置
        self.request_config = {
            'baseURL': 'https://open.fxiaoke.com',
            'timeout': 10,
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        # 重试配置
        self.retry_config = {
            'maxRetries': 3,
            'retryDelay': 1000,  # 1秒
            'backoffMultiplier': 2
        }
        
        # 频率限制配置
        self.rate_limit_config = {
            'maxRequestsPerWindow': 100,
            'windowSize': 20,  # 20秒
            'requestQueue': [],
            'lastRequestTime': 0
        }
    
    async def get_user_by_mobile(self, mobile: str) -> Dict[str, Any]:
        """
        根据手机号获取用户信息
        
        Args:
            mobile: 手机号
            
        Returns:
            用户信息字典
        """
        try:
            # 验证参数
            self.validate_mobile(mobile)
            
            # 获取认证信息
            auth_info = await self.auth_manager.get_corp_access_token()
            
            # 构建请求数据
            request_data = {
                'corpAccessToken': auth_info['corpAccessToken'],
                'corpId': auth_info['corpId'],
                'mobile': mobile
            }
            
            # 发送请求
            response = await self.request_with_rate_limit(
                '/cgi/user/getByMobile',
                request_data
            )
            
            # 检查API错误
            if response.get('errorCode') != 0:
                raise Exception(f"API错误: {response.get('errorCode')} - {response.get('errorMessage') or response.get('errorDescription')}")
            
            return response
            
        except Exception as error:
            logger.error(f'[FxiaokeUser] 获取用户信息失败: {str(error)}')
            raise
    
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
            logger.info(f'[FxiaokeUser] 频率限制，等待 {wait_time}秒')
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
                logger.warning(f'[FxiaokeUser] 第{attempt}次请求失败: {str(error)}')
                
                # 如果是最后一次尝试，抛出错误
                if attempt == self.retry_config['maxRetries']:
                    break
                
                # 计算延迟时间（指数退避）
                delay = self.retry_config['retryDelay'] * (self.retry_config['backoffMultiplier'] ** (attempt - 1))
                logger.info(f'[FxiaokeUser] {delay}ms后重试...')
                await self.sleep(delay / 1000)  # 转换为秒
        
        raise Exception(f"请求失败，已重试{self.retry_config['maxRetries']}次: {str(last_error)}")
    
    def validate_mobile(self, mobile: str):
        """
        验证手机号格式
        
        Args:
            mobile: 手机号
        """
        if not mobile:
            raise ValueError('手机号不能为空')
        
        # 简单的手机号格式验证（中国大陆手机号）
        mobile_regex = r'^1[3-9]\d{9}$'
        if not re.match(mobile_regex, mobile):
            raise ValueError('手机号格式不正确')
    
    async def get_current_open_user_id(self, mobile: str) -> str:
        """
        获取用户信息并提取currentOpenUserId
        
        Args:
            mobile: 手机号
            
        Returns:
            currentOpenUserId字符串
        """
        try:
            user_info = await self.get_user_by_mobile(mobile)
            
            # 检查返回的用户信息中是否包含empList
            if user_info.get('empList') and len(user_info['empList']) > 0:
                user = user_info['empList'][0]  # 取第一个匹配的用户
                
                # 检查是否有openUserId字段
                if user.get('openUserId'):
                    return user['openUserId']
                
                raise Exception('用户信息中未找到openUserId字段')
            
            # 如果没有找到用户信息，抛出错误
            raise Exception('未找到匹配的用户信息，请检查手机号是否正确')
            
        except Exception as error:
            logger.error(f'[FxiaokeUser] 获取currentOpenUserId失败: {str(error)}')
            raise
    
    async def get_user_detail(self, mobile: str) -> Dict[str, Any]:
        """
        获取用户详细信息
        
        Args:
            mobile: 手机号
            
        Returns:
            用户详细信息字典
        """
        try:
            user_info = await self.get_user_by_mobile(mobile)
            
            # 检查返回的用户信息中是否包含empList
            if user_info.get('empList') and len(user_info['empList']) > 0:
                user = user_info['empList'][0]  # 取第一个匹配的用户
                
                # 提取关键信息
                user_detail = {
                    'openUserId': user.get('openUserId'),
                    'fullName': user.get('fullName'),
                    'mobile': user.get('mobile'),
                    'email': user.get('email'),
                    'account': user.get('account'),
                    'status': user.get('status'),
                    'gender': user.get('gender'),
                    'isActive': user.get('isActive'),
                    'mainDepartmentIds': user.get('mainDepartmentIds', []),
                    'departmentIds': user.get('departmentIds', [])
                }
                
                return user_detail
            
            # 如果没有找到用户信息，抛出错误
            raise Exception('未找到匹配的用户信息，请检查手机号是否正确')
            
        except Exception as error:
            logger.error(f'[FxiaokeUser] 获取用户详细信息失败: {str(error)}')
            raise
    
    async def batch_get_users_by_mobile(self, mobiles: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取用户信息
        
        Args:
            mobiles: 手机号列表
            
        Returns:
            结果列表，每个元素包含success、data或error
        """
        results = []
        
        for mobile in mobiles:
            try:
                user_info = await self.get_user_by_mobile(mobile)
                results.append({
                    'mobile': mobile,
                    'success': True,
                    'data': user_info
                })
            except Exception as error:
                results.append({
                    'mobile': mobile,
                    'success': False,
                    'error': str(error)
                })
        
        return results
    
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
        logger.info('[FxiaokeUser] 清理用户管理器资源')
        # 清理请求队列
        self.rate_limit_config['requestQueue'].clear() 