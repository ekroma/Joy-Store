from apps.base import BaseDAO, NotFoundException
from .model import Chat, ChatStatus
from apps.market.model import Market
from apps.user_management.user import User, UserService
from datetime import datetime


class ChatService(BaseDAO[Chat]):
    model = Chat

    @classmethod
    async def create_chat(cls,client_id:str,status:ChatStatus ,market:Market|None=None) -> Chat:
        client = await UserService.get_by_id(client_id, market=market)
        data = {"status":status, "client":client}
        return await super().create(data=data, market=market)

    @classmethod
    async def get_chat_by_client_id_or_create(cls,client_id:str,market:Market|None=None) -> Chat:
        collection = await cls.get_collection()
        chat = await collection.find_one({"client.id": client_id})
        if not chat:
            return await cls.create_chat(client_id=client_id,status=ChatStatus.SUPPORT_CHAT, market=market)
        return Chat(**chat) #type:ignore

    @classmethod
    async def get_client_chats(cls,page:int=1, page_size:int=10,market:Market|None=None):
        return await cls.get_all(page=page,page_size=page_size, market=market)
    
    @classmethod
    async def create_support_message(cls,text:str,client_id:str,current_user_id:str,market:Market|None=None) -> Chat:
        chat = await cls.get_chat_by_client_id_or_create(client_id=client_id, market=market)
        message = {"text": text, "user_id": current_user_id, "created_at":datetime.utcnow()}
        chat = await cls.add_items_to_set(id=chat.id, field="messages", items=[message])
        return chat