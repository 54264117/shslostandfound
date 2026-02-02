from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import date
from PIL import Image


class FoundItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=140)])
    description = TextAreaField('Description',
                                validators=[DataRequired(), Length(max=1000)])
    date_found = DateField('Date Found', render_kw={"max": date.today()},
                           validators=[DataRequired()])
    location_found = StringField('Location Found',
                                 validators=[DataRequired(), Length(max=140)])
    image_file = FileField('Image', validators=[FileRequired()])
    submit = SubmitField('Submit')

    def validate_date_found(self, date_found):
        if date_found.data > date.today():
            raise ValidationError('Date found cannot be in the future.')

    def validate_image_file(self, image_file):
        try:
            img = Image.open(image_file.data)
            img.verify()
        except Exception:
            raise ValidationError('Invalid image file.')
