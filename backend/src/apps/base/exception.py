from fastapi import HTTPException, status
from typing import Any

class InvalidObjectIdException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail=f"1200"
        )

class InvalidDataException(HTTPException):
    def __init__(self, num:int|None=None):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail=f"120{num if num is not None else ''}")

class SpecialException(HTTPException):
    def __init__(self, data:Any=None):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail=f"120 {data if data is not None else ''}")

class FeatureAccessException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail="13012")

class NotFoundException(HTTPException):
    def __init__(self, num:int|None=None):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail=f"110{num if num is not None else ''}")

class ForbiddenException(HTTPException):
    def __init__(self, num:int|None=None):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail=f"130{num if num is not None else ''}")

class AlreadyExistException(HTTPException):
    def __init__(self, num:int|None=None):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail=f"140{num if num is not None else ''}")

class InvalidExtensionException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_200_OK,
                        detail=f"12099")

class ServerError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"150"
        )