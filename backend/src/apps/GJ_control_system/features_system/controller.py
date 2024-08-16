from pydantic import BaseModel


class Features(BaseModel):
    user_auth:bool = True
    online_payment:bool = True
    