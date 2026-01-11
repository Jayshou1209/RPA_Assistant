"""
API客户端 - 处理所有与调度系统的API交互
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class APIClient:
    """调度系统API客户端"""
    
    def __init__(self, token: str = None):
        """
        初始化API客户端
        
        Args:
            token: Bearer token，如果不提供则使用config中的token
        """
        self.base_url = config.API_BASE_URL
        self.token = (token or config.BEARER_TOKEN).strip()
        self.session = requests.Session()
        self._setup_headers()
        logger.info("API客户端初始化成功")
    
    def _setup_headers(self):
        """设置请求头"""
        self.session.headers.update({
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'RPA-Automation-Script/1.0'
        })
    
    def update_token(self, new_token: str):
        """
        更新Token
        
        Args:
            new_token: 新的Bearer token
        """
        self.token = new_token.strip()
        self._setup_headers()
        logger.info("Token已更新")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        发起HTTP请求
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            endpoint: API端点
            params: URL参数
            data: 表单数据
            json_data: JSON数据
            
        Returns:
            响应数据字典
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                timeout=config.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            
            logger.info(f"{method} {endpoint} - 状态码: {response.status_code}")
            
            try:
                return response.json()
            except ValueError:
                return {"success": True, "data": response.text}
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {e} - {response.text if 'response' in locals() else ''}")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, json_data: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        return self._make_request('POST', endpoint, json_data=json_data, data=data)
    
    def put(self, endpoint: str, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT请求"""
        return self._make_request('PUT', endpoint, json_data=json_data)
    
    def delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """DELETE请求"""
        return self._make_request('DELETE', endpoint, params=params)
    
    def verify_connection(self) -> tuple[bool, str]:
        """
        验证连接和Token是否有效
        
        Returns:
            (连接是否成功, 消息内容)
        """
        try:
            # 优先使用fleet/account端点测试连接（适用于fleet权限的token）
            response = self.get('/fleet/account')
            if 'user' in response and response.get('status_code') == 200:
                logger.info("连接验证成功 (fleet/account)")
                user_info = response.get('user', {})
                # 尝试多种方式获取用户名
                username = user_info.get('name') or \
                          f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or \
                          user_info.get('email', 'Unknown')
                return True, f"连接成功！用户: {username}"
            
            # 如果fleet端点失败，尝试drivers端点（适用于admin权限的token）
            response = self.get('/drivers', params={'page': 1, 'per_page': 1})
            if 'drivers' in response:
                logger.info("连接验证成功 (drivers)")
                return True, "连接成功！"
            else:
                error_msg = f"响应格式不正确"
                logger.error(f"连接验证失败: {error_msg}")
                return False, error_msg
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                if status_code == 403:
                    error_msg = "Token无效或已过期\n\n请点击'更新Token'按钮更新Token"
                    logger.error(f"Token验证失败 (403)")
                    return False, error_msg
                elif status_code == 401:
                    error_msg = "未授权，Token可能格式错误\n\n请确保Token以'Bearer '开头"
                    logger.error(f"连接验证失败 (401)")
                    return False, error_msg
                else:
                    error_msg = f"HTTP错误 {status_code}"
                    logger.error(f"连接验证失败: {error_msg}")
                    return False, error_msg
            else:
                error_msg = f"HTTP请求错误"
                logger.error(f"连接验证失败: {error_msg}")
                return False, error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"网络连接失败\n\n请检查网络连接"
            logger.error(f"连接验证失败: ConnectionError")
            return False, error_msg
        except requests.exceptions.Timeout as e:
            error_msg = f"请求超时\n\n请稍后重试"
            logger.error(f"连接验证失败: Timeout")
            return False, error_msg
        except Exception as e:
            error_msg = f"验证失败: {type(e).__name__}"
            logger.error(f"连接验证失败: {error_msg} - {str(e)}")
            return False, error_msg
