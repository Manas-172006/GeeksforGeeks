from sqlalchemy.orm import Session
from backend.models import Query
from backend.schemas import QueryCreate

def save_query(db: Session, query: QueryCreate, user_id: int):
    new_query = Query(
        query_text=query.query_text,
        llm_response=query.llm_response,
        dataset_id=query.dataset_id,
        user_id=user_id
    )
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    return new_query

def get_queries_for_user(db: Session, user_id: int):
    return db.query(Query).filter(Query.user_id == user_id).order_by(Query.created_at.desc()).all()
