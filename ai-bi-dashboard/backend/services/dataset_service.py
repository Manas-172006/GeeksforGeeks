from sqlalchemy.orm import Session
from backend.models import Dataset
from backend.schemas import DatasetCreate

def save_dataset(db: Session, dataset: DatasetCreate, user_id: int):
    new_dataset = Dataset(
        dataset_name=dataset.dataset_name,
        file_path=dataset.file_path,
        user_id=user_id
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    return new_dataset

def get_datasets_for_user(db: Session, user_id: int):
    return db.query(Dataset).filter(Dataset.user_id == user_id).order_by(Dataset.uploaded_at.desc()).all()
