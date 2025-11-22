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
        self.token = token or config.BEARER_TOKEN
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
        self.token = new_token
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
    
    def verify_connection(self) -> bool:
        """
        验证连接和Token是否有效
        
        Returns:
            连接是否成功
        """
        try:
            # 使用drivers端点测试连接（获取1条数据）
            response = self.get('/drivers', params={'page': 1, 'per_page': 1})
            if 'drivers' in response:
                logger.info("连接验证成功")
                return True
            else:
                logger.error(f"连接验证失败: 响应格式不正确")
                return False
        except Exception as e:
            logger.error(f"连接验证失败: {e}")
            return False
