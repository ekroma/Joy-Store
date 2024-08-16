from fastapi import HTTPException, status

from apps.base import BaseDAO, NotFoundException
from .model import Subcategory
from apps.market.model import Market

class SubcategoryService(BaseDAO[Subcategory]):
    model = Subcategory

    @classmethod
    async def delete(cls, id: str,market:Market|None=None) -> dict:
        from apps.e_commerce.product import ProductService
        existing_subcategory = await cls.get_by_id(id,market=market)
        if not existing_subcategory:
            raise NotFoundException(4)
        products = await ProductService.get_all(filter_criteria={"subcategory._id":id},market=market)
        if products:
            product_ids = [product.id for product in products] #type:ignore
            raise HTTPException(status.HTTP_200_OK, f"618994 {product_ids}")
        return await super().delete(id=id)