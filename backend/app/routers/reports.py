from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Category, Transaction, User
from ..schemas import CategoryShare, SummaryOut, TrendPoint

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year, 12, 31)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def _totals(db: Session, user_id, start: date, end: date) -> tuple[float, float]:
    income = float(
        db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
        )
    )
    expense = float(
        db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
        )
    )
    return income, expense


@router.get("/summary", response_model=SummaryOut)
def summary(
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    year = year or today.year
    month = month or today.month
    start, end = _month_bounds(year, month)
    income, expense = _totals(db, user.id, start, end)
    return SummaryOut(year=year, month=month, income=income, expenses=expense, net=income - expense)


@router.get("/expense-breakdown", response_model=list[CategoryShare])
def expense_breakdown(
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    year = year or today.year
    month = month or today.month
    start, end = _month_bounds(year, month)
    rows = db.execute(
        select(
            Transaction.category_id,
            Category.name,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .join(Category, Category.id == Transaction.category_id)
        .where(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end,
        )
        .group_by(Transaction.category_id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    total = sum(float(r[2]) for r in rows)
    return [
        CategoryShare(
            category_id=r[0],
            category_name=r[1],
            amount=float(r[2]),
            percent=round(float(r[2]) / total * 100, 1) if total else 0.0,
        )
        for r in rows
    ]


@router.get("/trend", response_model=list[TrendPoint])
def trend(
    months: int = Query(default=6, ge=1, le=24),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    points: list[TrendPoint] = []
    year, month = today.year, today.month
    for _ in range(months):
        start, end = _month_bounds(year, month)
        income, expense = _totals(db, user.id, start, end)
        points.append(TrendPoint(year=year, month=month, income=income, expense=expense))
        if month == 1:
            year, month = year - 1, 12
        else:
            month -= 1
    points.reverse()
    return points
