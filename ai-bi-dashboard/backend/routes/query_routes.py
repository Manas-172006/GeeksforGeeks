from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User
from backend.schemas import QueryCreate, Query as QuerySchema
from backend.auth import get_current_user
from backend.services.query_service import save_query, get_queries_for_user

router = APIRouter(prefix="/api/query", tags=["Queries"])

@router.post("", response_model=QuerySchema)
def create_query(
    query: QueryCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return save_query(db, query, current_user.id)

@router.get("-history", response_model=List[QuerySchema])
def query_history(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return get_queries_for_user(db, current_user.id)
