from bson import ObjectId
from datetime import datetime
from apps.base import BaseDAO, NotFoundException, InvalidDataException, SpecialException,\
    DataTypes
from .product_model import Product, TemplateInfo
from .product_info_model import TemplateInfo, TemplateTypes
from .public_model import ProductVisits
from apps.e_commerce.category import CategoryService
from apps.e_commerce.subcategory import SubcategoryService
from apps.e_commerce.brand import BrandService
from apps.market.model import Market
from .product_info_service import TemplateInfoService, ComponentTemplateService, ComponentService


class ProductService(BaseDAO[Product]):
    model = Product

    @classmethod
    async def process_product(cls, data: dict, market:Market|None=None) -> dict:
        if data.get('category_id'):
            category = await CategoryService.get_by_id(data.pop("category_id"), market=market)
            if not category:
                raise NotFoundException(3)
            data['category'] = category.model_dump()
        if data.get('subcategory_id'):
            subcategory = await SubcategoryService.get_by_id(data.pop('subcategory_id'), market=market)
            if not subcategory:
                raise NotFoundException(4)
            if category.subcategories:
                if subcategory not in category.subcategories:
                    raise NotFoundException(4)
            data['subcategory'] = subcategory.model_dump()
        if data.get("brand_id"):
            brand = await BrandService.get_by_id(data.pop("brand_id"), market=market)
            if not brand:
                raise NotFoundException(7)
            data['brand'] = brand
        if data.get('additional_info_template'):
            template = await TemplateInfoService.get_one_by(
                {"_id":data['additional_info_template']['id'],
                "type":TemplateTypes.ADDITIONAL_INFO.value},
                market=market)
            if not template:
                raise NotFoundException(14)
            for idx, field in enumerate(template.fields):
                field["value"] = data['additional_info_template']['fields'][str(idx)]
            data.pop('additional_info_template')
            data['additional_info'] = template.model_dump()
        elif data.get('additional_info'):
            additional_data = {
                "id":None,
                "name":None,
                "type":TemplateTypes.ADDITIONAL_INFO.value,
                "fields":[]}
            for field in data['additional_info']['fields']:
                additional_data['fields'].append(field)
            data['additional_info'] = additional_data
        if data.get("variants"):
            data["variants"] = await cls.process_product_variant(data["variants"], market=market)
            data["variants"] = {str(ObjectId()):variant for variant in data["variants"]}
        else:
            data['variants'] = {}
        return data

    @classmethod
    async def create(cls, data: dict, market:Market|None=None) -> Product:
        data = await cls.process_product(data, market=market)
        return await super().create(data=data, market=market)

    @classmethod
    async def process_product_variant(cls, variants:list, market:Market|None=None) -> list:
        for variant in variants:
            if variant.get('component_template'):
                component_template = await ComponentTemplateService.get_by_id(variant["component_template"]["id"],market=market)
                if not component_template:
                    raise NotFoundException()
                components_template_dict = component_template.model_dump()
                variant['components'] = components_template_dict['components']
                for key,value in variant['component_template']['values'].items():
                    variant['components'][key]['value'] = DataTypes(component_template.components[key].type).convert(value)
                variant.pop("component_template")
                variant['component_template_name'] = component_template.name
            elif variant.get('components'):
                components = []
                for component in variant['components']:
                    existing_component = await ComponentService.get_by_id(component['id'],market=market)
                    if not existing_component:
                        raise NotFoundException(17)
                    existing_component.value = DataTypes(existing_component.type).convert(component['value'])
                    components.append(existing_component.model_dump())
                variant['components'] = components
        return variants

    @classmethod
    async def add_product_variant(cls,product_id:str,variants:list, market:Market|None=None) -> Product:
        product = await cls.get_by_id(product_id,market=market)
        if not product:
            raise NotFoundException(8)
        variants = await cls.process_product_variant(variants, market=market)
        for variant in variants:
            result = await cls.update(
                id=product_id,
                update_data={f"variants.{str(ObjectId())}":variant}
                )
        return result

    @classmethod
    async def update_product_variant(
            cls,
            product_id:str,
            variant_idx:str,
            data:dict, 
            market:Market|None=None) -> Product:
        product = await cls.get_by_id(id=product_id,market=market)
        if not product:
            raise NotFoundException(8)
        if not product.variants.get(variant_idx):
            raise NotFoundException()
        variant = await cls.process_product_variant([data], market=market)
        return await cls.update(product_id, 
                    {f"variants.{variant_idx}":variant[0]},
                    market=market) 

    @classmethod
    async def remove_product_variant(
            cls, 
            product_id: str, 
            variant_idx: str, 
            market=None) -> Product:
        product = await cls.get_by_id(id=product_id, market=market)
        if not product:
            raise NotFoundException(8)
        if not product.variants.get(variant_idx):
            raise NotFoundException()
        collection = await cls.get_collection()
        pull_query = {
            "$unset": {f"variants.{variant_idx}": 1}
        }
        await collection.update_one({"_id": ObjectId(product_id)}, pull_query)
        document = await cls.get_by_id(id=product_id, market=market)
        if not document:
            raise NotFoundException(cls.model._error_num)  # type: ignore
        return document

    @classmethod
    async def product_update(cls,id:str, data: dict,market:Market|None=None) -> Product|None:
        product = await  cls.get_by_id(id,market=market)
        if not product:
            raise NotFoundException(8)   
        data = await cls.process_product(data, market=market)
        return await super().update(id=id, update_data=data)

    @classmethod
    async def get_product_by_id(cls,current_user, id:str,market:Market|None=None):
        product = await cls.get_by_id(id=id,market=market)
        if product:
            today_visits:ProductVisits = await ProductVisitsService.get_one_by(fields={"date": datetime.today(),"product_id":product.id})  # type: ignore
            if today_visits:
                if current_user:
                    if not str(current_user.id) in today_visits.registered_users:
                        await ProductVisitsService.add_items_to_set(id=today_visits.id,field="registered_users",items=[current_user])
                else:
                    await ProductVisitsService.update(id=today_visits.id,update_data={"anonym_users":today_visits.anonym_users+1})
            else:
                if current_user:
                    data = {
                        "product_id":product.id,
                        "registered_users":[str(current_user.id)]}
                    await ProductVisitsService.create(data,market=market)
                else:
                    data = {
                        "product_id":product.id,
                        "anonym_users":1}
                    await ProductVisitsService.create(data=data, market=market)
        return product


class ProductVisitsService(BaseDAO[TemplateInfo]):
    model = ProductVisits