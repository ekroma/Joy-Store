from fastapi import HTTPException, status

class NotFoundSubcategoryException(HTTPException):
    def __init__(self, subcategory_id: str):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail=f"1104 {subcategory_id}"
        )
