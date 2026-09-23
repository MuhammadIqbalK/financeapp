import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Budget, Category, Transaction, User
from ..schemas import CategoryIn, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])


def _get_category(db: Session, user: User, category_id: uuid.UUID) -> Category:
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user.id)
    )
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("", response_model=list[CategoryOut])
def list_categories(
    type: str | None = None,
    include_inactive: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Category).where(Category.user_id == user.id)
    if type:
        query = query.where(Category.type == type)
    if not include_inactive:
        query = query.where(Category.is_active.is_(True))
    return db.scalars(query.order_by(Category.type, Category.name)).all()


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    data: CategoryIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exists = db.scalar(
        select(Category).where(
            Category.user_id == user.id,
            Category.name == data.name,
            Category.type == data.type,
        )
    )
    if exists:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(user_id=user.id, **data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = _get_category(db, user, category_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=200)
def delete_category(
    category_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = _get_category(db, user, category_id)
    tx_count = db.scalar(
        select(func.count()).select_from(Transaction).where(Transaction.category_id == category.id)
    )
    budget_count = db.scalar(
        select(func.count()).select_from(Budget).where(Budget.category_id == category.id)
    )
    if (tx_count or 0) + (budget_count or 0) > 0:
        raise HTTPException(status_code=409, detail="Category is in use and cannot be deleted")
    db.delete(category)
    db.commit()
    return {"detail": "Category deleted"}
