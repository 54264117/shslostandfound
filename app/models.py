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

    found_items: so.WriteOnlyMapped['FoundItem'] = so.relationship(
        back_populates='reporter', cascade='all, delete-orphan')

    __table_args__ = (
        sa.CheckConstraint(
            "status IN ('PENDING', 'ACTIVE', 'INACTIVE')",
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

    def get_email_validation_token(
            self, expires_in: int) -> str:
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


class FoundItemStatus(Enum):
    REVIEW = 'review'
    PUBLISHED = 'published'
    CLOSED = 'closed'


class FoundItem(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    date_found: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    location_found: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    image_filename: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    user_id: so.Mapped[int] = so.mapped_column(
        sa.Integer, sa.ForeignKey('user.id'))
    status: so.Mapped[FoundItemStatus] = so.mapped_column(
        sa.Enum(FoundItemStatus, native_enum=False, validate_strings=True),
        default=FoundItemStatus.REVIEW)

    reporter: so.Mapped[User] = so.relationship(back_populates='found_items')

    __table_args__ = (
        sa.CheckConstraint(
            "status IN ('REVIEW', 'PUBLISHED', 'CLOSED')",
            name='check_found_item_status'),
    )

    def __repr__(self) -> str:
        return f'<FoundItem {self.title} by User {self.user_id}>'
