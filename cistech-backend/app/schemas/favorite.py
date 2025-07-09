from datetime import datetime
from pydantic import BaseModel

# Shared fields
class FavoriteBase(BaseModel):
    product_id: int

# Incoming POST payload
class FavoriteCreate(FavoriteBase):
    pass

# What lives in the database (read)  
class FavoriteInDBBase(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# What you return over the wire  
# class FavoriteOut(FavoriteInDBBase):
#     # optional: nest a Product preview schema
#     # product: ProductResponse
#     ...
