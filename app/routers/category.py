from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.helpers.response import error_response, success_response
from app.models import category as models
from app.schemas import category as schemas

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Check if category already exists
    if db.query(models.Category).filter(models.Category.name == category.name).first():
        return error_response(
            message="Category already exists",
            code=400
        )
    new_category = models.Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    category_data = {
        "id": new_category.id,
        "name": new_category.name
    }
    return success_response(data=category_data)


@router.get("/")
def get_categories(
    db: Session = Depends(get_db),
    name: str = Query(None, description="Name to search for")
) -> Dict[str, Any]:
    datas = models.Category
    query = db.query(datas.id, datas.name)
    if name:
        query = query.filter(datas.name.ilike(f"%{name}%"))
    categories = query.all()
    categories_data = [
        {
            "id": category.id,
            "name": category.name
        }
        for category in categories
    ]
    if not categories_data:
        return error_response("Error: No categories found")
    return success_response(data=categories_data)


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        return error_response(
            message="Category not found",
            code=404
        )
    # Format category data
    category_data = {
        "id": category.id,
        "name": category.name
    }
    return success_response(data=category_data)


@router.get("/paginated/")
def get_categories_paginated(
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    offset = (page - 1) * per_page
    total = db.query(models.Category).count()
    categories = db.query(models.Category).offset(offset).limit(per_page).all()
    categories_data = [
        {"id": category.id, "name": category.name}
        for category in categories
    ]
    from helpers.response import paginated_response
    return paginated_response(
        data=categories_data,
        total=total,
        page=page,
        per_page=per_page,
        message="Categories retrieved successfully"
    )
