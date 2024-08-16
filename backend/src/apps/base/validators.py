from bson import ObjectId
from bson.errors import InvalidId

from .exception import InvalidObjectIdException


def validate_object_id(name: str):
    try:
        object_id = ObjectId(name)
    except InvalidId as e:
        raise InvalidObjectIdException()
    return object_id