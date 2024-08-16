from pydantic import Field, BaseModel, AliasChoices
from pydantic.functional_validators import BeforeValidator
from typing import Annotated

from apps.newsletters.messages import Messages, ChatStatus

PyObjectId = Annotated[str, BeforeValidator(str)]


class ChatRead(BaseModel):
    status: ChatStatus = ChatStatus.SUPPORT_CHAT
    messages: list[Messages]
    client_id: str

