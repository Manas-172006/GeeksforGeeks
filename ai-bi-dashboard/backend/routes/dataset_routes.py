from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import User
from backend.schemas import DatasetCreate, Dataset as DatasetSchema
from backend.auth import get_current_user
from backend.services.dataset_service import save_dataset, get_datasets_for_user

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

@router.post("/upload-dataset", response_model=DatasetSchema)
def upload_dataset(
    dataset: DatasetCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return save_dataset(db, dataset, current_user.id)

@router.get("", response_model=List[DatasetSchema])
def get_datasets(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return get_datasets_for_user(db, current_user.id)
