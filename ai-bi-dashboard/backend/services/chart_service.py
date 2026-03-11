from sqlalchemy.orm import Session
from backend.models import Chart
from backend.schemas import ChartCreate

def save_chart(db: Session, chart: ChartCreate, user_id: int):
    new_chart = Chart(
        chart_config_json=chart.chart_config_json,
        dataset_id=chart.dataset_id,
        user_id=user_id
    )
    db.add(new_chart)
    db.commit()
    db.refresh(new_chart)
    return new_chart

def get_charts_for_user(db: Session, user_id: int):
    return db.query(Chart).filter(Chart.user_id == user_id).order_by(Chart.created_at.desc()).all()
