from sqlalchemy.orm import Session

from .models import Category, User

DEFAULT_INCOME = ["Salary", "Bonus", "Freelance", "Investment", "Other"]
DEFAULT_EXPENSE = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other",
]


def seed_default_categories(db: Session, user: User) -> None:
    for name in DEFAULT_INCOME:
        db.add(Category(user_id=user.id, name=name, type="income"))
    for name in DEFAULT_EXPENSE:
        db.add(Category(user_id=user.id, name=name, type="expense"))
    db.commit()
