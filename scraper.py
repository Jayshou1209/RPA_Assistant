"""
数据爬取模块 - 爬取司机资料、车型、开工时间段等信息
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import config
from api_client import APIClient

logger = logging.getLogger(__name__)


class DataScraper:
    """数据爬取器"""
    
    def __init__(self, api_client: APIClient):
        """
        初始化数据爬取器
        
        Args:
            api_client: API客户端实例
        """
        self.api = api_client
        self.data_dir = config.DATA_DIR
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"创建数据目录: {self.data_dir}")
    
    def get_drivers(self, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        获取司机列表
        
        Args:
            params: 查询参数，例如 {'status': 'active', 'page': 1}
            
        Returns:
            司机列表
        """
        try:
            logger.info("开始获取司机数据...")
            response = self.api.get(config.ENDPOINTS['drivers'], params=params)
            
            drivers = response.get('data', [])
            logger.info(f"成功获取 {len(drivers)} 位司机的数据")
            
            return drivers
        except Exception as e:
            logger.error(f"获取司机数据失败: {e}")
            return []
    
    def get_driver_details(self, driver_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个司机的详细信息
        
        Args:
            driver_id: 司机ID
            
        Returns:
            司机详细信息
        """
        try:
            endpoint = f"{config.ENDPOINTS['drivers']}/{driver_id}"
            response = self.api.get(endpoint)
            logger.info(f"获取司机 {driver_id} 的详细信息成功")
            return response.get('data', {})
        except Exception as e:
            logger.error(f"获取司机 {driver_id} 详细信息失败: {e}")
            return None
    
    def get_vehicles(self, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        获取车辆列表
        
        Args:
            params: 查询参数
            
        Returns:
            车辆列表
        """
        try:
            logger.info("开始获取车辆数据...")
            response = self.api.get(config.ENDPOINTS['vehicles'], params=params)
            
            vehicles = response.get('data', [])
            logger.info(f"成功获取 {len(vehicles)} 辆车的数据")
            
            return vehicles
        except Exception as e:
            logger.error(f"获取车辆数据失败: {e}")
            return []
    
    def get_schedules(self, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        获取排班/开工时间段信息
        
        Args:
            params: 查询参数，例如 {'date': '2025-11-20', 'driver_id': 123}
            
        Returns:
            排班列表
        """
        try:
            logger.info("开始获取排班数据...")
            response = self.api.get(config.ENDPOINTS['schedules'], params=params)
            
            schedules = response.get('data', [])
            logger.info(f"成功获取 {len(schedules)} 条排班数据")
            
            return schedules
        except Exception as e:
            logger.error(f"获取排班数据失败: {e}")
            return []
    
    def scrape_all_data(self) -> Dict[str, Any]:
        """
        爬取所有数据
        
        Returns:
            包含所有数据的字典
        """
        logger.info("=" * 50)
        logger.info("开始爬取所有数据")
        logger.info("=" * 50)
        
        all_data = {
            'timestamp': datetime.now().isoformat(),
            'drivers': [],
            'vehicles': [],
            'schedules': []
        }
        
        # 获取司机数据
        all_data['drivers'] = self.get_drivers()
        
        # 获取车辆数据
        all_data['vehicles'] = self.get_vehicles()
        
        # 获取排班数据
        all_data['schedules'] = self.get_schedules()
        
        logger.info("数据爬取完成")
        return all_data
    
    def save_data(self, data: Dict[str, Any], filename: str = None):
        """
        保存数据到JSON文件
        
        Args:
            data: 要保存的数据
            filename: 文件名，默认使用配置中的文件名
        """
        if filename is None:
            filename = config.DRIVER_DATA_FILE
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
    
    def load_data(self, filename: str = None) -> Optional[Dict[str, Any]]:
        """
        从JSON文件加载数据
        
        Args:
            filename: 文件名
            
        Returns:
            加载的数据
        """
        if filename is None:
            filename = config.DRIVER_DATA_FILE
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"数据已从 {filepath} 加载")
            return data
        except FileNotFoundError:
            logger.warning(f"文件不存在: {filepath}")
            return None
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return None
    
    def get_driver_summary(self, drivers: List[Dict[str, Any]]) -> str:
        """
        生成司机数据摘要
        
        Args:
            drivers: 司机列表
            
        Returns:
            摘要字符串
        """
        if not drivers:
            return "暂无司机数据"
        
        summary = f"\n司机数据摘要 (共 {len(drivers)} 位):\n"
        summary += "-" * 60 + "\n"
        
        for i, driver in enumerate(drivers[:10], 1):  # 只显示前10位
            name = driver.get('name', '未知')
            driver_id = driver.get('id', 'N/A')
            status = driver.get('status', '未知')
            vehicle = driver.get('vehicle_type', '未分配')
            
            summary += f"{i}. ID: {driver_id} | 姓名: {name} | 状态: {status} | 车型: {vehicle}\n"
        
        if len(drivers) > 10:
            summary += f"... 还有 {len(drivers) - 10} 位司机\n"
        
        return summary
