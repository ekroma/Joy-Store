from apps.base import BaseDAO, NotFoundException, LanguageService, AlreadyExistException
from .product_model import TemplateInfo
from .product_info_model import TemplateInfo, TemplateTypes, Component, ComponentTemplate
from apps.market.model import Market



class ComponentService(BaseDAO[Component]):
    model = Component


class ComponentTemplateService(BaseDAO[ComponentTemplate]):
    model = ComponentTemplate

    @classmethod
    async def create(cls,data, market:Market|None=None) -> ComponentTemplate:
        existing_component_name = await cls.get_one_by({"name":data["name"]},market=market)
        if existing_component_name:
            raise AlreadyExistException()
        data["components"] = []
        for component_id in data['components_ids']:
            component = await ComponentService.get_by_id(component_id,market=market)
            if not component:
                raise NotFoundException(17)
            data["components"].append(component)
        return await super().create(data,market=market)


class TemplateInfoService(BaseDAO[TemplateInfo]):
    model = TemplateInfo
    
    @classmethod
    async def create(cls, name:str,type:TemplateTypes,keys: list[dict],market:Market|None=None) -> TemplateInfo:
        languages = await LanguageService.get_all(market=market)
        languages = [lng.language_code for lng in languages] #type:ignore
        fields = []
        for key in keys:
            for lng in key:
                if lng not in languages:
                    raise NotFoundException(10)
            fields.append({"key": key, "value": None})
        template = {
            "type":type,
            "name":name,
            "fields":fields}
        return await super().create(template,market=market)


    @classmethod
    async def update(cls, id: str,name:str, keys: list,market:Market|None=None):
        languages = await LanguageService.get_all(market=market)
        languages = [lng.language_code for lng in languages] #type:ignore
        fields = []
        for key in keys:
            for lng in key:
                if lng not in languages:
                    raise NotFoundException(10)
            fields.append({"key": key, "value": None})
        return await super().update(id,{"name":name,"fields":fields},market=market)