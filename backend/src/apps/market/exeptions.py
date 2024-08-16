from fastapi import HTTPException, status

class MarketNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail=f"1101"
        )