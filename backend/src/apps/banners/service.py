from fastapi import HTTPException, status

from apps.base import BaseDAO, NotFoundException, PaginationBase, AlreadyExistException
from .model import Banner
from apps.market.model import Market

class BannerService(BaseDAO[Banner]):
    model = Banner

    @classmethod
    async def create(cls, data: dict, market:Market|None=None) -> Banner:
        query = {"name":data["name"]}
        if market:
            query['market.id'] = market.id
        if await cls.get_one_by(query):
            raise AlreadyExistException(cls.model._error_num)
        return await super().create(data=data, market=market)