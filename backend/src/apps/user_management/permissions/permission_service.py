from bson import ObjectId
from typing import Any
from apps.base import validate_object_id, PaginationBase
from apps.base import BaseDAO, NotFoundException
from .model import Group 
from apps.market.model import Market
from apps.user_management.user import UserService

class GroupService(BaseDAO[Group]):
    model = Group


    @classmethod
    async def update(cls, id:str,update_data:dict,market=None):
        group = await cls.get_by_id(id=id,market=market)
        if not group:
            raise NotFoundException(9)
        group = await super().update(id=group.id,update_data=update_data,market=market)
        users = await UserService.get_all(filter_criteria={"group.group_id":group.id})
        for user in users:
            await UserService.update_assistant_or_admin(id=user.id, user_data={"group_id":group.id}) #type:ignore
        return group
    
    @classmethod
    async def delete(cls, id:str,market=None):
        group = await cls.get_by_id(id=id,market=market)
        if not group:
            raise NotFoundException(9)
        users = await UserService.get_all(filter_criteria={"group.group_id":group.id})
        for user in users:
            await UserService.update_assistant_or_admin(id=user.id, user_data={"group_id":None}) #type:ignore
        return await cls.delete(id=id)


    @classmethod
    async def get_all(cls, page:int=1, page_size:int=10,filter_criteria:dict|None=None,
                    sort_criteria: list|None=None, paginate: bool = False, 
                    market:Market|None=None)->PaginationBase[Group]|list[Group]:
        collection = await cls.get_collection()
        if filter_criteria is None:
            filter_criteria = {}
        filter_criteria['market.id'] = None
        if market:
            filter_criteria['market.id'] = market.id
        cursor = collection.find(filter_criteria)
        if sort_criteria:
            cursor = cursor.sort(sort_criteria)
        if paginate:
            offset = (page - 1) * page_size
            cursor = cursor.skip(offset).limit(page_size)
            items = await cursor.to_list(None)
            items = await cls._fetch_all(items)
            total = await collection.count_documents(filter_criteria) if filter_criteria else await collection.count_documents({})
            return PaginationBase(
                items=items,
                total=total,
                page=page,
                page_size=page_size
                )
        else:
            documents = await cursor.to_list(None)
            return await cls._fetch_all(documents)


    @classmethod
    async def get_by_id(cls, id:str,market=None):
        validate_object_id(id)
        collection = await cls.get_collection()
        query:dict[str,Any] = {"_id": ObjectId(id)}
        if market:
            query["market.id"] = market.id
        document = await collection.find_one(query)
        if not document:
            return document
        return cls.model(**document) #type:ignore