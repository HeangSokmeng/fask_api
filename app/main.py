from fastapi import FastAPI

from app.database import Base, engine
from app.middleware.auth import auth_middleware
from app.routers import auth, category

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Category API")

# Public routes
app.include_router(auth.router)

# Protected routes
app.include_router(category.router)

# Middleware applied to all routes
app.middleware("http")(auth_middleware)
