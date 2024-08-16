import logging

from fastapi import APIRouter, status, Query, Body, Depends, UploadFile, File
from fastapi_versioning import version
from fastapi_limiter.depends import RateLimiter
from apps.user_management.common.dependencies import get_current_user
from apps.user_management.permissions.permissions import check_permissions
from apps.user_management.user import User
from apps.e_commerce.product import AdminProductCreate,AdminProductRead,AdminProductUpdate,\
    ProductService, TemplateInfoService,AdditionalInfoItemRead, VariantsCreate,\
    VariantsUpdate, TemplateTypes, ComponentCreate, ComponentRead,\
    ComponentUpdate, ComponentService, ComponentTemplateUpdate, ComponentTemplateRead,\
    ComponentTemplateCreate, ComponentTemplateService
from apps.base import NotFoundException, PaginationBase,\
    SuccessResponse, FileBase, InvalidExtensionException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/product-admin",
    tags=["Продyкты-> Админка"]
)


#-------------product-------------


@router.post("", 
        response_model=AdminProductRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create(
        data: AdminProductCreate = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.product, "c")
    return await ProductService.create(data.model_dump(),market=current_user.market)


@router.patch("", 
        response_model=AdminProductRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update(
        id:str = Query(...),
        data: AdminProductUpdate = Body(None),
        current_user: User = Depends(get_current_user)
        ):
    check_permissions(current_user.permissions.product, "u")
    product = await ProductService.product_update(id, data.model_dump(exclude_none=True), market=current_user.market)
    return product


@router.get("", 
        response_model=PaginationBase[AdminProductRead]|AdminProductRead|None, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get(
        id: str = Query(None),
        category_id: str = Query(None),
        subcategory_id: str = Query(None),
        brand_ids: list[str] = Query(None),
        search:str = Query(None),
        min_price: float = Query(None, ge=0),
        max_price: float = Query(None,ge=0),
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.product, "r")
    if id:
        return await ProductService.get_by_id(id=id,market=current_user.market)
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
        filter_query["subcategory.id"] = subcategory_id
    if category_id:
        filter_query["category.id"] = category_id
    if brand_ids:
        filter_query["brand.id"] = {"$in":brand_ids}
    return await ProductService.get_all(
        page,
        page_size, 
        paginate=True, 
        filter_criteria=filter_query,
        market=current_user.market)


@router.delete("", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete(
        id: str = Query(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.product, "d")
    existing_subcategory = await ProductService.get_by_id(id, market=current_user.market)
    if not existing_subcategory:
        raise NotFoundException(3)
    await ProductService.delete(id=id)
    return SuccessResponse


@router.patch("/add-file", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def add_file(
        id:str,
        images: list[UploadFile] = File(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.category, "u")
    product = await ProductService.get_by_id(id, market=current_user.market)
    if not product:
        raise NotFoundException(3)
    images_data = []
    for image in images:
        if image.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidExtensionException()
        images_data.append(await FileBase.save_upload_file(
            image, 
            market=current_user.market,
            destination_path="product/images"))
    await ProductService.add_items_to_set(id,"images",images_data)
    return SuccessResponse

@router.delete("/delete-file", 

        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_file(
        id:str,
        file_path: list[str] = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.category, "u")
    product = await ProductService.get_by_id(id,market=current_user.market)
    if not product:
        raise NotFoundException(3)
    for path in file_path:
        await FileBase.delete_file(path)
    await ProductService.remove_items_from_set(id,"images",file_path)
    return SuccessResponse


#-------product_variant-------------


@router.patch("/add-product-variant", 
        response_model=AdminProductRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def add_product_variant(
        product_id:str,
        variants: list[VariantsCreate],
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.product, "u")
    variants_data = [variant.model_dump() for variant in variants]
    return await ProductService.add_product_variant(
        product_id=product_id,
        variants=variants_data,
        market=current_user.market)


@router.patch("/update-product-variant", 
        response_model=AdminProductRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update_product_variant(
        product_id:str,
        variant_idx:str,
        data: VariantsUpdate,
        current_user: User = Depends(get_current_user),):
    check_permissions(current_user.permissions.product, "u")
    return await ProductService.update_product_variant(
        variant_idx=variant_idx,
        product_id=product_id,
        data=data.model_dump(exclude_unset=True,exclude_none=True), 
        market=current_user.market)


@router.patch("/remove-product-variant", 
        response_model=AdminProductRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def remove_product_variant(
        product_id:str,
        variant_idx:str,
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.product, "u")
    return await ProductService.remove_product_variant(
        product_id=product_id,
        variant_idx=variant_idx, 
        market=current_user.market)


#---------component-------


@router.post("/component", 
        response_model=ComponentRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create_component(
        data: ComponentCreate = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.component, "c")
    return await ComponentService.create(data.model_dump(),market=current_user.market)


@router.get("/component", 
        response_model=PaginationBase[ComponentRead]|ComponentRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get_component(
        id: str = Query(None),
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.component, "r")
    if id:
        return await ComponentService.get_by_id(id,market=current_user.market)
    return await ComponentService.get_all(
        page=page,
        page_size=page_size,
        paginate=True,
        market=current_user.market)


@router.patch("/component", 
        response_model=ComponentRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update_component(
        id: str = Query(...),
        data: ComponentUpdate = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.component, "u")
    return await ComponentService.update(id=id,update_data=data.model_dump(),market=current_user.market)


@router.delete("/component", 
        response_model=SuccessResponse, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_component(
        id: str = Query(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.component, "d")
    await ComponentService.delete(id=id, market=current_user.market)
    return SuccessResponse


#-----Component-Template---


@router.post("/component-template", 
        response_model=ComponentTemplateRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=3,seconds=5))])
@version(1)
async def create_component_template(
        data: ComponentTemplateCreate = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.component, "c")
    return await ComponentTemplateService.create(data.model_dump(),market=current_user.market)


@router.get("/component-template", 
        response_model=PaginationBase[ComponentTemplateRead], 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def read_component_template(
        current_user: User = Depends(get_current_user),
        page:int=Query(gt=0,default=1), page_size:int=Query(gt=0,default=10)):
    check_permissions(current_user.permissions.component, "r")
    return await ComponentTemplateService.get_all(
        page=page,
        page_size=page_size,
        paginate=True,
        market=current_user.market)


@router.patch("/component-template", 
        response_model=ComponentTemplateRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update_component_template(
        id:str,
        data: ComponentTemplateUpdate = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.component, "u")
    return await ComponentTemplateService.update(
        id=id,
        update_data=data.model_dump(),
        market=current_user.market)


#--------Templates---------


@router.post("/template",
        response_model=AdditionalInfoItemRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def create_template(
        name:str,
        type:TemplateTypes,
        keys: list[dict] = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.product, "c")
    return await TemplateInfoService.create(
        name=name,
        type=type,
        keys=keys,
        market=current_user.market)


@router.get("/template",
        response_model=list[AdditionalInfoItemRead], 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def get_templates(
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.product, "r")
    return await TemplateInfoService.get_all(market=current_user.market)


@router.patch("/template",
        response_model=AdditionalInfoItemRead, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def update_template(
        id:str = Query(...),
        name:str = Query(...),
        keys:list[dict] = Body(...),
        current_user: User = Depends(get_current_user)):
    check_permissions(current_user.permissions.product, "u")
    return await TemplateInfoService.update(id,name, keys, market=current_user.market)


@router.delete("/template",
        response_model=dict, 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(times=2, seconds=5))])
@version(1)
async def delete_template(
        id:str = Query(...),
        name:str = Query(...),
        keys:list[dict] = Body(...),
        current_user: User = Depends(get_current_user),):
    check_permissions(current_user.permissions.product, "d")
    return await TemplateInfoService.delete(id,market=current_user.market)