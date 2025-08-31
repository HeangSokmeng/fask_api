from fastapi import FastAPI

from app.database import Base, engine
from app.routers import category

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Category API")

# Register routers
app.include_router(category.router)
