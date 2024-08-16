from fastapi import HTTPException, status

from apps.base import BaseDAO, NotFoundException, PaginationBase
from .model import Category
from apps.e_commerce.subcategory import SubcategoryService
from apps.market.model import Market

class CategoryService(BaseDAO[Category]):
    model = Category

    @classmethod
    async def get_all(cls, page:int,page_size:int, market=None):
        data = await super().get_all(page=page,page_size=page_size,paginate=True, market=market)
        for category in data.items: #type:ignore
            subcategories = await SubcategoryService.get_all(filter_criteria={"category_id": str(category.id)}, market=market)
            category.subcategories = subcategories #type:ignore
        return data #type:ignore

    @classmethod
    async def get_detail_by_id(cls, id: str, market:Market|None=None) -> Category:
        category = await super().get_by_id(id=id, market=market)
        if not category:
            raise NotFoundException(3)
        category.subcategories = await SubcategoryService.get_all(filter_criteria={"category_id": str(category.id)}, market=market) #type:ignore
        return category 

    @classmethod
    async def delete(cls, id: str,market:Market|None=None) -> dict:
        from apps.e_commerce.product import ProductService
        category = await cls.get_by_id(id,market=market)
        if not category:
            raise NotFoundException(3)
        products = await ProductService.get_all(filter_criteria={"category._id":id}, market=market)
        if products:
            product_ids = [product.id for product in products] #type:ignore
            raise HTTPException(status.HTTP_409_CONFLICT, f"618994 {product_ids}")
        subcategories = await SubcategoryService.get_all(filter_criteria={"category_id":id}, market=market)
        if subcategories:
            subcategory_ids = [subcategory.id for subcategory in subcategories] #type:ignore
            raise HTTPException(status.HTTP_200_OK, f"614993 {subcategory_ids}")
        return await super().delete(id=id, market=market)
    
    @classmethod
    async def update(cls, id: str, update_data: dict, market:Market|None=None) -> Category:
        await super().update(id=id,update_data=update_data,market=market)
        category = await cls.get_detail_by_id(id=id,market=market)
        if not category:
            raise NotFoundException(3)
        return category