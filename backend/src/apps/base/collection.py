from pydantic import BaseModel
from typing import Any, TypeVar, Generic
from config.database import get_db
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from .validators import validate_object_id
from .exception import NotFoundException, InvalidDataException
from .shemas import PaginationBase
from apps.market.model import Market

T = TypeVar("T", bound=BaseModel)

class BaseDAO(Generic[T]):
    model = BaseModel

    @classmethod
    async def get_collection(cls)->AsyncIOMotorCollection:
        async_db = await get_db()
        collection = async_db[cls.model.__collection_name__]#type:ignore
        return collection

    @classmethod
    async def create(cls, data: dict, market:Market|None=None) -> T:
        from .services import LanguageService
        data = cls.model(**data).model_dump()
        data.pop("id")
        collection = await cls.get_collection()
        translate_data = data.get("translate_content", [])
        lang_codes = set()

        if translate_data:
            for translate in translate_data:
                if not await LanguageService.get_by_code(translate['lang_code'], market) :
                    raise NotFoundException(10)
                if translate['lang_code'] in lang_codes:
                    raise InvalidDataException(10)
                else:
                    lang_codes.add(translate['lang_code'])
        if market:
            data['market'] = market.model_dump()
        result = await collection.insert_one(data)
        data['_id'] = ObjectId(result.inserted_id)
        return cls.model(**data) #type:ignore

    @classmethod
    async def update(cls, id: str, update_data: dict, market:Market|None=None) -> T:
        from .services import LanguageService
        collection = await cls.get_collection()
        translate_data = update_data.get("translates", [])
        if translate_data:
            for translate in translate_data:
                if not await LanguageService.get_by_code(translate['lang_code'], market) :
                    raise NotFoundException(10)
        query:dict[str,Any] = {"_id": ObjectId(id)}
        if market:
            query["market.id"] = market.id
        await collection.update_one(query, {"$set": update_data})
        document = await collection.find_one(query)
        if not document:
            raise NotFoundException(cls.model._error_num) #type:ignore
        return cls.model(**document) #type:ignore

    @classmethod
    async def get_all(cls, page:int=1, page_size:int=10,filter_criteria:dict|None=None,
                    sort_criteria: list|None=None, paginate: bool = False, 
                    market:Market|None=None)->PaginationBase[T]|list[T]:
        collection = await cls.get_collection()
        if filter_criteria is None:
            filter_criteria = {}
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
    async def get_one_by(cls, fields:dict[str,Any], market:Market|None=None) -> T|None:
        collection = await cls.get_collection()
        query = {}
        if market:
            query["market.id"] = market.id
        for key, value in fields.items():
            if key in ["_id","id"]:
                validate_object_id(value)
                query["_id"] = ObjectId(value)
                continue
            query[key] = value
        document = await collection.find_one(query)
        if not document:
            return document
        return cls.model(**document) #type:ignore

    @classmethod
    async def get_by_id(cls, id: str, market:Market|None=None) -> T|None:
        validate_object_id(id)
        collection = await cls.get_collection()
        query:dict = {"_id": ObjectId(id)}
        if market:
            query["market.id"] = market.id
        document = await collection.find_one(query)
        if not document:
            return document
        return cls.model(**document) #type:ignore

    @classmethod
    async def delete(cls, id: str, market:Market|None=None) -> dict:
        validate_object_id(id)
        collection = await cls.get_collection()
        if market:
            result = await collection.delete_one({"_id": ObjectId(id),"market.id":market.id})
        else:
            result = await collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 1:
            return {"message": "Document deleted successfully"}
        else:
            return {"message": "Document not found"}

    @classmethod
    async def delete_many(cls, filter_criteria: dict,market:Market|None=None) -> dict:
        collection = await cls.get_collection()
        if market:
            filter_criteria['market.id'] = market.id
        result = await collection.delete_many(filter_criteria)
        return {"message": f"{result.deleted_count} documents deleted"}

    @classmethod
    async def add_items_to_set(cls, id: str, field:str,items: list[Any]|Any, market:Market|None=None) -> T:
        collection = await cls.get_collection()
        update_dict = {"$addToSet": {field: {"$each": items}}}
        query:dict[str,Any] = {"_id": ObjectId(id)}
        if market:
            query["market.id"] = market.id
        await collection.update_one(query, update_dict)
        document = await collection.find_one(query)
        if not document:
            raise NotFoundException(cls.model._error_num)  # type: ignore
        return cls.model(**document) #type:ignore
    
    @classmethod
    async def remove_items_from_set(cls, id: str,field:str, items: list[Any], market:Market|None=None) -> T:
        collection = await cls.get_collection()
        update_dict = {"$pullAll": {field: items}}
        if market:
            await collection.update_one({"_id": ObjectId(id),"market.id":market.id}, update_dict)
            document = await collection.find_one({"_id": ObjectId(id), "market.id":market.id})
        else:
            await collection.update_one({"_id": ObjectId(id)}, update_dict)
            document = await collection.find_one({"_id": ObjectId(id)})
        if not document:
            raise NotFoundException(cls.model._error_num)  # type: ignore
        return cls.model(**document) #type:ignore
    
    @classmethod
    async def _fetch_all(cls, items: list[dict]) -> list[T]:
        fetched_items = []
        for document in items:
            fetched_items.append(cls.model(**document))
        return fetched_items