from datetime import datetime, timezone
from flask import render_template
from flask_login import current_user, login_required
import sqlalchemy as sa
from app import db
from app.main import bp
from app.models import User


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    return render_template('index.html', title='Home')
