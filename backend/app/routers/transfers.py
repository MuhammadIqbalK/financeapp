import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Account, Transfer, User
from ..schemas import TransferIn, TransferOut, TransferUpdate

router = APIRouter(prefix="/api/transfers", tags=["transfers"])


def _validate_accounts(db: Session, user: User, from_id: uuid.UUID, to_id: uuid.UUID) -> None:
    if from_id == to_id:
        raise HTTPException(status_code=400, detail="Source and destination accounts must differ")
    count = db.scalar(
        select(func.count()).where(Account.id.in_([from_id, to_id]), Account.user_id == user.id)
    )
    if count != 2:
        raise HTTPException(status_code=400, detail="Invalid account")


def _to_out(db: Session, transfer: Transfer) -> TransferOut:
    out = TransferOut.model_validate(transfer)
    from_acc = db.get(Account, transfer.from_account_id)
    to_acc = db.get(Account, transfer.to_account_id)
    return out.model_copy(
        update={
            "from_account_name": from_acc.name if from_acc else "",
            "to_account_name": to_acc.name if to_acc else "",
        }
    )


@router.get("", response_model=list[TransferOut])
def list_transfers(
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.scalars(
        select(Transfer)
        .where(Transfer.user_id == user.id)
        .order_by(Transfer.transfer_date.desc(), Transfer.created_at.desc())
        .limit(limit)
    ).all()
    return [_to_out(db, t) for t in rows]


@router.post("", response_model=TransferOut, status_code=201)
def create_transfer(
    data: TransferIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _validate_accounts(db, user, data.from_account_id, data.to_account_id)
    transfer = Transfer(user_id=user.id, **data.model_dump())
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return _to_out(db, transfer)


@router.put("/{transfer_id}", response_model=TransferOut)
def update_transfer(
    transfer_id: uuid.UUID,
    data: TransferUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfer = db.scalar(
        select(Transfer).where(Transfer.id == transfer_id, Transfer.user_id == user.id)
    )
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    updates = data.model_dump(exclude_unset=True)
    from_id = updates.get("from_account_id", transfer.from_account_id)
    to_id = updates.get("to_account_id", transfer.to_account_id)
    _validate_accounts(db, user, from_id, to_id)
    for key, value in updates.items():
        setattr(transfer, key, value)
    db.commit()
    db.refresh(transfer)
    return _to_out(db, transfer)


@router.delete("/{transfer_id}", status_code=200)
def delete_transfer(
    transfer_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transfer = db.scalar(
        select(Transfer).where(Transfer.id == transfer_id, Transfer.user_id == user.id)
    )
    if transfer is None:
        raise HTTPException(status_code=404, detail="Transfer not found")
    db.delete(transfer)
    db.commit()
    return {"detail": "Transfer deleted"}
