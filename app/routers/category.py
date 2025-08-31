from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.helpers.response import error_response, success_response

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Check if category already exists
    db_category = db.query(models.Category).filter(models.Category.name == category.name).first()
    if db_category:
        return error_response(
            message="Category already exists",
            code=400
        )
    
    try:
        # Create new category
        new_category = models.Category(**category.dict())
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        # Format response data
        category_data = {
            "id": new_category.id,
            "name": new_category.name
        }
        
        return success_response(
            message="Category created successfully",
            data=category_data,
            code=201
        )
        
    except Exception as e:
        db.rollback()
        return error_response(
            message="Failed to create category",
            code=500
        )


@router.get("/")
def get_categories(db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        categories = db.query(models.Category).all()
        
        # Format categories data
        categories_data = [
            {"id": category.id, "name": category.name}
            for category in categories
        ]
        
        return success_response(
            message="Categories retrieved successfully",
            data=categories_data
        )
        
    except Exception as e:
        return error_response(
            message="Failed to retrieve categories",
            code=500
        )


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
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
        
        return success_response(
            message="Category retrieved successfully",
            data=category_data
        )
        
    except Exception as e:
        return error_response(
            message="Failed to retrieve category",
            code=500
        )


# Example with pagination (if you want to add pagination to get_categories)
@router.get("/paginated/")
def get_categories_paginated(
    page: int = 1, 
    per_page: int = 10, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get total count
        total = db.query(models.Category).count()
        
        # Get paginated categories
        categories = db.query(models.Category).offset(offset).limit(per_page).all()
        
        # Format categories data
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
        
    except Exception as e:
        return error_response(
            message="Failed to retrieve categories",
            code=500
        )