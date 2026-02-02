from flask import current_app
from flask_wtf import FlaskForm
from datetime import datetime, timedelta, timezone
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User, UserStatus


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            if user.status != UserStatus.PENDING:
                raise ValidationError('This email address has already been registered')
            expiration_time = user.last_seen + \
                timedelta(seconds=current_app.config['EMAIL_TOKEN_EXPIRATION'])
            if datetime.now(timezone.utc).replace(tzinfo=None) > expiration_time:
                db.session.delete(user)
                db.session.commit()
            else:
                raise ValidationError(
                    'This email address has already been registered but not yet validated. '
                    'Please check your email for the validation link.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Request Password Reset')
