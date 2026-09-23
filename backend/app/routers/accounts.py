import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..calc import account_balance_expr, compute_account_balances
from ..database import get_db
from ..deps import get_current_user
from ..models import Account, Transaction, Transfer, User
from ..schemas import AccountIn, AccountOut, AccountUpdate

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


def _get_account(db: Session, user: User, account_id: uuid.UUID) -> Account:
    account = db.scalar(select(Account).where(Account.id == account_id, Account.user_id == user.id))
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.get("", response_model=list[AccountOut])
def list_accounts(
    include_inactive: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Account).where(Account.user_id == user.id)
    if not include_inactive:
        query = query.where(Account.is_active.is_(True))
    accounts = db.scalars(query.order_by(Account.created_at)).all()
    balances = compute_account_balances(db, user.id)
    return [
        AccountOut.model_validate(a).model_copy(update={"balance": balances.get(a.id, 0.0)})
        for a in accounts
    ]


@router.post("", response_model=AccountOut, status_code=201)
def create_account(
    data: AccountIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = Account(user_id=user.id, **data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return AccountOut.model_validate(account).model_copy(
        update={"balance": float(account.initial_balance)}
    )


@router.get("/{account_id}", response_model=AccountOut)
def get_account(
    account_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = _get_account(db, user, account_id)
    balance = db.scalar(select(account_balance_expr(account.id)))
    return AccountOut.model_validate(account).model_copy(update={"balance": float(balance)})


@router.put("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: uuid.UUID,
    data: AccountUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = _get_account(db, user, account_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    balances = compute_account_balances(db, user.id)
    return AccountOut.model_validate(account).model_copy(
        update={"balance": balances.get(account.id, 0.0)}
    )


@router.delete("/{account_id}", status_code=200)
def delete_account(
    account_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = _get_account(db, user, account_id)
    tx_count = db.scalar(
        select(func.count()).select_from(Transaction).where(Transaction.account_id == account.id)
    )
    transfer_count = db.scalar(
        select(func.count())
        .select_from(Transfer)
        .where((Transfer.from_account_id == account.id) | (Transfer.to_account_id == account.id))
    )
    if (tx_count or 0) + (transfer_count or 0) > 0:
        account.is_active = False
        db.commit()
        return {"detail": "Account has history and was deactivated"}
    db.delete(account)
    db.commit()
    return {"detail": "Account deleted"}
