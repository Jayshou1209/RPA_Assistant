"""
调度模块 - 实现派工、退工、订单转派功能
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import config
from api_client import APIClient

logger = logging.getLogger(__name__)


class Dispatcher:
    """调度管理器"""
    
    def __init__(self, api_client: APIClient):
        """
        初始化调度管理器
        
        Args:
            api_client: API客户端实例
        """
        self.api = api_client
    
    def assign_driver(self, ride_id: int, driver_id: int) -> Dict[str, Any]:
        """
        派工 (Assign) - 分配司机给订单
        
        Args:
            ride_id: 订单ID
            driver_id: 司机ID
            
        Returns:
            派工结果
        """
        try:
            logger.info(f"派工 (Assign): 订单 {ride_id} -> 司机 {driver_id}")
            
            # 调用assign API
            data = {
                'driver_id': driver_id
            }
            
            response = self.api.post(f'/rides/{ride_id}/assign', json_data=data)
            logger.info(f"派工成功: {response}")
            return response
            
        except Exception as e:
            logger.error(f"派工失败: {e}")
            raise
    
    # 保留旧的dispatch_order方法作为别名
    def dispatch_order(
        self,
        driver_id: int,
        order_id: int,
        date: str = None,
        time_slot: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """兼容旧接口"""
        return self.assign_driver(order_id, driver_id)
    
    def cancel_ride(self, ride_id: int, reason: str = "driver cancel") -> Dict[str, Any]:
        """
        退工 (Revive) - 取消司机分配，默认原因为driver cancel
        
        根据Myle系统Network面板，正确的API格式是:
        POST /rides/{id}
        Body: {"status": "revive", "reason": "..."}
        
        Args:
            ride_id: 订单ID
            reason: 取消原因，默认为"driver cancel"
            
        Returns:
            退工结果
        """
        try:
            logger.info(f"退工 (Revive): 订单 {ride_id}, 原因: {reason}")
            
            # 必须发送status字段！
            data = {
                'status': 'revive',
                'reason': reason
            }
            
            response = self.api.post(f'/rides/{ride_id}', json_data=data)
            logger.info(f"退工成功: {response}")
            return response
            
        except Exception as e:
            logger.error(f"退工失败: {e}")
            raise
    
    # 保留旧的withdraw_order方法作为别名
    def withdraw_order(
        self,
        order_id: int,
        driver_id: Optional[int] = None,
        reason: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """兼容旧接口"""
        return self.cancel_ride(order_id, reason or "driver cancel")
    
    def transfer_driver(self, ride_id: int, new_driver_id: int) -> Dict[str, Any]:
        """
        转派 (Switch) - 更换订单的司机
        
        根据Myle系统Network面板，正确的API格式是:
        POST /rides/{id}
        Body: {"entity_id": driver_id, "entity_type": "driver", "status": "switch_driver"}
        
        Args:
            ride_id: 订单ID
            new_driver_id: 新司机ID
            
        Returns:
            转派结果
        """
        try:
            logger.info(f"转派 (Switch): 订单 {ride_id} -> 新司机 {new_driver_id}")
            
            # 使用正确的字段格式
            data = {
                'entity_id': new_driver_id,
                'entity_type': 'driver',
                'status': 'switch_driver'
            }
            
            response = self.api.post(f'/rides/{ride_id}', json_data=data)
            logger.info(f"转派成功: {response}")
            return response
            
        except Exception as e:
            logger.error(f"转派失败: {e}")
            raise
    
    # 保留旧的transfer_order方法作为别名
    def transfer_order(
        self,
        order_id: int,
        from_driver_id: int,
        to_driver_id: int,
        date: str = None,
        reason: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """兼容旧接口"""
        return self.transfer_driver(order_id, to_driver_id)
    
    def batch_dispatch(
        self,
        dispatch_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        批量派工
        
        Args:
            dispatch_list: 派工列表，每项包含 driver_id, order_id 等信息
            
        Returns:
            批量派工结果列表
        """
        results = []
        
        logger.info(f"开始批量派工 - 共 {len(dispatch_list)} 个订单")
        
        for i, item in enumerate(dispatch_list, 1):
            logger.info(f"处理第 {i}/{len(dispatch_list)} 个订单")
            
            result = self.dispatch_order(
                driver_id=item.get('driver_id'),
                order_id=item.get('order_id'),
                date=item.get('date'),
                time_slot=item.get('time_slot'),
                **{k: v for k, v in item.items() if k not in ['driver_id', 'order_id', 'date', 'time_slot']}
            )
            
            results.append({
                'order_id': item.get('order_id'),
                'driver_id': item.get('driver_id'),
                'result': result
            })
        
        success_count = sum(1 for r in results if r['result'].get('success'))
        logger.info(f"批量派工完成 - 成功: {success_count}/{len(dispatch_list)}")
        
        return results
    
    def batch_withdraw(
        self,
        order_ids: List[int],
        reason: str = None
    ) -> List[Dict[str, Any]]:
        """
        批量退工
        
        Args:
            order_ids: 订单ID列表
            reason: 退工原因
            
        Returns:
            批量退工结果列表
        """
        results = []
        
        logger.info(f"开始批量退工 - 共 {len(order_ids)} 个订单")
        
        for i, order_id in enumerate(order_ids, 1):
            logger.info(f"处理第 {i}/{len(order_ids)} 个订单")
            
            result = self.withdraw_order(
                order_id=order_id,
                reason=reason
            )
            
            results.append({
                'order_id': order_id,
                'result': result
            })
        
        success_count = sum(1 for r in results if r['result'].get('success'))
        logger.info(f"批量退工完成 - 成功: {success_count}/{len(order_ids)}")
        
        return results
    
    def get_driver_orders(
        self,
        driver_id: int,
        date: str = None
    ) -> List[Dict[str, Any]]:
        """
        获取司机的订单列表
        
        Args:
            driver_id: 司机ID
            date: 日期
            
        Returns:
            订单列表
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            params = {
                'driver_id': driver_id,
                'date': date
            }
            response = self.api.get(config.ENDPOINTS['schedules'], params=params)
            orders = response.get('data', [])
            logger.info(f"司机 {driver_id} 在 {date} 有 {len(orders)} 个订单")
            return orders
        except Exception as e:
            logger.error(f"获取司机订单失败: {e}")
            return []
