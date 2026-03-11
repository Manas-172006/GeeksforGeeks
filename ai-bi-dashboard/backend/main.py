from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routes import auth_routes, dataset_routes, query_routes, chart_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI BI Dashboard API",
    description="Backend API for the AI-powered Business Intelligence Dashboard.",
    version="1.0.0"
)

# Configure CORS so Streamlit can talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the Streamlit app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_routes.router)
app.include_router(dataset_routes.router)
app.include_router(query_routes.router)
app.include_router(chart_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI BI Dashboard API"}
