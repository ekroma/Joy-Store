from apps.base import BaseDAO
from .public_model import Comment
from apps.market.model import Market
from apps.user_management.user import User


class CommentService(BaseDAO[Comment]):
    model = Comment

    @classmethod
    async def create_comment(cls,data:dict,user:User,market:Market|None=None) -> Comment:
        data = {"user":user,"product_id":data['product_id'],"text":data['text'],"rating":data['rating']}
        return await super().create(data=data,market=market)

    @classmethod
    async def get_product_comments(cls,product_id:str,page:int=1, page_size:int=10,market:Market|None=None):
        return await cls.get_all(
            page=page,
            page_size=page_size,
            filter_criteria={"product_id":product_id},
            market=market,
            paginate=True)