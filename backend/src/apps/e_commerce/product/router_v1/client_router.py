import logging
from fastapi_limiter.depends import RateLimiter
from fastapi import APIRouter, status, Query, Depends, Body
from fastapi_versioning import version
from apps.e_commerce.product import ProductRead, ProductService, CommentService, CommentRead, CommentCreate
from apps.base import PaginationBase, InvalidDataException
from apps.market.model import Market
from apps.market import MarketNotFoundException
from apps.user_management.user import User
from apps.market.dependencies import get_market
from apps.user_management.common.dependencies import get_current_user, get_current_user_or_none


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/product-client",
    tags=["Продyкты-> Клиентская"]
)


@router.get("", 
        response_model=PaginationBase[ProductRead]|ProductRead|None, 
        status_code=status.HTTP_200_OK, 
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        id: str = Query(None),
        search:str = Query(None),
        category_id: str = Query(None),
        subcategory_id: str = Query(None),
        brand_id: str = Query(None),
        market:Market=Depends(get_market),
        min_price: float = Query(None, ge=0),
        max_price: float = Query(None, ge=0),
        current_user: User = Depends(get_current_user_or_none),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    if not market:
        raise MarketNotFoundException()
    if id:
        return await ProductService.get_product_by_id(id=id,market=market,current_user=current_user)
    if min_price and max_price:
        if max_price < min_price:
            raise InvalidDataException()
    filter_query = {}
    if search:
        filter_query["translate_content"] = {"$elemMatch": {"content.name": {"$regex": search, "$options": "i"}}}
    if min_price:
        filter_query["price"] = {"ge":min_price}
    if max_price:
        if  "price" in filter_query:
            filter_query['price']['le'] = max_price
        else:
            filter_query["price"] = {"le":max_price}
    if subcategory_id:
        filter_query["subcategory_id"] = subcategory_id
    elif category_id:
        filter_query["category_id"] = category_id
    if brand_id:
        filter_query["brand.id"] = brand_id
    return await ProductService.get_all(
        page,
        page_size, 
        paginate=True,
        filter_criteria=filter_query,
        market=market)


#-------Comment--------


@router.get("/public", 
        response_model=PaginationBase[CommentRead], 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get_comments(
        product_id:str = Query(...),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10),
        market:Market=Depends(get_market),
        current_user: User = Depends(get_current_user)):
    if not market:
        raise MarketNotFoundException()
    return await CommentService.get_product_comments(
        page=page,
        page_size=page_size,
        product_id=product_id,
        market=current_user.market)


@router.post("/comment", response_model=CommentRead, status_code=status.HTTP_200_OK)
@version(1)
async def create(
        data:CommentCreate = Body(...),
        market:Market=Depends(get_market),
        current_user: User = Depends(get_current_user)):
    if not market:
        raise MarketNotFoundException()
    return await CommentService.create_comment(data=data.model_dump(),user=current_user,market=current_user.market)