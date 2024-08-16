from fastapi import HTTPException, status


class NotFoundCategoryException(HTTPException):
    def __init__(self,category_id: str):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail=f"1103 {category_id}"
        )