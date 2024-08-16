from typing import Any
from apps.base import BaseDAO, PaginationBase, validate_object_id, NotFoundException
from .model import Notification, NotificationStatus
from apps.market.model import Market


class NotificationsService(BaseDAO[Notification]):
    model = Notification


    @classmethod
    async def create_global_notification(cls, data: dict,market_ids:list=[]) -> Notification:
        from apps.market.market_service import MarketService
        data['status'] = NotificationStatus.GLOBAL
        if market_ids:
            for id in market_ids:
                if not await MarketService.get_by_id(id=id):
                    raise NotFoundException(1)
            data['recipient_markets_ids'] = market_ids
        else:
            collection = await cls.get_collection()
            market_ids = await collection.find({}, {'_id': 1}) # type: ignore
            data['recipient_markets_ids'] = []
            for id in market_ids:
                data['recipient_markets_ids'].append(str(id))
        return await super().create(data=data)
    
    @classmethod
    async def create_market_notification(cls, data: dict, market:Market|None=None) -> Notification:
        data['status'] = NotificationStatus.MARKET
        return await super().create(data=data, market=market)


    @classmethod
    async def get_global_notifications(cls,id:str|None=None, page:int=1, page_size:int=10,market:Market|None=None):
        if not market:
            return await cls.get_all(page=page,page_size=page_size,filter_criteria={"status": NotificationStatus.GLOBAL}, paginate=True)#type:ignore
        collection = await cls.get_collection()
        match_stage:dict[Any,Any] = {
            '$match': {
                "status": NotificationStatus.GLOBAL,
                "recipient_markets_ids":market.id
                }
        }
        if id:
            match_stage['$match']['_id'] = validate_object_id(id)
            
        pipeline = [
            {'$unwind': '$recipient_markets_ids'},
            match_stage,
            {'$addFields': {'_id': {'$toString': '$_id'}}},
            {'$skip': (page - 1) * page_size},
            {'$limit': page_size}
        ]
        if id:
            try:
                return await collection.aggregate(pipeline).next()
            except StopAsyncIteration:
                raise NotFoundException(11)
        
        count_pipeline = [
                {'$unwind': '$recipient_markets_ids'},
                match_stage,
                {
                    '$count': 'total'
                }
            ]
        items = []
        async for document in collection.aggregate(pipeline):
            items.append(document)
        total_result = await collection.aggregate(count_pipeline).next() if items else {'total': 0}
        total = total_result['total']
        return PaginationBase(
                items=items,
                total=total,
                page=page,
                page_size=page_size
                )