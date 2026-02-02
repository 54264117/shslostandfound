from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_email_validation_token()
    send_email('[SMS Lost and Found] Reset Your Password',
               sender=current_app.config['MAIL_FROMADDRESS'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_validation_email(user):
    token = user.get_email_validation_token()
    send_email('[SMS Lost and Found] Validate Your Email Address',
               sender=current_app.config['MAIL_FROMADDRESS'],
               recipients=[user.email],
               text_body=render_template('email/email_validation.txt',
                                         user=user, token=token),
               html_body=render_template('email/email_validation.html',
                                         user=user, token=token))
