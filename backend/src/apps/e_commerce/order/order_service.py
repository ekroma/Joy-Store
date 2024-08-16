from datetime import datetime
from fastapi import HTTPException, status
from typing import Any

from apps.base import BaseDAO, NotFoundException, ForbiddenException,\
    InvalidDataException, SpecialException
from .model import Order, OrderStatus, Customer
from apps.user_management.user import User
from apps.e_commerce.product import ProductService
from apps.e_commerce.promocode import PromoCodeService, PromoCodeTypeNames
from apps.market.model import Market

class OrderService(BaseDAO[Order]):
    model = Order

    @classmethod
    async def process_promocodes(cls,promocodes:list[str], product,market:Market|None=None)-> dict:
        total_price = product.price
        not_reusable_promocodes = []
        reusable_promocodes = []
        for promocode_data in promocodes:
            promocode = await PromoCodeService.get_by_code(promocode_data, market=market)
            if not promocode:
                raise NotFoundException(6)
            if promocode.validity:
                if promocode.validity < datetime.now():
                    raise InvalidDataException(6)
                
            if promocode.type.type_name == PromoCodeTypeNames.CATEGORY and str(product.category.id) in promocode.type.content_ids or \
                promocode.type.type_name == PromoCodeTypeNames.SUBCATEGORY and str(product.subcategory.id) in promocode.type.content_ids or \
                promocode.type.type_name == PromoCodeTypeNames.PRODUCT and str(product.id) in promocode.type.content_ids:
                discount = product.price * promocode.discount/100
                total_price -= discount
                if not promocode.reusable:
                    not_reusable_promocodes.append(promocode.code)
                else:
                    reusable_promocodes.append(promocode.code)
        return {"total_price":total_price, "not_reusable_promocodes":not_reusable_promocodes, "reusable_promocodes":reusable_promocodes}

    @classmethod
    async def process_order(cls, data: dict, promocodes:list[str], market:Market|None=None):
        total_price = 0
        for product_item in data["products"]:
            product = await ProductService.get_by_id(product_item.pop("product_id"), market=market)
            if not product:
                raise NotFoundException(8)
            if not product.variants[product_item["variant_idx"]]:
                raise SpecialException("variant not found")
            variant_idx = product_item['variant_idx']
            product.variants = {variant_idx:product.variants[variant_idx]}
            if product.variants[variant_idx].is_storage_countable:
                if product.translate_content:
                    name = product.translate_content[0].content.name
                else:
                    name = f"product with id {product.id}"
                if product_item['quantity'] > product.variants[variant_idx].quantity_in_storage:
                    raise HTTPException(status.HTTP_200_OK, f'1208992 {name} {product.variants[variant_idx].quantity_in_storage}')
            product_item['purchase_price'] = product.price
            if promocodes:
                total_price_data = await cls.process_promocodes(promocodes, product)
                product_item['purchase_price'] = total_price_data["total_price"]
            product_item['purchase_price']-= product.price * product.product_discount/100
            product_item['purchase_price'] *= product_item['quantity'] 
            total_price += product_item['purchase_price']
            product_item['product'] = product.model_dump()
        data['total_price'] = total_price
        return data

    @classmethod
    async def create(cls, user:User ,data: dict, promocodes:list[str],market:Market|None=None) -> Order:
        user_data = data.get("customer")
        if not user_data:
            data["customer"] = Customer(**user.model_dump()).model_dump()
        products_total_quantity = 0
        total_price = 0
        total_cost_price = 0 
        not_reusable_promocodes:set[str] = set()
        for product_item in data["products"]:
            product = await ProductService.get_by_id(product_item.pop("product_id"))
            if not product:
                raise NotFoundException(8)
            if not product.variants[product_item["variant_idx"]]:
                raise SpecialException("index out of range")
            variant_idx = product_item['variant_idx']
            product.variants = {variant_idx:product.variants[variant_idx]}
            if product.variants[variant_idx].is_storage_countable:
                if product.translate_content:
                    name = product.translate_content[0].content.name
                else:
                    name = f"product with id {product.id}"
                if product_item['quantity'] > product.variants[variant_idx].quantity_in_storage:
                    raise HTTPException(status.HTTP_200_OK, f'1208992 {name} {product.variants[variant_idx].quantity_in_storage}')
                reserved = product.variants[variant_idx].reserved + product_item['quantity']
                quantity_in_storage = product.variants[variant_idx].quantity_in_storage-product_item['quantity']
                await ProductService.update(
                    product.id,
                    {f"variants.{variant_idx}.reserved":reserved,
                    f"variants.{variant_idx}.quantity_in_storage":quantity_in_storage})
            product.variants[variant_idx].reserved = reserved
            product.variants[variant_idx].quantity_in_storage = quantity_in_storage
            product_item['purchase_price'] = product.price
            if promocodes:
                total_price_and_promocodes = await cls.process_promocodes(promocodes, product)
                product.purchase_price = total_price_and_promocodes["total_price"]
                data['promocodes'].update(total_price_and_promocodes["not_reusable_promocodes"] + total_price_and_promocodes["reusable_promocodes"])
                not_reusable_promocodes.update(total_price_and_promocodes["not_reusable_promocodes"])
            product_item['purchase_price']-= product.price * product.product_discount/100
            product_item['purchase_price'] *= product_item['quantity'] 
            total_cost_price += product.cost_price * product_item['quantity']
            total_price += product_item['purchase_price']
            products_total_quantity += product_item['quantity']
            product_item['product'] = product.model_dump()
        data['status'] = OrderStatus.PENDING
        data['total_price'] = total_price
        data['total_gross_profit'] = total_price-total_cost_price
        data['products_total_quantity'] = products_total_quantity
        order = await super().create(data, market=market)
        if not_reusable_promocodes:
            for code in not_reusable_promocodes:
                await PromoCodeService.update(code=code,data={"is_active":False}, market=market)
        return order


    @classmethod
    async def cancel_order(cls,id:str, user:User,market:Market|None=None) -> Order:
        order:Order|None = await cls.get_by_id(id=id, market=market)
        if not order:
            raise NotFoundException(5)
        if user:
            if user.id != order.customer.id and not user.is_staff:
                raise ForbiddenException()
        for order_product in order.products:
            product = await ProductService.get_by_id(id=order_product.product.id, market=market)
            if not product:
                continue
            product_info_idx = max(order_product.product.variants.keys())
            reserved = product.variants[max(order_product.product.variants.keys())].reserved - order_product.quantity
            quantity_in_storage = product.variants[max(order_product.product.variants.keys())].quantity_in_storage + order_product.quantity
            await ProductService.update(id=product.id, update_data={
                f"variants.{product_info_idx}.reserved": reserved,
                f"variants.{product_info_idx}.quantity_in_storage": quantity_in_storage})
        for code in order.promocodes:
            promocode = await PromoCodeService.get_by_code(code=code, market=market)
            if promocode and not promocode.reusable:
                await PromoCodeService.update(code=code, market=market, data={"is_active":True})
        return await cls.update(id=order.id, update_data={"status": OrderStatus.CANCELLED.value}, market=market)


    @classmethod
    async def get_statistic(cls,market:Market|None=None, from_time:datetime|None=None ,to_time:datetime|None=None):
        collection = await cls.get_collection()
        query = {}
        if market:
            query["market.id"] = market.id

        previous_period_completed_query = None

        if from_time:
            query['created_at'] = {'$gt': from_time}
            if not to_time:
                to_time = datetime.today()
            previous_period_completed_query = {
                'created_at':
                    {'$gt': from_time-(to_time-from_time),
                    '$lt': from_time},
                'status':OrderStatus.COMPLETED.value
                }
            previous_period_orders_pipeline = await cls.get_orders_total_income(
                previous_period_completed_query,
                collection=collection)
        if to_time:
            if 'created_at' in query:
                query['created_at']['$lt'] = to_time
            else:
                query['created_at'] = {'$lt': to_time}

        pending_query = query.copy()      
        completed_query = query.copy()
        cancelled_query = query.copy()

        pending_query['status'] = OrderStatus.PENDING.value
        completed_query['status'] = OrderStatus.COMPLETED.value
        cancelled_query['status'] = OrderStatus.CANCELLED.value

        completed_orders_pipeline = await cls.get_orders_total_income(completed_query,collection=collection)
        pending_orders_pipeline = await cls.get_orders_total_income({"status":OrderStatus.PENDING.value},collection=collection)
        total_income = 0
        total_gross_profit = 0
        income_in_processing = 0
        gross_profit_in_processing = 0
        income_increase_percentage = None
        gross_profit_increase_percentage = None
        if completed_orders_pipeline:
            total_income = completed_orders_pipeline['total_income'] 
            total_gross_profit = completed_query['total_gross_profit']
            if previous_period_orders_pipeline:
                previous_period_income = previous_period_orders_pipeline['total_income']
                previous_period_gross_profit = previous_period_orders_pipeline['total_gross_profit']
                income_increase_percentage = (total_income-previous_period_income)/previous_period_income*100
                gross_profit_increase_percentage = (total_income-previous_period_gross_profit)/previous_period_gross_profit*100
        if pending_orders_pipeline:
            income_in_processing = pending_orders_pipeline['total_income']
            gross_profit_in_processing = pending_orders_pipeline['total_gross_profit']

        total_orders = await collection.count_documents(query)
        pending = await collection.count_documents({"status":OrderStatus.PENDING.value})
        completed = await collection.count_documents(completed_query)
        cancelled = await collection.count_documents(cancelled_query)
        
        return {
            "income_increase_percentage": income_increase_percentage,
            "gross_profit_increase_percentage":gross_profit_increase_percentage,
            "average_order_price":total_income/total_orders,
            "cancelled_orders": cancelled,
            "total_income": total_income,
            "total_gross_profit": total_gross_profit,
            "income_in_processing": income_in_processing,
            "gross_profit_in_processing": gross_profit_in_processing,
            "total_orders": total_orders,
            "pending_orders": pending,
            "completed_orders": completed
        }


    @classmethod
    async def get_orders_total_income(cls,filter_query:dict,collection):
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": None, 
                "total_income": {"$sum": "$total_price"},
                "total_gross_profit": {"$sum": "$total_gross_profit"}}}
        ]
        async for result in collection.aggregate(pipeline):
            if result:
                return result

    
    @classmethod
    async def get_total_sales_statistic(cls, market: Market | None = None, from_time: datetime | None = None, to_time: datetime | None = None):
        collection = await cls.get_collection()
        query: dict[Any, Any] = {
            "date": {
                "$gte": from_time,
                "$lt": to_time
            }
        }
        if market:
            query['market.id'] = market.id
        pipeline = [
            {"$addFields": {"date": {"$toDate": "$created_at"}}},
            {"$match": query},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date"},
                    "month": {"$month": "$date"},
                    "week": {"$week": "$date"},
                    "dayOfWeek": {"$dayOfWeek": "$date"},
                    "hour": {"$hour": "$date"}
                },
                "sales": {"$sum": "$products_total_quantity"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.week": 1, "_id.dayOfWeek": 1, "_id.hour": 1}},
            {"$addFields": {"name": {"$concat": [{"$toString": "$_id.hour"}, ":00"]}}},
            {"$group": {
                "_id": {"year": "$_id.year", "month": "$_id.month", "week": "$_id.week", "dayOfWeek": "$_id.dayOfWeek"},
                "hours": {"$push": {"name": "$name", "sales": "$sales"}}
            }},
            {"$group": {
                "_id": {"year": "$_id.year", "month": "$_id.month", "week": "$_id.week"},
                "daysOfWeek": {"$push": {"dayOfWeek": {"$arrayElemAt": [["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "$_id.dayOfWeek"]}, "hours": "$hours"}}
            }},
            {"$group": {
                "_id": {"year": "$_id.year", "month": "$_id.month"},
                "weeks": {"$push": {"week": {"$concat": ["Week ", {"$toString": "$_id.week"}]}, "daysOfWeek": "$daysOfWeek"}}
            }},
            {"$group": {
                "_id": {"year": "$_id.year"},
                "months": {"$push": {"month": {"$arrayElemAt": [["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "$_id.month"]}, "weeks": "$weeks"}}
            }},
            {"$sort": {"_id.year": 1}},
            {"$addFields": {"year": {"$toString": "$_id.year"}}},
            {"$project": {"_id": 0}}
        ]
        async for result in collection.aggregate(pipeline):
            if result:
                return result


    @classmethod
    async def get_frequently_ordered_products(cls, from_time:datetime|None=None ,to_time:datetime|None=None,market:Market|None=None):
        collection = await cls.get_collection()
        time_filter = {}
        if from_time:
            time_filter['$gte'] = from_time
        if to_time:
            time_filter['$lte'] = to_time

        match_stage:dict[Any,Any] = {
            '$match': {
                'created_at': time_filter}
        }

        if market:
            match_stage['$match']['market.id'] = market.id

        pipeline = [
            {'$unwind': '$products'},
            match_stage,
            {'$group': {'_id': '$products.product.id', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1, '_id': -1}},
            {'$project': {'_id': 0, 'product_id': '$_id', 'count': 1}}
        ]
        
        result = []
        async for document in collection.aggregate(pipeline):
            result.append(document)
        return result


    @classmethod
    async def get_product_in_orders(cls, product_id:str,from_time:datetime|None=None ,to_time:datetime|None=None,market:Market|None=None):
        collection = await cls.get_collection()
        time_filter = {}
        if from_time:
            time_filter['$gte'] = from_time
        if to_time:
            time_filter['$lte'] = to_time

        match_stage = {
            '$match': {
                'products.product.id': product_id,
                'created_at': time_filter}
        }

        if market:
            match_stage['$match']['market.id'] = market.id 
            
        pipeline = [
            {'$unwind': '$products'},
            match_stage,
            {'$addFields': {'_id': {'$toString': '$_id'}}},
            {'$replaceRoot': {'newRoot': '$products'}}
        ]

        result = []
        async for document in collection.aggregate(pipeline):
            result.append(document)

        return result

    @classmethod
    async def get_product_statistics(cls, product_id,from_time:datetime|None=None ,to_time:datetime|None=None,market:Market|None=None):
        products = await cls.get_product_in_orders(product_id=product_id,from_time=from_time,to_time=to_time,market=market)
        result = {
            "total_income":0,
            "total_order":0,
            "total_sale":0,
        }
        for product in products:
            result['total_income'] += product['purchase_price']
            result['total_order'] += 1
            result['total_sale'] += product['quantity']

        return result