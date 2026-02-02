from datetime import datetime, timezone, time
from flask import render_template, flash, redirect, request, url_for, current_app, \
    send_from_directory
from flask_login import current_user, login_required
from typing import cast
from pathlib import Path
from app import db
from app.main import bp
from app.models import User, FoundItem, FoundItemStatus
from app.main.image_files import upload_file
from app.main.forms import FoundItemForm


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    found_items = db.paginate(
        db.select(FoundItem)
        .order_by(FoundItem.date_found.desc()),
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('main.index', page=found_items.next_num) \
        if found_items.has_next else None
    prev_url = url_for('main.index', page=found_items.prev_num) \
        if found_items.has_prev else None
    return render_template('index.html', title='Home', found_items=found_items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/found_item', methods=['GET', 'POST'])
@login_required
def add_found_item():
    form = FoundItemForm()
    if form.validate_on_submit():
        found_item = FoundItem()
        found_item.title = form.title.data if form.title.data else ''
        found_item.description = form.description.data
        found_item.date_found = datetime.combine(form.date_found.data, time()) \
            if form.date_found.data else None
        found_item.location_found = form.location_found.data
        found_item.reporter = cast(User, current_user)
        found_item.status = FoundItemStatus.REVIEW
        db.session.add(found_item)
        db.session.flush()
        image_filename = upload_file(request.files['image_file'], str(found_item.id))
        if image_filename:
            found_item.image_filename = str(image_filename)
        db.session.commit()
        flash('Found item submitted successfully!')
        return redirect(url_for('main.index'))
    return render_template('edit_found_item.html', title='Report Found Item', form=form)


@bp.route('/found_item/<int:id>', methods=['GET'])
def found_item(id):
    found_item = FoundItem.query.get_or_404(id)
    return render_template('found_item.html', title='Found Item Details',
                           found_item=found_item)


@bp.route('/found_item/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_found_item(id):
    found_item = FoundItem.query.get_or_404(id)
    if found_item.reporter != current_user:
        flash('You are not authorized to update this found item.')
        return redirect(url_for('main.found_item', id=id))
    form = FoundItemForm()
    if form.validate_on_submit():
        found_item = FoundItem()
        found_item.title = form.title.data if form.title.data else ''
        found_item.description = form.description.data
        found_item.date_found = datetime.combine(form.date_found.data, time()) \
            if form.date_found.data else None
        found_item.location_found = form.location_found.data
        found_item.reporter = cast(User, current_user)
        found_item.status = FoundItemStatus.REVIEW
        image_filename = upload_file(request.files['image_file'], str(found_item.id))
        if image_filename:
            found_item.image_filename = image_filename
        db.session.commit()
        flash('Found item updated successfully!')
        return redirect(url_for('main.found_item', id=id))
    elif request.method == 'GET':
        form.title.data = found_item.title
        form.description.data = found_item.description
        form.date_found.data = found_item.date_found.date() \
            if found_item.date_found else None
        form.location_found.data = found_item.location_found
    return render_template('edit_found_item.html', title='Update Found Item', form=form)


@bp.route('/images/<id>')
def images(id):
    if current_app.static_folder is None:
        return "Static folder not configured", 404
    filepath = Path(current_app.static_folder,
                    current_app.config['IMAGE_FOLDER'],
                    id)
    file = [f for f in filepath.iterdir() if f.is_file()][0]
    return send_from_directory(filepath, file.name)


@bp.route('/images/<id>/thumb_<size>')
def image_thumbnails(id, size):
    if current_app.static_folder is None:
        return "Static folder not configured", 404
    filepath = Path(current_app.static_folder,
                    current_app.config['IMAGE_FOLDER'],
                    id,
                    f'thumb_{size}')
    return send_from_directory(filepath, 'thumb.jpg')
