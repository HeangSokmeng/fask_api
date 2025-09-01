

# ---------------- Updated Category Routes ----------------
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.helpers.response import (error_response, paginated_response,
                                  success_response)
from app.models import category as models
from app.schemas import category as schemas

router = APIRouter(prefix="/categories", tags=["Categories"])


# Option 1: Using middleware (current approach)
@router.post("/")
def create_category(
    request: Request,
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category. Protected route."""
    try:
        current_user = request.state.user
    except AttributeError:
        return error_response(message="Authentication required", code=401)

    # Check if category already exists
    existing_category = db.query(models.Category).filter(
        models.Category.name == category.name
    ).first()
    
    if existing_category:
        return error_response(message="Category already exists", code=400)

    # Create new category
    new_category = models.Category(**category.dict())
    new_category.created_by = current_user.id

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return success_response(
        data={
            "id": new_category.id, 
            "name": new_category.name, 
            "created_by": new_category.created_by
        }
    )



@router.get("/")
async def get_categories(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Query(None, description="Name to search for")
):
    """Get all categories with optional name filter."""
    try:
        current_user = request.state.user
    except AttributeError:
        return error_response(message="Authentication required", code=401)

    query = db.query(models.Category)
    if name:
        query = query.filter(models.Category.name.ilike(f"%{name}%"))
    
    categories = query.all()

    if not categories:
        return success_response(data=[], message="No categories found")

    categories_data = [
        {"id": cat.id, "name": cat.name, "created_by": cat.created_by}
        for cat in categories
    ]
    
    return success_response(data=categories_data)


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get single category by ID."""
    try:
        current_user = request.state.user
    except AttributeError:
        return error_response(message="Authentication required", code=401)

    category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    
    if not category:
        return error_response(message="Category not found", code=404)

    return success_response(
        data={"id": category.id, "name": category.name, "created_by": category.created_by}
    )