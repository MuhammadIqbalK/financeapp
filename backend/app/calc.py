import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Account, Transaction, Transfer


def account_balance_expr(account_id: uuid.UUID):
    """Initial + income - expense + transfer in - transfer out."""
    income = (
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.account_id == account_id, Transaction.type == "income")
        .scalar_subquery()
    )
    expense = (
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.account_id == account_id, Transaction.type == "expense")
        .scalar_subquery()
    )
    transfer_in = (
        select(func.coalesce(func.sum(Transfer.amount), 0))
        .where(Transfer.to_account_id == account_id)
        .scalar_subquery()
    )
    transfer_out = (
        select(func.coalesce(func.sum(Transfer.amount), 0))
        .where(Transfer.from_account_id == account_id)
        .scalar_subquery()
    )
    return Account.initial_balance + income - expense + transfer_in - transfer_out


def compute_account_balances(db: Session, user_id: uuid.UUID) -> dict[uuid.UUID, float]:
    rows = db.execute(
        select(Account.id, account_balance_expr(Account.id)).where(Account.user_id == user_id)
    ).all()
    return {row[0]: float(row[1]) for row in rows}


def total_balance(db: Session, user_id: uuid.UUID) -> float:
    return float(sum(compute_account_balances(db, user_id).values()))


def resolve_period(period: str, start: date | None, end: date | None) -> tuple[date, date]:
    today = datetime.now(UTC).date()
    if period == "today":
        return today, today
    if period == "week":
        start_week = today - timedelta(days=today.weekday())
        return start_week, today
    if period == "custom":
        if start is None or end is None:
            raise ValueError("start and end required for custom period")
        if start > end:
            raise ValueError("start must be before end")
        return start, end
    # default: month
    return today.replace(day=1), today


def period_totals(db: Session, user_id: uuid.UUID, start: date, end: date) -> tuple[float, float]:
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


def daily_series(db: Session, user_id: uuid.UUID, start: date, end: date) -> list[dict]:
    rows = db.execute(
        select(
            Transaction.transaction_date,
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end,
        )
        .group_by(Transaction.transaction_date, Transaction.type)
        .order_by(Transaction.transaction_date)
    ).all()
    series: dict[date, dict] = {}
    current = start
    while current <= end:
        series[current] = {"label": current.isoformat(), "income": 0.0, "expense": 0.0}
        current += timedelta(days=1)
    for tx_date, tx_type, amount in rows:
        if tx_date in series:
            series[tx_date]["income" if tx_type == "income" else "expense"] = float(amount)
    # cap chart points for long ranges
    points = list(series.values())
    if len(points) > 31:
        step = len(points) // 30 + 1
        points = points[::step]
    return points
