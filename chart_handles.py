# encoding:utf-8
__author__ = 'kalomuse'

from common.base import AdminBaseHandler
from datacache.datacache import UserMsgCache
from services.orders.order_services import OrderServices
from conf.order_conf import ORDER_STATUS,ORDER_TYPE,INTERVAL_TYPE
from services.product.service_product_service import ServiceProductService
import time
import math

class OrderChartShowHandle(AdminBaseHandler):
    def get(self, *args, **kwargs):
        #订单图表展示
        self.get_paras_dict()
        order_db = OrderServices(self.db)
        sps_db = ServiceProductService(self.db)
        query = order_db.query_order_to_chart(**self.qdict)
        #添加订单为零数据
        res = []
        last_timestamp = 0

        if self.qdict.get('interval', '') == "week":    #按周搜索
            interval = 3600 * 24 * 7
        elif self.qdict.get('interval', '') == "month": #按月搜索
            interval = 3600 * 24 * 31
        else:
            interval = 3600 * 24                    #按日搜索
        for value in query:#循环结果集query
            if(not last_timestamp):#如果前一个时间点时间戳为空
                last_timestamp = time.mktime(time.strptime(value[0],'%Y-%m-%d'))#初始化上一个时间戳
                #计算偏移
                if self.qdict.get('interval', '') == "week":                        #周偏移,星期一偏移为0,星期二偏移为1
                    last_timestamp = last_timestamp - value[2] * 3600 * 24
                elif self.qdict.get('interval', '') == "month":                     #月偏移
                    last_timestamp = last_timestamp - (value[3] - 1) * 3600 * 24
                #重置偏移
                date = time.strftime('%Y-%m-%d', time.localtime(last_timestamp))
                res.append([date, value[1]])
                continue
            else:
                now_timestamp = time.mktime(time.strptime(value[0],'%Y-%m-%d'))
                if self.qdict.get('interval', '') == "week":
                    now_timestamp = now_timestamp - value[2] * 3600 * 24
                elif self.qdict.get('interval', '') == "month":
                    now_timestamp = now_timestamp - (value[3] - 1) * 3600 * 24
                date_res = time.strftime('%Y-%m-%d', time.localtime(now_timestamp))
                #计算与上一个时间点相差时间
                diff = math.ceil((last_timestamp - now_timestamp) / interval - 1)
                while(diff):#插入为0结果集
                    date = time.strftime('%Y-%m-%d', time.localtime(now_timestamp + diff * interval))
                    res.append([date, 0])
                    diff = diff - 1
                res.append([date_res, value[1]])
                last_timestamp = now_timestamp
        if(not self.qdict.get('end_time', '')):
            res = res[:30];

        self.echo('ops/orders/order_chart.html',{
            'interval': INTERVAL_TYPE,
            'data_info': res[-30:],
            'order_type': ORDER_TYPE,
            'status': ORDER_STATUS,
            'user_db': UserMsgCache(self.db),
            'sps_db' : sps_db,
            'qdict': self.qdict,
        })

