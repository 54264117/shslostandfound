from flask import render_template
from app.main import bp


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    """Render the main index page."""
    return render_template('index.html', title='Home')
