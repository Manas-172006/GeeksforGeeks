from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User
from backend.schemas import ChartCreate, Chart as ChartSchema
from backend.auth import get_current_user
from backend.services.chart_service import save_chart, get_charts_for_user

router = APIRouter(prefix="/api/charts", tags=["Charts"])

@router.post("/save-chart", response_model=ChartSchema)
def create_chart(
    chart: ChartCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return save_chart(db, chart, current_user.id)

@router.get("", response_model=List[ChartSchema])
def get_charts(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return get_charts_for_user(db, current_user.id)
