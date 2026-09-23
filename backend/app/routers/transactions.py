import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_user
from ..models import Account, Category, Transaction, User
from ..schemas import TransactionIn, TransactionOut, TransactionUpdate

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _to_out(tx: Transaction) -> TransactionOut:
    out = TransactionOut.model_validate(tx)
    return out.model_copy(
        update={
            "category_name": tx.category.name if tx.category else "",
            "account_name": tx.account.name if tx.account else "",
        }
    )


def _validate(
    db: Session, user: User, account_id: uuid.UUID, category_id: uuid.UUID, tx_type: str
) -> None:
    account = db.scalar(select(Account).where(Account.id == account_id, Account.user_id == user.id))
    if account is None:
        raise HTTPException(status_code=400, detail="Invalid account")
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user.id)
    )
    if category is None:
        raise HTTPException(status_code=400, detail="Invalid category")
    if category.type != tx_type:
        raise HTTPException(status_code=400, detail=f"Category type must be {tx_type}")


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    q: str | None = None,
    type: str | None = Query(default=None, pattern="^(income|expense)$"),
    category_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(Transaction)
        .options(joinedload(Transaction.category), joinedload(Transaction.account))
        .where(Transaction.user_id == user.id)
    )
    if q:
        query = query.where(Transaction.description.ilike(f"%{q}%"))
    if type:
        query = query.where(Transaction.type == type)
    if category_id:
        query = query.where(Transaction.category_id == category_id)
    if account_id:
        query = query.where(Transaction.account_id == account_id)
    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)
    rows = db.scalars(
        query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [_to_out(tx) for tx in rows]


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    data: TransactionIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _validate(db, user, data.account_id, data.category_id, data.type)
    tx = Transaction(user_id=user.id, **data.model_dump())
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return _to_out(tx)


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tx = db.scalar(
        select(Transaction)
        .options(joinedload(Transaction.category), joinedload(Transaction.account))
        .where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _to_out(tx)


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: uuid.UUID,
    data: TransactionUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tx = db.scalar(
        select(Transaction)
        .options(joinedload(Transaction.category), joinedload(Transaction.account))
        .where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    updates = data.model_dump(exclude_unset=True)
    account_id = updates.get("account_id", tx.account_id)
    category_id = updates.get("category_id", tx.category_id)
    tx_type = updates.get("type", tx.type)
    _validate(db, user, account_id, category_id, tx_type)
    for key, value in updates.items():
        setattr(tx, key, value)
    db.commit()
    db.refresh(tx)
    return _to_out(tx)


@router.delete("/{transaction_id}", status_code=200)
def delete_transaction(
    transaction_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tx = db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return {"detail": "Transaction deleted"}
