"""
真实API爬虫 - 使用正确的api-admin.myle.tech端点
支持分页获取所有数据，并导出到Excel
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import time
import logging
import config

logger = logging.getLogger(__name__)


class RealAPIScraper:
    """真实API爬虫 - 支持分页获取完整数据"""
    
    def __init__(self, api_client=None):
        """初始化"""
        if api_client:
            self.api = api_client
        else:
            from api_client import APIClient
            self.api = APIClient()
        
        self.data_dir = config.DATA_DIR
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_all_drivers(self, per_page: int = 100, progress_callback=None) -> List[Dict[str, Any]]:
        """
        获取所有司机数据（支持分页）
        
        Args:
            per_page: 每页数量（最大100）
            progress_callback: 进度回调函数
            
        Returns:
            完整的司机列表
        """
        logger.info("开始获取所有司机数据（分页模式）...")
        
        all_drivers = []
        page = 1
        
        while True:
            try:
                params = {
                    'page': page,
                    'per_page': per_page,
                    'search': '',
                    'sort_by': 'drivers.id',
                    'sort_by_type': 'true'
                }
                
                logger.info(f"正在获取第 {page} 页数据...")
                response = self.api.get('/fleet/drivers', params=params)
                
                # 检查响应格式 - API返回格式: {"drivers": {"data": [...], "current_page": 1, ...}}
                if isinstance(response, dict):
                    # 处理Myle API的特殊格式
                    drivers_data = response.get('drivers', response.get('data', {}))
                    
                    if isinstance(drivers_data, dict):
                        drivers = drivers_data.get('data', [])
                        total = drivers_data.get('total', 0)
                        current_page = drivers_data.get('current_page', page)
                        last_page = drivers_data.get('last_page')
                        next_page_url = drivers_data.get('next_page_url')
                    else:
                        drivers = drivers_data if isinstance(drivers_data, list) else []
                        total = len(all_drivers) + len(drivers)
                        last_page = None
                        next_page_url = None
                    
                    if not drivers:
                        logger.info(f"第 {page} 页没有数据，停止获取")
                        break
                    
                    all_drivers.extend(drivers)
                    logger.info(f"✓ 第 {page} 页: 获取 {len(drivers)} 条数据 (累计: {len(all_drivers)})")
                    
                    if progress_callback:
                        progress_callback(len(all_drivers), total if total > 0 else len(all_drivers), f"第{page}页")
                    
                    # 检查是否还有下一页（优先使用next_page_url判断）
                    if isinstance(drivers_data, dict):
                        # 如果有next_page_url字段且为None，说明没有下一页了
                        if 'next_page_url' in drivers_data and next_page_url is None:
                            logger.info(f"没有更多数据（next_page_url为空）")
                            break
                        # 如果有last_page字段，也用来判断
                        if last_page is not None and page >= last_page:
                            logger.info(f"已到达最后一页 ({last_page})")
                            break
                    
                    # 如果返回的数据少于per_page，说明是最后一页
                    if len(drivers) < per_page:
                        logger.info(f"返回数据少于 {per_page}，判断为最后一页")
                        break
                    
                    page += 1
                    time.sleep(0.2)  # 避免请求过快
                    
                else:
                    logger.error(f"响应格式错误: {type(response)}")
                    break
                    
            except Exception as e:
                logger.error(f"获取第 {page} 页数据失败: {e}")
                break
        
        logger.info(f"✓ 完成！共获取 {len(all_drivers)} 位司机数据")
        return all_drivers
    
    def get_all_routes(self, date: str = None, per_page: int = 100, 
                       progress_callback=None) -> List[Dict[str, Any]]:
        """
        获取所有路线/订单数据（支持分页）
        
        Args:
            date: 日期，格式 YYYY-MM-DD（默认今天）
            per_page: 每页数量
            progress_callback: 进度回调
            
        Returns:
            完整的路线列表
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"开始获取 {date} 的路线数据（分页模式）...")
        
        all_routes = []
        page = 1
        
        while True:
            try:
                params = {
                    'page': page,
                    'per_page': per_page,
                    'statuses': '',
                    'route_brokers': '',
                    'company_ids': '',
                    'sort_by': 'routes.id',
                    'sort_by_type': 'true',
                    'fleet_ids': '',
                    'from_datetime': f'{date}T00:00',
                    'to_datetime': f'{date}T23:59'
                }
                
                logger.info(f"正在获取第 {page} 页路线数据...")
                response = self.api.get('/fleet/routes', params=params)
                
                # API返回格式: {"routes": {"data": [...], ...}}
                if isinstance(response, dict):
                    routes_data = response.get('routes', response.get('data', {}))
                    
                    if isinstance(routes_data, dict):
                        routes = routes_data.get('data', [])
                        total = routes_data.get('total', 0)
                        last_page = routes_data.get('last_page')
                        next_page_url = routes_data.get('next_page_url')
                    else:
                        routes = routes_data if isinstance(routes_data, list) else []
                        total = len(all_routes) + len(routes)
                        last_page = None
                        next_page_url = None
                    
                    if not routes:
                        break
                    
                    all_routes.extend(routes)
                    logger.info(f"✓ 第 {page} 页: 获取 {len(routes)} 条路线 (累计: {len(all_routes)})")
                    
                    if progress_callback:
                        progress_callback(len(all_routes), total if total > 0 else len(all_routes), f"第{page}页")
                    
                    # 检查是否还有下一页（优先使用next_page_url判断）
                    if isinstance(routes_data, dict):
                        if 'next_page_url' in routes_data and next_page_url is None:
                            logger.info(f"没有更多路线数据")
                            break
                        if last_page is not None and page >= last_page:
                            break
                    
                    if len(routes) < per_page:
                        break
                    
                    page += 1
                    time.sleep(0.2)
                    
                else:
                    break
                    
            except Exception as e:
                logger.error(f"获取第 {page} 页路线数据失败: {e}")
                break
        
        logger.info(f"✓ 完成！共获取 {len(all_routes)} 条路线数据")
        return all_routes
    
    def get_all_rides(self, date: str = None, per_page: int = 500, 
                      statuses: str = '', progress_callback=None) -> List[Dict[str, Any]]:
        """
        获取所有订单数据（支持分页）
        
        Args:
            date: 日期，格式 YYYY-MM-DD（默认今天）
            per_page: 每页数量（最大500）
            statuses: 订单状态过滤，多个用逗号分隔，空字符串表示所有状态
            progress_callback: 进度回调
            
        Returns:
            完整的订单列表
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"开始获取 {date} 的订单数据（分页模式）...")
        
        all_rides = []
        page = 1
        
        while True:
            try:
                params = {
                    'page': page,
                    'per_page': per_page,
                    'search': '',
                    'sort_by': 'rides.pickup_at',
                    'sort_by_type': 'false',
                    'statuses': statuses,
                    'all_rides': 'true',
                    'from_datetime': f'{date}T00:00',
                    'to_datetime': f'{date}T23:59',
                    'filters': ''
                }
                
                logger.info(f"正在获取第 {page} 页订单数据...")
                response = self.api.get('/fleet/rides', params=params)
                
                # API返回格式: {"rides": {"data": [...], ...}}
                if isinstance(response, dict):
                    rides_data = response.get('rides', response.get('data', {}))
                    
                    if isinstance(rides_data, dict):
                        rides = rides_data.get('data', [])
                        total = rides_data.get('total', 0)
                        last_page = rides_data.get('last_page')
                        next_page_url = rides_data.get('next_page_url')
                    else:
                        rides = rides_data if isinstance(rides_data, list) else []
                        total = len(all_rides) + len(rides)
                        last_page = None
                        next_page_url = None
                    
                    if not rides:
                        break
                    
                    all_rides.extend(rides)
                    logger.info(f"✓ 第 {page} 页: 获取 {len(rides)} 条订单 (累计: {len(all_rides)})")
                    
                    if progress_callback:
                        progress_callback(len(all_rides), total if total > 0 else len(all_rides), f"第{page}页")
                    
                    # 检查是否还有下一页（优先使用next_page_url判断）
                    if isinstance(rides_data, dict):
                        if 'next_page_url' in rides_data and next_page_url is None:
                            logger.info(f"没有更多订单数据")
                            break
                        if last_page is not None and page >= last_page:
                            break
                    
                    if len(rides) < per_page:
                        break
                    
                    page += 1
                    time.sleep(0.2)
                    
                else:
                    break
                    
            except Exception as e:
                logger.error(f"获取第 {page} 页订单失败: {e}")
                break
        
        logger.info(f"✓ 完成！共获取 {len(all_rides)} 条订单数据")
        return all_rides
    
    def get_driver_detail(self, driver_id: int) -> Dict[str, Any]:
        """
        获取单个司机的详细信息
        
        Args:
            driver_id: 司机ID
            
        Returns:
            司机详细信息
        """
        try:
            endpoint = f"/fleet/drivers/{driver_id}"
            response = self.api.get(endpoint)
            return response.get('data', response)
        except Exception as e:
            logger.error(f"获取司机 {driver_id} 详细信息失败: {e}")
            return None
    
    def get_vehicle_detail(self, vehicle_id: int) -> Dict[str, Any]:
        """
        获取单个车辆的详细信息
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            车辆详细信息
        """
        try:
            endpoint = f"/fleet/cars/{vehicle_id}"
            response = self.api.get(endpoint)
            # API返回格式: {"car": {...}}
            return response.get('car', response.get('data', response))
        except Exception as e:
            logger.error(f"获取车辆 {vehicle_id} 详细信息失败: {e}")
            return None
    
    def get_all_drivers_with_full_details(self, per_page: int = 100, progress_callback=None) -> List[Dict[str, Any]]:
        """
        获取所有司机数据及其完整的详细信息（包括证件、车辆等）
        
        Args:
            per_page: 每页数量
            progress_callback: 进度回调函数
            
        Returns:
            包含完整详细信息的司机列表
        """
        logger.info("开始爬取司机完整详细信息...")
        
        # 第一步：获取所有司机基本信息
        all_drivers = self.get_all_drivers(per_page=per_page, progress_callback=progress_callback)
        logger.info(f"✓ 获取到 {len(all_drivers)} 位司机的基本信息")
        
        if not all_drivers:
            return []
        
        # 第二步：逐个获取司机详细信息
        detailed_drivers = []
        total = len(all_drivers)
        
        logger.info(f"开始获取每位司机的详细信息（包括证件、车辆等）...")
        
        for idx, driver in enumerate(all_drivers, 1):
            try:
                driver_id = driver.get('id')
                if not driver_id:
                    detailed_drivers.append(driver)
                    continue
                
                # 获取司机详细信息（包含证件信息）
                driver_detail = self.get_driver_detail(driver_id)
                
                if driver_detail:
                    # 合并基本信息和详细信息
                    merged_driver = {**driver, **driver_detail}
                    
                    # 获取车辆详细信息 - API返回的是'cars'而不是'vehicles'
                    cars = merged_driver.get('cars', []) or merged_driver.get('vehicles', [])
                    if cars and isinstance(cars, list) and len(cars) > 0:
                        car = cars[0]
                        vehicle_id = car.get('id') if isinstance(car, dict) else None
                        
                        if vehicle_id:
                            logger.info(f"  获取车辆 {vehicle_id} 的详细信息...")
                            vehicle_detail = self.get_vehicle_detail(vehicle_id)
                            if vehicle_detail:
                                # 将车辆详细信息添加到司机信息中
                                merged_driver['vehicle_detail'] = vehicle_detail
                                logger.info(f"  ✓ 车辆信息已获取")
                            else:
                                logger.warning(f"  ✗ 车辆 {vehicle_id} 详情获取失败")
                    else:
                        logger.warning(f"  司机 {driver_id} 没有关联的车辆")
                    
                    detailed_drivers.append(merged_driver)
                else:
                    detailed_drivers.append(driver)
                
                # 每处理10条数据记录一次日志
                if idx % 10 == 0 or idx == total:
                    logger.info(f"进度: {idx}/{total} ({idx*100//total}%)")
                    if progress_callback:
                        progress_callback(idx, total, f"获取详情 {idx}/{total}")
                
                # 避免请求过快
                time.sleep(0.3)
                
            except Exception as e:
                logger.error(f"处理司机 {driver.get('id')} 时出错: {e}")
                detailed_drivers.append(driver)
        
        logger.info(f"✓ 完成！成功获取 {len(detailed_drivers)} 位司机的完整详细信息")
        return detailed_drivers
    
    def scrape_all_data(self, get_driver_details: bool = False, date: str = None,
                        progress_callback=None) -> Dict[str, Any]:
        """
        爬取所有数据
        
        Args:
            get_driver_details: 是否获取每个司机的详细信息（会很慢）
            date: 路线日期
            progress_callback: 进度回调
            
        Returns:
            包含所有数据的字典
        """
        logger.info("=" * 70)
        logger.info("开始爬取所有数据")
        logger.info("=" * 70)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'drivers': [],
            'routes': [],
            'metadata': {}
        }
        
        # 1. 爬取司机数据
        if progress_callback:
            progress_callback(0, 2, "正在爬取司机数据...")
        
        result['drivers'] = self.get_all_drivers(progress_callback=progress_callback)
        result['metadata']['total_drivers'] = len(result['drivers'])
        
        # 2. 如果需要详细信息，逐个获取
        if get_driver_details and result['drivers']:
            logger.info("\n开始获取每个司机的详细信息...")
            detailed_drivers = []
            
            for i, driver in enumerate(result['drivers'], 1):
                driver_id = driver.get('id')
                if driver_id:
                    detail = self.get_driver_detail(driver_id)
                    if detail:
                        combined = {**driver, **detail}
                        detailed_drivers.append(combined)
                    else:
                        detailed_drivers.append(driver)
                    
                    if i % 10 == 0:
                        logger.info(f"已获取 {i}/{len(result['drivers'])} 位司机的详细信息")
                    
                    time.sleep(0.1)
            
            result['drivers'] = detailed_drivers
        
        # 3. 爬取路线数据
        if progress_callback:
            progress_callback(1, 2, "正在爬取路线数据...")
        
        result['routes'] = self.get_all_routes(date=date, progress_callback=progress_callback)
        result['metadata']['total_routes'] = len(result['routes'])
        result['metadata']['route_date'] = date or datetime.now().strftime('%Y-%m-%d')
        
        logger.info("=" * 70)
        logger.info("数据爬取完成！")
        logger.info(f"  司机: {result['metadata']['total_drivers']} 位")
        logger.info(f"  路线: {result['metadata']['total_routes']} 条")
        logger.info("=" * 70)
        
        return result
    
    def export_to_excel(self, data: Dict[str, Any], filename: str = None) -> str:
        """导出数据到Excel"""
        try:
            import pandas as pd
            
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"myle_complete_data_{timestamp}.xlsx"
            
            filepath = os.path.join(self.data_dir, filename)
            
            logger.info(f"开始导出数据到Excel: {filepath}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 导出司机数据
                if data.get('drivers'):
                    df = pd.DataFrame(data['drivers'])
                    df.to_excel(writer, sheet_name='司机数据', index=False)
                    logger.info(f"  ✓ 司机数据: {len(data['drivers'])} 行")
                
                # 导出路线数据
                if data.get('routes'):
                    df = pd.DataFrame(data['routes'])
                    df.to_excel(writer, sheet_name='路线数据', index=False)
                    logger.info(f"  ✓ 路线数据: {len(data['routes'])} 行")
                
                # 导出元数据
                if data.get('metadata'):
                    df = pd.DataFrame([data['metadata']])
                    df.to_excel(writer, sheet_name='统计信息', index=False)
            
            logger.info(f"✓ 导出完成: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"导出Excel失败: {e}")
            raise
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """保存数据为JSON"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"myle_complete_data_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ 数据已保存到JSON: {filepath}")
        return filepath


# 测试
if __name__ == "__main__":
    print("=" * 70)
    print("真实API爬虫测试")
    print("=" * 70)
    
    scraper = RealAPIScraper()
    
    # 测试获取司机数据（仅前2页）
    print("\n测试: 获取前2页司机数据")
    print("-" * 70)
    
    drivers = []
    for page in [1, 2]:
        params = {
            'page': page,
            'per_page': 10,
            'search': '',
            'sort_by': 'drivers.id',
            'sort_by_type': 'true'
        }
        response = scraper.api.get('/fleet/drivers', params=params)
        print(f"\n第 {page} 页响应:")
        print(f"响应类型: {type(response)}")
        
        if isinstance(response, dict):
            data = response.get('data', {})
            print(f"Data类型: {type(data)}")
            
            if isinstance(data, dict):
                print(f"分页信息:")
                print(f"  当前页: {data.get('current_page')}")
                print(f"  总页数: {data.get('last_page')}")
                print(f"  总数: {data.get('total')}")
                print(f"  每页: {data.get('per_page')}")
                
                page_drivers = data.get('data', [])
                print(f"  本页数据: {len(page_drivers)} 条")
                
                if page_drivers:
                    print(f"\n第一条司机数据:")
                    print(json.dumps(page_drivers[0], ensure_ascii=False, indent=2))
                
                drivers.extend(page_drivers)
    
    print(f"\n总共获取: {len(drivers)} 条司机数据")
