
import random
import string
from fastapi import HTTPException, status

from apps.base import BaseDAO, NotFoundException, AlreadyExistException
from .model import PromoCode, PromoCodeTypeNames
from apps.e_commerce.category import CategoryService
from apps.e_commerce.subcategory import SubcategoryService
from apps.e_commerce.product import ProductService
from apps.market.model import Market

class PromoCodeService(BaseDAO[PromoCode]):
    model = PromoCode

    @classmethod
    async def generate_code(cls, length:int) -> str:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if await cls.get_by_code(code):
            return await cls.generate_code(length)
        return code

    @classmethod
    async def create(cls, data: dict, code_length:int,market:Market|None=None) -> PromoCode:
        if not data['code']:
            data['code'] = await cls.generate_code(code_length)
        elif await cls.get_by_code(data["code"],market=market):
            raise AlreadyExistException(6)
        if data['type']['type_name'] == PromoCodeTypeNames.CATEGORY:
            for category_id in data['type']['content_ids']:
                if not await CategoryService.get_by_id(category_id,market=market):
                    raise NotFoundException(3)
        elif data['type']['type_name'] == PromoCodeTypeNames.SUBCATEGORY:
            for subcategory_id in data['type']['content_ids']:
                if not await SubcategoryService.get_by_id(subcategory_id,market=market):
                    raise NotFoundException(4)
        elif data['type']['type_name'] == PromoCodeTypeNames.PRODUCT:
            for product_id in data['type']['content_ids']:
                if not await ProductService.get_by_id(product_id,market=market):
                    raise NotFoundException(8)        
        if data['reusable'] and not data['validity']:
            raise HTTPException(status.HTTP_200_OK,"Validity is required for reusable promocodes")
        return  await super().create(data,market=market)


    @classmethod
    async def update(cls, code: str, data: dict,market:Market|None=None)->PromoCode:
        promocode = await cls.get_by_code(code=code,market=market)
        if not promocode:
            raise NotFoundException(6)
        if promocode.code != data['code']:
            if await cls.get_by_code(data['code'],market=market):
                raise AlreadyExistException(6)
        if data['type']['type_name'] == PromoCodeTypeNames.CATEGORY:
            for category_id in data['type']['content_ids']:
                if not await CategoryService.get_by_id(category_id,market=market):
                    raise NotFoundException(3)
        elif data['type']['type_name'] == PromoCodeTypeNames.SUBCATEGORY:
            for subcategory_id in data['type']['content_ids']:
                if not await SubcategoryService.get_by_id(subcategory_id,market=market):
                    raise NotFoundException(4)
        elif data['type']['type_name'] == PromoCodeTypeNames.PRODUCT:
            for product_id in data['type']['content_ids']:
                if not await ProductService.get_by_id(product_id,market=market):
                    raise NotFoundException(8)  
        return await super().update(id=promocode.id,update_data=data,market=market)


    @classmethod
    async def get_by_code(cls, code: str, market:Market|None=None) -> PromoCode|None:
        collection = await cls.get_collection()
        if market:
            document = await collection.find_one({"code": code,"market.id":market.id})
        else:
            document = await collection.find_one({"code": code})
        return document