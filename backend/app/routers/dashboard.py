from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..calc import daily_series, period_totals, resolve_period, total_balance
from ..database import get_db
from ..deps import get_current_user
from ..models import Budget, Category, Transaction, User
from ..schemas import (
    BudgetOut,
    CategoryShare,
    DashboardOut,
    Period,
    Point,
    TransactionOut,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _month_end(year: int, month: int) -> date:
    if month == 12:
        return date(year, 12, 31)
    return date(year, month + 1, 1) - timedelta(days=1)


def _budget_progress(db: Session, user: User, year: int, month: int) -> list[BudgetOut]:
    rows = db.scalars(
        select(Budget)
        .options(joinedload(Budget.category))
        .where(Budget.user_id == user.id, Budget.month == month, Budget.year == year)
    ).all()
    start = date(year, month, 1)
    end = _month_end(year, month)
    result = []
    for b in sorted(rows, key=lambda x: (x.category.name if x.category else "").lower()):
        spent = float(
            db.scalar(
                select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                    Transaction.user_id == user.id,
                    Transaction.category_id == b.category_id,
                    Transaction.type == "expense",
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date <= end,
                )
            )
        )
        amount = float(b.amount)
        out = BudgetOut.model_validate(b).model_copy(
            update={
                "category_name": b.category.name if b.category else "",
                "spent": spent,
                "remaining": amount - spent,
                "usage_percent": round((spent / amount * 100) if amount > 0 else 0.0, 1),
            }
        )
        result.append(out)
    return result


@router.get("", response_model=DashboardOut)
def dashboard(
    period: str = Query(default="month", pattern="^(today|week|month|custom)$"),
    start: date | None = None,
    end: date | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        p_start, p_end = resolve_period(period, start, end)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    balance = total_balance(db, user.id)
    income, expense = period_totals(db, user.id, p_start, p_end)
    series = daily_series(db, user.id, p_start, p_end)

    breakdown_rows = db.execute(
        select(
            Transaction.category_id,
            Category.name,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .join(Category, Category.id == Transaction.category_id)
        .where(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            Transaction.transaction_date >= p_start,
            Transaction.transaction_date <= p_end,
        )
        .group_by(Transaction.category_id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    total_exp = sum(float(r[2]) for r in breakdown_rows)
    expense_by_category = [
        CategoryShare(
            category_id=r[0],
            category_name=r[1],
            amount=float(r[2]),
            percent=round(float(r[2]) / total_exp * 100, 1) if total_exp > 0 else 0.0,
        )
        for r in breakdown_rows
    ]

    recent = db.scalars(
        select(Transaction)
        .options(joinedload(Transaction.category), joinedload(Transaction.account))
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .limit(8)
    ).all()
    recent_out = [
        TransactionOut.model_validate(tx).model_copy(
            update={"category_name": tx.category.name, "account_name": tx.account.name}
        )
        for tx in recent
    ]

    today = date.today()
    budgets = _budget_progress(db, user, today.year, today.month)

    return DashboardOut(
        period=Period(start=p_start, end=p_end),
        balance=balance,
        income=income,
        expenses=expense,
        savings=income - expense,
        income_vs_expense=[Point(**p) for p in series],
        expense_by_category=expense_by_category,
        recent_transactions=recent_out,
        budgets=budgets,
    )
