from .model import Language
from .collection import BaseDAO

class LanguageService(BaseDAO[Language]):
    model = Language

    @classmethod
    async def create(cls, data: dict, market=None) -> Language:
        data["market"] = market
        return await super().create(data)

    @classmethod
    async def get_by_code(cls, code: str, market=None) -> Language|None:
        collection = await cls.get_collection()
        if market:
            document = await collection.find_one({"language_code": code, "market.id": market.id})
        else:
            document = await collection.find_one({"language_code": code})
        if not document:
            return None
        return cls.model(**document)