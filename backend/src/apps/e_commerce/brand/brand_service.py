from apps.base import BaseDAO
from .model import Brand

class BrandService(BaseDAO[Brand]):
    model = Brand