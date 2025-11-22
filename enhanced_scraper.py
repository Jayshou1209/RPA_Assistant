"""
增强版数据爬取器 - 爬取司机详细资料
支持获取每个司机的完整信息并导出Excel
"""

import requests
import json
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import config

logger = logging.getLogger(__name__)


class EnhancedScraper:
    """增强版数据爬取器 - 获取详细的司机、车辆、路线数据"""
    
    def __init__(self, api_client):
        """初始化"""
        self.api = api_client
        self.base_url = config.API_BASE_URL
        self.data_dir = config.DATA_DIR
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_driver_detail(self, driver_id: int) -> Optional[Dict[str, Any]]:
        """
        获取单个司机的详细信息
        
        Args:
            driver_id: 司机ID
            
        Returns:
            司机详细信息字典
        """
        try:
            endpoint = f"/drivers/{driver_id}"
            logger.info(f"获取司机 {driver_id} 的详细信息...")
            response = self.api.get(endpoint)
            
            if response.get('success') or 'data' in response:
                return response.get('data', response)
            else:
                logger.warning(f"获取司机 {driver_id} 详细信息失败")
                return None
                
        except Exception as e:
            logger.error(f"获取司机 {driver_id} 详细信息出错: {e}")
            return None
    
    def get_all_drivers_with_details(self, limit: int = None, progress_callback=None) -> List[Dict[str, Any]]:
        """
        获取所有司机列表及其详细信息
        
        Args:
            limit: 限制获取数量（用于测试）
            progress_callback: 进度回调函数
            
        Returns:
            包含详细信息的司机列表
        """
        logger.info("开始获取所有司机列表...")
        
        # 1. 获取司机列表
        try:
            response = self.api.get("/drivers")
            drivers_list = response.get('data', [])
            logger.info(f"获取到 {len(drivers_list)} 位司机")
            
            if limit:
                drivers_list = drivers_list[:limit]
                logger.info(f"限制获取数量为 {limit}")
            
        except Exception as e:
            logger.error(f"获取司机列表失败: {e}")
            return []
        
        # 2. 获取每个司机的详细信息
        detailed_drivers = []
        total = len(drivers_list)
        
        for index, driver in enumerate(drivers_list, 1):
            driver_id = driver.get('id')
            driver_name = driver.get('name', '未知')
            
            if progress_callback:
                progress_callback(index, total, driver_name)
            
            logger.info(f"[{index}/{total}] 获取司机 {driver_name} (ID: {driver_id}) 的详细信息...")
            
            # 获取详细信息
            detail = self.get_driver_detail(driver_id)
            
            if detail:
                # 合并基本信息和详细信息
                combined = {**driver, **detail}
                detailed_drivers.append(combined)
            else:
                # 如果获取详细信息失败，至少保留基本信息
                detailed_drivers.append(driver)
            
            # 避免请求过快，添加小延迟
            time.sleep(0.1)
        
        logger.info(f"完成！共获取 {len(detailed_drivers)} 位司机的详细信息")
        return detailed_drivers
    
    def get_car_detail(self, car_id: int) -> Optional[Dict[str, Any]]:
        """获取单个车辆的详细信息"""
        try:
            endpoint = f"/vehicles/{car_id}"
            logger.info(f"获取车辆 {car_id} 的详细信息...")
            response = self.api.get(endpoint)
            return response.get('data', response)
        except Exception as e:
            logger.error(f"获取车辆 {car_id} 详细信息出错: {e}")
            return None
    
    def get_all_cars_with_details(self, limit: int = None, progress_callback=None) -> List[Dict[str, Any]]:
        """获取所有车辆及详细信息"""
        logger.info("开始获取所有车辆列表...")
        
        try:
            response = self.api.get("/vehicles")
            cars_list = response.get('data', [])
            logger.info(f"获取到 {len(cars_list)} 辆车")
            
            if limit:
                cars_list = cars_list[:limit]
            
        except Exception as e:
            logger.error(f"获取车辆列表失败: {e}")
            return []
        
        detailed_cars = []
        total = len(cars_list)
        
        for index, car in enumerate(cars_list, 1):
            car_id = car.get('id')
            
            if progress_callback:
                progress_callback(index, total, f"车辆 {car_id}")
            
            detail = self.get_car_detail(car_id)
            
            if detail:
                combined = {**car, **detail}
                detailed_cars.append(combined)
            else:
                detailed_cars.append(car)
            
            time.sleep(0.1)
        
        logger.info(f"完成！共获取 {len(detailed_cars)} 辆车的详细信息")
        return detailed_cars
    
    def get_all_routes(self, date: str = None) -> List[Dict[str, Any]]:
        """
        获取所有路线（订单）
        
        Args:
            date: 日期，格式 YYYY-MM-DD
        """
        logger.info("开始获取路线数据...")
        
        try:
            params = {}
            if date:
                params['date'] = date
            
            # 尝试不同的端点
            endpoints = ['/routes', '/bookings', '/trips']
            
            for endpoint in endpoints:
                try:
                    response = self.api.get(endpoint, params=params)
                    routes = response.get('data', [])
                    if routes:
                        logger.info(f"从 {endpoint} 获取到 {len(routes)} 条路线")
                        return routes
                except:
                    continue
            
            logger.warning("无法获取路线数据")
            return []
            
        except Exception as e:
            logger.error(f"获取路线失败: {e}")
            return []
    
    def export_to_excel(self, data_dict: Dict[str, List[Dict]], filename: str = None):
        """
        导出数据到Excel文件
        
        Args:
            data_dict: 数据字典，格式: {'sheet_name': [data_list]}
            filename: 文件名
        """
        try:
            import pandas as pd
            
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"myle_data_export_{timestamp}.xlsx"
            
            filepath = os.path.join(self.data_dir, filename)
            
            logger.info(f"开始导出数据到Excel: {filepath}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, data in data_dict.items():
                    if data:
                        df = pd.DataFrame(data)
                        
                        # 清理列名（移除特殊字符）
                        df.columns = [str(col).replace('/', '_').replace('\\', '_') for col in df.columns]
                        
                        # 截断过长的sheet名称
                        safe_sheet_name = sheet_name[:31]
                        
                        df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                        logger.info(f"  ✓ 工作表 '{safe_sheet_name}': {len(data)} 行数据")
            
            logger.info(f"✓ 导出完成: {filepath}")
            return filepath
            
        except ImportError:
            logger.error("缺少pandas或openpyxl库，无法导出Excel")
            raise Exception("请安装: pip install pandas openpyxl")
        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            raise
    
    def scrape_all_detailed_data(self, driver_limit: int = None, car_limit: int = None, 
                                  progress_callback=None) -> Dict[str, Any]:
        """
        爬取所有详细数据（司机、车辆、路线）
        
        Args:
            driver_limit: 司机数量限制（用于测试）
            car_limit: 车辆数量限制（用于测试）
            progress_callback: 进度回调
            
        Returns:
            包含所有详细数据的字典
        """
        logger.info("=" * 60)
        logger.info("开始爬取所有详细数据")
        logger.info("=" * 60)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'drivers': [],
            'cars': [],
            'routes': []
        }
        
        # 1. 爬取司机详细数据
        if progress_callback:
            progress_callback(0, 3, "爬取司机数据...")
        
        result['drivers'] = self.get_all_drivers_with_details(
            limit=driver_limit, 
            progress_callback=progress_callback
        )
        
        # 2. 爬取车辆详细数据
        if progress_callback:
            progress_callback(1, 3, "爬取车辆数据...")
        
        result['cars'] = self.get_all_cars_with_details(
            limit=car_limit,
            progress_callback=progress_callback
        )
        
        # 3. 爬取路线数据
        if progress_callback:
            progress_callback(2, 3, "爬取路线数据...")
        
        result['routes'] = self.get_all_routes(
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        logger.info("=" * 60)
        logger.info("数据爬取完成")
        logger.info(f"  司机: {len(result['drivers'])} 位")
        logger.info(f"  车辆: {len(result['cars'])} 辆")
        logger.info(f"  路线: {len(result['routes'])} 条")
        logger.info("=" * 60)
        
        return result
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None):
        """保存数据为JSON"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"myle_data_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ 数据已保存到JSON: {filepath}")
        return filepath


# 命令行测试
if __name__ == "__main__":
    from api_client import APIClient
    
    print("=" * 60)
    print("增强版数据爬取器测试")
    print("=" * 60)
    
    # 初始化
    client = APIClient()
    scraper = EnhancedScraper(client)
    
    # 测试获取前5位司机的详细信息
    print("\n测试: 获取前5位司机的详细信息")
    drivers = scraper.get_all_drivers_with_details(limit=5)
    
    print(f"\n获取到 {len(drivers)} 位司机")
    if drivers:
        print("\n第一位司机的详细信息:")
        print(json.dumps(drivers[0], ensure_ascii=False, indent=2))
    
    # 测试导出Excel
    print("\n测试: 导出到Excel")
    data_dict = {
        '司机详细信息': drivers
    }
    
    try:
        filepath = scraper.export_to_excel(data_dict, 'test_export.xlsx')
        print(f"✓ 导出成功: {filepath}")
    except Exception as e:
        print(f"✗ 导出失败: {e}")
