from apps.base import BaseDAO, AlreadyExistException, NotFoundException, ForbiddenException, InvalidDataException
from .model import Market
from apps.user_management.user.user_service import UserService, User
from apps.user_management.auth.auth import verify_password
from apps.user_management.auth.auth import get_password_hash
from apps.user_management.permissions.permission_service import GroupService
from apps.e_commerce.brand import BrandService
from apps.e_commerce.category import CategoryService
from apps.e_commerce.order import OrderService
from apps.e_commerce.product import ProductService, TemplateInfoService, CommentService
from apps.e_commerce.promocode import PromoCodeService
from apps.e_commerce.subcategory import SubcategoryService
from apps.newsletters.notifications import NotificationsService


class MarketService(BaseDAO[Market]):
    model = Market

    @classmethod
    async def create(cls, data:dict, admin:dict) -> Market:
        existing_market = await cls.get_by_domain_or_ip(data["domain"])
        if existing_market:
            raise AlreadyExistException(1)
        existing_user = await UserService.get_user_by_email(admin['email'])
        if existing_user:
            raise AlreadyExistException(2)
        password = get_password_hash(admin['password'])
        if admin.get('group_id'):
            group = await GroupService.get_by_id(id=admin['group_id'])
            if not group:
                raise NotFoundException(9)
            admin['permissions'] = group.permissions.model_dump()
            admin['group'] = {"name":group.name, "id":group.id}
        market = await super().create(data)
        admin['password'] = password
        admin['is_active'] = True
        admin['is_staff'] = True
        user = await UserService.create(admin,market=market)
        return await cls.update(id=market.id,update_data={"admin":user.model_dump()})

    @classmethod
    async def get_by_domain_or_ip(cls, domain: str, ip:str|None=None) -> Market|None:
        collection = await cls.get_collection()
        query = {"domain": domain}
        if ip:
            query['ip'] = ip
        document = await collection.find_one(query)
        if not document:
            return document
        return cls.model(**document) #type:ignore

    @classmethod
    async def cascade_delete_all_market_data(cls,current_user:User, id: str, domain:str,admin_id:str, password:str):
        if not current_user.is_global:
            raise ForbiddenException()
        admin = await UserService.get_by_id(id=admin_id)
        if not admin:
            raise NotFoundException(2)
        market = await cls.get_by_id(id)
        if not market:
            raise NotFoundException(1)
        if market.domain != domain or not verify_password(password, current_user.password) or admin.market.id != market.id: #type:ignore
            raise InvalidDataException()
        await CategoryService.delete_many(filter_criteria={},market=market)
        await UserService.delete_many(filter_criteria={},market=market)
        await SubcategoryService.delete_many(filter_criteria={},market=market)
        await BrandService.delete_many(filter_criteria={},market=market)
        await NotificationsService.delete_many(filter_criteria={},market=market)
        await OrderService.delete_many(filter_criteria={},market=market)
        await PromoCodeService.delete_many(filter_criteria={},market=market)
        await ProductService.delete_many(filter_criteria={},market=market)
        await TemplateInfoService.delete_many(filter_criteria={},market=market)
        await CommentService.delete_many(filter_criteria={},market=market)
        await ProductService.delete_many(filter_criteria={},market=market)
        await GroupService.delete_many(filter_criteria={},market=market)
        return await cls.delete(id)