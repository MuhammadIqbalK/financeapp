import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_user
from ..models import Budget, Category, Transaction, User
from ..schemas import BudgetIn, BudgetOut, BudgetUpdate

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


def _spent(db: Session, user_id: uuid.UUID, category_id: uuid.UUID, month: int, year: int) -> float:
    start = date(year, month, 1)
    if month == 12:
        end = date(year, 12, 31)
    else:
        end = date(year, month + 1, 1).fromordinal(date(year, month + 1, 1).toordinal() - 1)
    return float(
        db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.category_id == category_id,
                Transaction.type == "expense",
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
        )
    )


def _to_out(db: Session, user: User, budget: Budget) -> BudgetOut:
    out = BudgetOut.model_validate(budget)
    spent = _spent(db, user.id, budget.category_id, budget.month, budget.year)
    remaining = float(budget.amount) - spent
    usage = (spent / float(budget.amount) * 100) if float(budget.amount) > 0 else 0.0
    return out.model_copy(
        update={
            "category_name": budget.category.name if budget.category else "",
            "spent": spent,
            "remaining": remaining,
            "usage_percent": round(usage, 1),
        }
    )


@router.get("", response_model=list[BudgetOut])
def list_budgets(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    month = month or today.month
    year = year or today.year
    rows = db.scalars(
        select(Budget)
        .options(joinedload(Budget.category))
        .where(Budget.user_id == user.id, Budget.month == month, Budget.year == year)
    ).all()
    rows = sorted(rows, key=lambda b: (b.category.name if b.category else "").lower())
    return [_to_out(db, user, b) for b in rows]


@router.post("", response_model=BudgetOut, status_code=201)
def create_budget(
    data: BudgetIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    category = db.scalar(
        select(Category).where(Category.id == data.category_id, Category.user_id == user.id)
    )
    if category is None:
        raise HTTPException(status_code=400, detail="Invalid category")
    if category.type != "expense":
        raise HTTPException(status_code=400, detail="Budgets are only for expense categories")
    existing = db.scalar(
        select(Budget).where(
            Budget.user_id == user.id,
            Budget.category_id == data.category_id,
            Budget.month == data.month,
            Budget.year == data.year,
        )
    )
    if existing:
        existing.amount = data.amount
        db.commit()
        db.refresh(existing)
        return _to_out(db, user, existing)
    budget = Budget(user_id=user.id, **data.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _to_out(db, user, budget)


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: uuid.UUID,
    data: BudgetUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = db.scalar(
        select(Budget)
        .options(joinedload(Budget.category))
        .where(Budget.id == budget_id, Budget.user_id == user.id)
    )
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    updates = data.model_dump(exclude_unset=True)
    if "category_id" in updates:
        category = db.scalar(
            select(Category).where(
                Category.id == updates["category_id"], Category.user_id == user.id
            )
        )
        if category is None:
            raise HTTPException(status_code=400, detail="Invalid category")
    for key, value in updates.items():
        setattr(budget, key, value)
    db.commit()
    db.refresh(budget)
    return _to_out(db, user, budget)


@router.delete("/{budget_id}", status_code=200)
def delete_budget(
    budget_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == user.id))
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
    return {"detail": "Budget deleted"}
