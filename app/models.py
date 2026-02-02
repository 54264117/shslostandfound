from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from enum import Enum
from time import time
from app import db, login


class UserStatus(Enum):
    PENDING = 'pending'
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(120))
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    last_seen: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    status: so.Mapped[UserStatus] = so.mapped_column(
        sa.Enum(UserStatus, native_enum=False, validate_strings=True),
        default=UserStatus.PENDING)

    __table_args__ = (
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'inactive')",
            name='check_user_status'),
    )

    def __repr__(self) -> str:
        return f'<User {self.email}>'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def get_email_validation_token(self, expires_in: int = 600) -> str:
        return jwt.encode(
            {'validate_email': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_email_validation_token(token: str) -> Optional['User']:
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['validate_email']
        except Exception:
            return None
        return db.session.get(User, id)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
