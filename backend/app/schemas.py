import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

AccountType = Literal["cash", "bank", "e-wallet", "other"]
TxType = Literal["income", "expense"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORMModel):
    id: uuid.UUID
    email: EmailStr
    created_at: datetime


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None


# ---------- Accounts ----------


class AccountIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: AccountType = "cash"
    initial_balance: float = 0


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    type: AccountType | None = None
    initial_balance: float | None = None
    is_active: bool | None = None


class AccountOut(ORMModel):
    id: uuid.UUID
    name: str
    type: str
    initial_balance: float
    is_active: bool
    created_at: datetime
    balance: float = 0


# ---------- Categories ----------


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: TxType


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    type: TxType | None = None
    is_active: bool | None = None


class CategoryOut(ORMModel):
    id: uuid.UUID
    name: str
    type: str
    is_active: bool


# ---------- Transactions ----------


class TransactionIn(BaseModel):
    type: TxType
    amount: float = Field(gt=0)
    category_id: uuid.UUID
    account_id: uuid.UUID
    description: str = Field(default="", max_length=255)
    transaction_date: date


class TransactionUpdate(BaseModel):
    type: TxType | None = None
    amount: float | None = Field(default=None, gt=0)
    category_id: uuid.UUID | None = None
    account_id: uuid.UUID | None = None
    description: str | None = Field(default=None, max_length=255)
    transaction_date: date | None = None


class TransactionOut(ORMModel):
    id: uuid.UUID
    type: str
    amount: float
    description: str
    transaction_date: date
    created_at: datetime
    category_id: uuid.UUID
    account_id: uuid.UUID
    category_name: str = ""
    account_name: str = ""


# ---------- Transfers ----------


class TransferIn(BaseModel):
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    amount: float = Field(gt=0)
    description: str = Field(default="", max_length=255)
    transfer_date: date


class TransferUpdate(BaseModel):
    from_account_id: uuid.UUID | None = None
    to_account_id: uuid.UUID | None = None
    amount: float | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=255)
    transfer_date: date | None = None


class TransferOut(ORMModel):
    id: uuid.UUID
    amount: float
    description: str
    transfer_date: date
    created_at: datetime
    from_account_id: uuid.UUID
    to_account_id: uuid.UUID
    from_account_name: str = ""
    to_account_name: str = ""


# ---------- Budgets ----------


class BudgetIn(BaseModel):
    category_id: uuid.UUID
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
    amount: float = Field(ge=0)


class BudgetUpdate(BaseModel):
    amount: float | None = Field(default=None, ge=0)
    category_id: uuid.UUID | None = None
    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = Field(default=None, ge=2000, le=2100)


class BudgetOut(ORMModel):
    id: uuid.UUID
    category_id: uuid.UUID
    category_name: str = ""
    month: int
    year: int
    amount: float
    spent: float = 0
    remaining: float = 0
    usage_percent: float = 0


# ---------- Dashboard / Reports ----------


class Point(BaseModel):
    label: str
    income: float = 0
    expense: float = 0


class CategoryShare(BaseModel):
    category_id: uuid.UUID
    category_name: str
    amount: float
    percent: float


class Period(BaseModel):
    start: date
    end: date


class DashboardOut(BaseModel):
    period: Period
    balance: float
    income: float
    expenses: float
    savings: float
    income_vs_expense: list[Point]
    expense_by_category: list[CategoryShare]
    recent_transactions: list[TransactionOut]
    budgets: list[BudgetOut]


class SummaryOut(BaseModel):
    year: int
    month: int
    income: float
    expenses: float
    net: float


class TrendPoint(BaseModel):
    year: int
    month: int
    income: float
    expense: float
