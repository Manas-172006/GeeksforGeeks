from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class DatasetBase(BaseModel):
    dataset_name: str
    file_path: str

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: int
    user_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

class QueryBase(BaseModel):
    dataset_id: int
    query_text: str
    llm_response: str

class QueryCreate(QueryBase):
    pass

class Query(QueryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChartBase(BaseModel):
    dataset_id: int
    chart_config_json: str

class ChartCreate(ChartBase):
    pass

class Chart(ChartBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
