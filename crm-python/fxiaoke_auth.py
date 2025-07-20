import requests
import time
import hashlib
import hmac
import base64
import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FxiaokeAuthManager:
    """
    纷享销客CRM授权管理类
    负责获取、缓存和自动刷新企业访问令牌
    """
    
    def __init__(self, config: Dict[str, str] = None):
        """
        初始化认证管理器
        
        Args:
            config: 配置字典，包含appId、appSecret、permanentCode
        """
        self.config = config or {}
        self.app_id = self.config.get('appId')
        self.app_secret = self.config.get('appSecret')
        self.permanent_code = self.config.get('permanentCode')
        
        # 缓存相关
        self.token_cache = {
            'corpAccessToken': None,
            'corpId': None,
            'expiresIn': None,
            'createdAt': None,
            'lastRefreshTime': None
        }
        
        # 重试配置
        self.retry_config = {
            'maxRetries': 3,
            'retryDelay': 1000,  # 1秒
            'backoffMultiplier': 2
        }
        
        # 时间配置（秒）
        self.time_config = {
            'cacheMinTime': 6600,        # 最小缓存时间
            'refreshWindowStart': 6650,  # 开始刷新窗口
            'refreshWindowEnd': 7200,    # 结束刷新窗口
            'maxTokenLifetime': 7200     # 最大token生命周期
        }
        
        # 请求配置
        self.request_config = {
            'baseURL': 'https://open.fxiaoke.com',
            'timeout': 10,
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
        # 验证配置
        self.validate_config()
        
        # 自动刷新定时器
        self.refresh_timer = None
    
    def validate_config(self):
        """验证配置参数"""
        if not self.app_id:
            raise ValueError('appId是必需参数')
        if not self.app_secret:
            raise ValueError('appSecret是必需参数')
        if not self.permanent_code:
            raise ValueError('permanentCode是必需参数')
    
    async def get_corp_access_token(self) -> Dict[str, Any]:
        """
        获取企业访问令牌
        
        Returns:
            返回token信息字典
        """
        try:
            # 检查缓存是否有效
            if self.is_token_valid():
                logger.info('[FxiaokeAuth] 使用缓存的token')
                return self.token_cache
            
            # 检查是否需要刷新
            if self.should_refresh_token():
                logger.info('[FxiaokeAuth] 开始刷新token')
            else:
                logger.info('[FxiaokeAuth] 获取新token')
            
            # 请求新token
            token_data = await self.request_token_with_retry()
            
            # 更新缓存
            self.update_token_cache(token_data)
            
            logger.info(f'[FxiaokeAuth] Token获取成功，过期时间: {token_data["expiresIn"]} 秒')
            return self.token_cache
            
        except Exception as error:
            logger.error(f'[FxiaokeAuth] 获取token失败: {str(error)}')
            raise
    
    async def request_token_with_retry(self) -> Dict[str, Any]:
        """
        带重试机制的token请求
        
        Returns:
            token数据字典
        """
        last_error = None
        
        for attempt in range(1, self.retry_config['maxRetries'] + 1):
            try:
                response = await self.request_token()
                
                # 检查错误码
                if response.get('errorCode') != 0:
                    raise Exception(f"API错误: {response.get('errorCode')} - {response.get('errorMessage')}")
                
                return response
                
            except Exception as error:
                last_error = error
                logger.warning(f'[FxiaokeAuth] 第{attempt}次请求失败: {str(error)}')
                
                # 如果是最后一次尝试，抛出错误
                if attempt == self.retry_config['maxRetries']:
                    break
                
                # 计算延迟时间（指数退避）
                delay = self.retry_config['retryDelay'] * (self.retry_config['backoffMultiplier'] ** (attempt - 1))
                logger.info(f'[FxiaokeAuth] {delay}ms后重试...')
                await self.sleep(delay / 1000)  # 转换为秒
        
        raise Exception(f"获取token失败，已重试{self.retry_config['maxRetries']}次: {str(last_error)}")
    
    async def request_token(self) -> Dict[str, Any]:
        """
        发送token请求
        
        Returns:
            API响应字典
        """
        request_data = {
            'appId': self.app_id,
            'appSecret': self.app_secret,
            'permanentCode': self.permanent_code
        }
        
        url = f"{self.request_config['baseURL']}/cgi/corpAccessToken/get/V2"
        
        response = requests.post(
            url,
            json=request_data,
            headers=self.request_config['headers'],
            timeout=self.request_config['timeout']
        )
        
        response.raise_for_status()
        return response.json()
    
    def is_token_valid(self) -> bool:
        """
        检查token是否有效
        
        Returns:
            bool: token是否有效
        """
        if not self.token_cache['corpAccessToken'] or not self.token_cache['createdAt']:
            return False
        
        now = time.time()
        elapsed = now - self.token_cache['createdAt']
        remaining = self.token_cache['expiresIn'] - elapsed
        
        return remaining > 0
    
    def should_refresh_token(self) -> bool:
        """
        检查是否需要刷新token
        
        Returns:
            bool: 是否需要刷新
        """
        if not self.token_cache['createdAt'] or not self.token_cache['expiresIn']:
            return False
        
        now = time.time()
        elapsed = now - self.token_cache['createdAt']
        remaining = self.token_cache['expiresIn'] - elapsed
        
        # 在刷新窗口内且距离上次刷新超过一定时间
        time_since_last_refresh = (now - self.token_cache['lastRefreshTime']) if self.token_cache['lastRefreshTime'] else float('inf')
        
        return (remaining <= self.time_config['refreshWindowEnd'] and 
                remaining >= self.time_config['refreshWindowStart'] and
                time_since_last_refresh > 60)  # 至少间隔1分钟
    
    def update_token_cache(self, token_data: Dict[str, Any]):
        """
        更新token缓存
        
        Args:
            token_data: API返回的token数据
        """
        now = time.time()
        
        self.token_cache = {
            'corpAccessToken': token_data['corpAccessToken'],
            'corpId': token_data['corpId'],
            'expiresIn': int(token_data['expiresIn']),
            'createdAt': now,
            'lastRefreshTime': now
        }
        
        # 设置自动刷新定时器
        self.schedule_token_refresh()
    
    def schedule_token_refresh(self):
        """设置自动刷新定时器"""
        # 计算下次刷新时间
        if self.token_cache['expiresIn']:
            refresh_time = self.token_cache['createdAt'] + self.time_config['refreshWindowStart']
            now = time.time()
            
            if refresh_time > now:
                delay = refresh_time - now
                logger.info(f'[FxiaokeAuth] 设置自动刷新定时器，{delay}秒后刷新')
                # 这里可以使用asyncio.create_task来实现异步定时器
                # 为了简化，这里只是记录日志
    
    def get_current_token(self) -> Optional[str]:
        """
        获取当前token（不进行刷新）
        
        Returns:
            当前token字符串，如果无效则返回None
        """
        if self.is_token_valid():
            return self.token_cache['corpAccessToken']
        return None
    
    async def force_refresh_token(self) -> Dict[str, Any]:
        """
        强制刷新token
        
        Returns:
            新的token信息
        """
        logger.info('[FxiaokeAuth] 强制刷新token')
        
        # 清除缓存
        self.token_cache = {
            'corpAccessToken': None,
            'corpId': None,
            'expiresIn': None,
            'createdAt': None,
            'lastRefreshTime': None
        }
        
        # 重新获取token
        return await self.get_corp_access_token()
    
    def destroy(self):
        """清理资源"""
        logger.info('[FxiaokeAuth] 清理认证管理器资源')
        
        # 清除定时器
        if self.refresh_timer:
            # 这里应该取消定时器
            pass
        
        # 清除缓存
        self.token_cache = {
            'corpAccessToken': None,
            'corpId': None,
            'expiresIn': None,
            'createdAt': None,
            'lastRefreshTime': None
        }
    
    @staticmethod
    async def sleep(seconds: float):
        """
        异步睡眠
        
        Args:
            seconds: 睡眠秒数
        """
        import asyncio
        await asyncio.sleep(seconds)
    
    def set_retry_config(self, config: Dict[str, Any]):
        """
        设置重试配置
        
        Args:
            config: 重试配置字典
        """
        self.retry_config.update(config)
    
    def set_timeout(self, timeout: int):
        """
        设置请求超时时间
        
        Args:
            timeout: 超时时间（秒）
        """
        self.request_config['timeout'] = timeout 