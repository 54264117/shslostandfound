from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, UserStatus
from app.auth.email import send_password_reset_email, send_validation_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit() and form.password.data:
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        bad_login = (
            user is None
            or not user.check_password(form.password.data)
            or user.status != UserStatus.ACTIVE
        )
        if bad_login:
            if user and user.status == UserStatus.INACTIVE:
                flash('Your account has been deactivated. Please contact an administrator')
            else:
                flash('Invalid email address or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit() and form.email.data and form.password.data:
        user = User()
        user.email = form.email.data
        user.name = form.name.data
        user.set_password(form.password.data)
        user.status = UserStatus.PENDING
        db.session.add(user)
        db.session.commit()
        send_validation_email(user)
        flash('Check your email for the instructions to complete your registration')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register',
                           form=form)


@bp.route('/register/<token>', methods=['GET', 'POST'])
def validate_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_email_validation_token(token)
    if not user:
        flash('Invalid or expired token')
        return redirect(url_for('main.index'))
    if user.status != UserStatus.PENDING:
        return redirect(url_for('main.index'))
    user.status = UserStatus.ACTIVE
    db.session.commit()
    flash('You have successfully completed registration. You can now log in')
    return redirect(url_for('auth.login'))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user and user.status == UserStatus.INACTIVE:
            flash('Your account has been deactivated. Please contact an administrator')
        else:
            if user and user.status == UserStatus.ACTIVE:
                send_password_reset_email(user)
            flash(
                'Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_email_validation_token(token)
    if not user:
        flash('Invalid or expired token')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit() and form.password.data:
        password = form.password.data
        user.set_password(password)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
